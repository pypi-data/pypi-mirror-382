import logging
import subprocess
import time
import os
import shutil
from tinydb import TinyDB, Query
import json
import paramiko
import base64
import re
import pickle
import base64
import uuid
from kubernetes import client
from kubernetes.client.rest import ApiException
from pprint import pformat
import fnmatch


RBD_REPO_TYPES = ["qemu", "lxc", "k8s"]

logger = logging.getLogger("bdd")

os.environ["BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK"] = "yes" # we need this to stop borg cli from manual prompting
os.environ["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = "yes"

ENV = os.getenv("ENV", "TESTING")

# constants
BACKUP_DIR = os.getenv("BACKUP_DIR", "/tmp/pve-cloud-test-backup")

IMAGE_META_DB_PATH = f"{BACKUP_DIR}/image-meta-db.json"

STACK_META_DB_PATH = f"{BACKUP_DIR}/stack-meta-db.json"


def group_image_metas(metas, type_keys, group_key, stack_filter=None):
  metas_grouped = {}

  # group metas by vmid
  for meta in metas:
    logger.debug(f"meta {meta}")

    if not meta["type"] in type_keys:
      continue # skip non fitting

    if stack_filter and meta["stack"] != stack_filter:
      continue # skip filtered out stack

    if meta[group_key] not in metas_grouped:
      metas_grouped[meta[group_key]] = []

    metas_grouped[meta[group_key]].append(meta)

  return metas_grouped


# these functions are necessary to convert python k8s naming to camel case
def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# this one too
def convert_keys_to_camel_case(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = to_camel_case(key)
            new_dict[new_key] = convert_keys_to_camel_case(value)
        return new_dict
    elif isinstance(obj, list):
        return [convert_keys_to_camel_case(item) for item in obj]
    else:
        return obj


def restore_pvcs(metas_grouped, namespace_secret_dict, args, api_client):
  core_v1 = client.CoreV1Api(api_client=api_client)
  apps_v1 = client.AppsV1Api(api_client=api_client)
  storage_v1 = client.StorageV1Api(api_client=api_client)

  # get ceph storage classes
  ceph_storage_classes = {sc.metadata.name: sc for sc in storage_v1.list_storage_class().items if sc.provisioner == 'rbd.csi.ceph.com'}

  # load existing ceph pools and fetch their ids, needed for later pv restoring
  ls_call = subprocess.run(["ceph", "osd", "pool", "ls", "detail", "-f", "json"], check=True, text=True, capture_output=True)
  pool_details = json.loads(ls_call.stdout)  # load existing ceph pools and fetch their ids, needed for later pv restoring

  pool_name_id = {}
  for pool_detail in pool_details:
    pool_name_id[pool_detail["pool_name"]] = pool_detail["pool_id"]

  # get the cluster id from ceph ns
  ceph_csi_config = core_v1.read_namespaced_config_map(name="ceph-csi-config", namespace="ceph-csi")

  if not ceph_csi_config:
    raise Exception("Could not find ceph-csi-config config map in ceph-csi namespace")

  ceph_cluster_id = json.loads(ceph_csi_config.data.get("config.json"))[0]["clusterID"]

  filter_namespaces = [] if args.namespaces == "" else args.namespaces.split(",")

  for namespace, metas_group in metas_grouped.items():
    if filter_namespaces and namespace not in filter_namespaces:
      continue # skip filtered out namespaces

    logger.info(f"trying to restore volumes of {namespace}")

    auto_scale_replicas = {}
    if args.auto_scale:
      # auto downscale deployments and statefulsets of namespace
      deployments = apps_v1.list_namespaced_deployment(namespace)
      for d in deployments.items:
        name = d.metadata.name
        auto_scale_replicas[f"dp-{name}"] = d.spec.replicas # save original replicas for upscale later
        logger.info(f"Scaling Deployment '{name}' to 0 replicas...")
        apps_v1.patch_namespaced_deployment_scale(
          name=name,
          namespace=namespace,
          body={"spec": {"replicas": 0}}
        )

      statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
      for s in statefulsets.items:
        name = s.metadata.name
        auto_scale_replicas[f"ss-{name}"] = s.spec.replicas
        logger.info(f"Scaling StatefulSet '{name}' to 0 replicas...")
        apps_v1.patch_namespaced_stateful_set_scale(
          name=name,
          namespace=namespace,
          body={"spec": {"replicas": 0}}
        )

      # wait for termination
      while True:
        pods = core_v1.list_namespaced_pod(namespace)
        remaining = [
          pod.metadata.name
          for pod in pods.items
          if pod.status.phase in ["Running", "Pending", "Terminating"]
        ]
        if not remaining:
          logger.info("All pods have terminated.")
          break
        logger.info(f"Still active pods: {remaining}")
        time.sleep(5)


    # check if namespace has pods => throw exeption and tell user to scale down any
    pods = core_v1.list_namespaced_pod(namespace=namespace)

    existing_pvcs = set(pvc.metadata.name for pvc in core_v1.list_namespaced_persistent_volume_claim(namespace).items)
    logger.debug(f"existing pvcs {existing_pvcs}")

    # if any pending / running pods exist fail
    pod_phases = [pod for pod in pods.items if pod.status.phase != "Succeeded"]
    if pod_phases:
      raise Exception(f"found pods in {namespace} - {pod_phases} - scale down all and force delete!")

    # process secret overwrites
    if args.secret_pattern:
      
      namespace_secrets = {secret["metadata"]["name"]: secret for secret in namespace_secret_dict[namespace]}

      for secret_pattern in args.secret_pattern:
        if secret_pattern.split("/")[0] == namespace:
          # arg that is meant for this namespace restore
          pattern = secret_pattern.split("/")[1]

          for secret in namespace_secrets:
            if fnmatch.fnmatch(secret, pattern):
              logger.info(f"overwrite pattern matched {pattern}, trying to patch {secret}")
              try:
                core_v1.patch_namespaced_secret(name=secret, namespace=namespace, body={"data": namespace_secrets[secret]["data"]})
              except ApiException as e:
                # if it doesnt exist we simply create it
                if e.status == 404:
                  core_v1.create_namespaced_secret(
                      namespace=namespace,
                      body={"metadata": {"name": secret}, "data": namespace_secrets[secret]["data"]}
                  )
                  logger.info(f"secret {secret} did not exist, created it instead!")
                else:
                    raise

    if args.auto_delete:
      pvcs = core_v1.list_namespaced_persistent_volume_claim(namespace)
      for pvc in pvcs.items:
        name = pvc.metadata.name
        logger.info(f"Deleting PVC: {name}")
        core_v1.delete_namespaced_persistent_volume_claim(
          name=name,
          namespace=namespace,
          body=client.V1DeleteOptions()
        )
      
      while True:
        leftover = core_v1.list_namespaced_persistent_volume_claim(namespace).items
        if not leftover:
          logger.info("All PVCs have been deleted.")
          break
        logger.info(f"Still waiting on: {[p.metadata.name for p in leftover]}")
        time.sleep(5)

      # there are no more existing pvcs
      existing_pvcs = set()


    # extract raw rbd images, import and recreate pvc if necessary
    for meta in metas_group:
      logger.debug(f"restoring {meta}") 

      image_name = meta["image_name"]

      type = meta["type"]

      pvc_dict = pickle.loads(base64.b64decode(meta["pvc_dict_b64"]))
      logger.debug(f"pvc_dict:\n{pvc_dict}")
      pv_dict = pickle.loads(base64.b64decode(meta["pv_dict_b64"]))
      logger.debug(f"pv_dict:\n{pv_dict}")

      # extract from borg archive
      if args.backup_path:
        # we can use the absolute path provided
        full_borg_archive = f"{args.backup_path}borg-{type}::{image_name}_{args.timestamp}"
      else:
        full_borg_archive = f"{os.getcwd()}/borg-{type}::{image_name}_{args.timestamp}"
      
      # import the image into ceph
      # move to new pool if mapping is defined
      pool = meta["pool"]
      storage_class = pvc_dict["spec"]["storage_class_name"]

      if args.pool_sc_mapping:
        for pool_mapping in args.pool_sc_mapping:
          old_pool = pool_mapping.split(":")[0]
          new_pool_sc = pool_mapping.split(":")[1]
          if pool == old_pool:
            pool = new_pool_sc.split("/")[0]
            storage_class = new_pool_sc.split("/")[1]
            logger.debug(f"new mapping specified old pool {old_pool}, new pool {pool}, new sc {storage_class}")
            break

      new_csi_image_name = f"csi-vol-{uuid.uuid4()}"

      logger.info(f"extracting borg archive {full_borg_archive} into rbd import {pool}/{new_csi_image_name}")

      with subprocess.Popen(["borg", "extract", "--sparse", "--stdout", full_borg_archive], stdout=subprocess.PIPE) as proc:
        subprocess.run(["rbd", "import", "-", f"{pool}/{new_csi_image_name}"], check=True, stdin=proc.stdout)

      # restore from pickled pvc dicts
      new_pv_name = f"pvc-{uuid.uuid4()}"

      logger.debug(f"restoring pv with new pv name {new_pv_name} and csi image name {new_csi_image_name}")
    
      # create the new pvc based on the old - remove dynamic fields of old:
      if pvc_dict['metadata']['name'] in existing_pvcs:
        pvc_name = pvc_dict['metadata']['name']
        pvc_dict['metadata']['name'] = f"test-restore-{pvc_name}"
        logger.info(f"pvc {pvc_name} exists, creating it with test-restore- prefix")

      # clean the old pvc object so it can be submitted freshly
      pvc_dict['metadata']['annotations'].pop('pv.kubernetes.io/bind-completed', None)
      pvc_dict['metadata']['annotations'].pop('pv.kubernetes.io/bound-by-controller', None)
      pvc_dict['metadata'].pop('finalizers', None)
      pvc_dict['metadata'].pop('managed_fields', None)
      pvc_dict['metadata'].pop('resource_version', None)
      pvc_dict['metadata'].pop('uid', None)
      pvc_dict['metadata'].pop('creation_timestamp', None)
      pvc_dict.pop('status', None)
      pvc_dict.pop('kind', None)
      pvc_dict.pop('api_version', None)

      # set new values
      pvc_dict['spec']['storage_class_name'] = storage_class

      # we can give it a customized pv name so we know migrated ones - will still behave like a normal created pv
      pvc_dict['spec']['volume_name'] = new_pv_name

      # creation call 
      logger.debug(f"creating new pvc:\n{pformat(pvc_dict)}")
      core_v1.create_namespaced_persistent_volume_claim(namespace=namespace, body=client.V1PersistentVolumeClaim(**convert_keys_to_camel_case(pvc_dict)))

      # cleanup the old pv aswell for recreation
      pv_dict.pop('api_version', None)
      pv_dict.pop('kind', None)
      pv_dict['metadata'].pop('creation_timestamp', None)
      pv_dict['metadata'].pop('finalizers', None)
      pv_dict['metadata'].pop('managed_fields', None)
      pv_dict['metadata'].pop('resource_version', None)
      pv_dict['metadata']['annotations'].pop('volume.kubernetes.io/provisioner-deletion-secret-name', None)
      pv_dict['metadata']['annotations'].pop('volume.kubernetes.io/provisioner-deletion-secret-namespace', None)
      pv_dict.pop('status', None)
      pv_dict['spec'].pop('claim_ref', None)
      pv_dict['spec'].pop('volume_attributes_class_name', None)
      pv_dict['spec'].pop('scale_io', None)
      pv_dict['spec']['csi'].pop('volume_handle', None)
      pv_dict['spec']['csi']['volume_attributes'].pop('imageName', None)
      pv_dict['spec']['csi']['volume_attributes'].pop('journalPool', None)
      pv_dict['spec']['csi']['volume_attributes'].pop('pool', None)

      # set values

      # get the storage class and set secrets from it
      ceph_storage_class = ceph_storage_classes[storage_class]
      pv_dict['metadata']['annotations']['volume.kubernetes.io/provisioner-deletion-secret-name'] = ceph_storage_class.parameters['csi.storage.k8s.io/provisioner-secret-name']
      pv_dict['metadata']['annotations']['volume.kubernetes.io/provisioner-deletion-secret-namespace'] = ceph_storage_class.parameters['csi.storage.k8s.io/provisioner-secret-namespace']
      
      pv_dict['spec']['csi']['node_stage_secret_ref']['name'] = ceph_storage_class.parameters['csi.storage.k8s.io/node-stage-secret-name']
      pv_dict['spec']['csi']['node_stage_secret_ref']['namespace'] = ceph_storage_class.parameters['csi.storage.k8s.io/node-stage-secret-namespace']

      pv_dict['spec']['csi']['controller_expand_secret_ref']['name'] = ceph_storage_class.parameters['csi.storage.k8s.io/controller-expand-secret-name']
      pv_dict['spec']['csi']['controller_expand_secret_ref']['namespace'] = ceph_storage_class.parameters['csi.storage.k8s.io/controller-expand-secret-namespace']

      pv_dict['spec']['csi']['volume_attributes']['clusterID'] = ceph_cluster_id

      # reconstruction of volume handle that the ceph csi provisioner understands
      pool_id = format(pool_name_id[pool], '016x')
      trimmed_new_csi_image_name = new_csi_image_name.removeprefix('csi-vol-')
      pv_dict['spec']['csi']['volumeHandle'] = f"0001-0024-{ceph_cluster_id}-{pool_id}-{trimmed_new_csi_image_name}"

      pv_dict['spec']['csi']['volume_attributes']['imageName'] = new_csi_image_name
      pv_dict['spec']['csi']['volume_attributes']['journalPool'] = pool
      pv_dict['spec']['csi']['volume_attributes']['pool'] = pool

      pv_dict['spec']['storage_class_name'] = storage_class

      pv_dict['metadata']['name'] = new_pv_name

      # creation call
      logger.debug(f"creating new pv:\n{pformat(pv_dict)}")
      core_v1.create_persistent_volume(body=client.V1PersistentVolume(**convert_keys_to_camel_case(pv_dict)))

    # scale back up again
    if args.auto_scale:
      # auto downscale deployments and statefulsets of namespace
      deployments = apps_v1.list_namespaced_deployment(namespace)
      for d in deployments.items:
        name = d.metadata.name
        logger.info(f"Scaling Deployment '{name}' back up...")
        apps_v1.patch_namespaced_deployment_scale(
          name=name,
          namespace=namespace,
          body={"spec": {"replicas": auto_scale_replicas[f"dp-{name}"]}}
        )

      statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
      for s in statefulsets.items:
        name = s.metadata.name
        logger.info(f"Scaling StatefulSet '{name}' back up...")
        apps_v1.patch_namespaced_stateful_set_scale(
          name=name,
          namespace=namespace,
          body={"spec": {"replicas": auto_scale_replicas[f"ss-{name}"]}}
        )

    logger.info(f"restore of namespace {namespace} complete, you can now scale up your deployments again")
    

def restore_images(image_metas, stack_metas, args, proxmox):
  stack_name_filter = [] if args.stack_names == "" else args.stack_names.split(",")

  # init paramiko for restoring pve vm conf files, either remote pve host or loopback connection
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  if args.proxmox_host and args.proxmox_private_key:
    # remove connection
    ssh.connect(hostname=args.proxmox_host, username="root", pkey=paramiko.RSAKey.from_private_key_file(args.proxmox_private_key))
  else:
    # localhost connection
    ssh.connect(hostname="localhost", username="root")

  # replace pools
  pool_update_map = {}
  if args.pool_mapping:
    for pool_mapping in args.pool_mapping:
      old_pool = pool_mapping.split(":")[0]
      new_pool = pool_mapping.split(":")[1]

      if old_pool in pool_update_map:
        raise Exception(f"pool {old_pool} defined in more than one mapping!")
      
      pool_update_map[old_pool] = new_pool

  for vmid, metas_group in image_metas.items():
    stack_meta = stack_metas[vmid]

    if stack_meta is None:
      raise Exception(f"stack meta for vmid {vmid} is none!")

    if stack_name_filter and stack_meta["stack"] not in stack_name_filter:
      continue # skip filtered out namespaces

    # use paramiko to restore the vm conf
    vm_conf = base64.b64decode(stack_meta["vm_conf"]).decode("utf-8")

    # get id for import 
    next_id = proxmox.cluster.nextid.get()

    # update disks in conf
    for meta in metas_group:
      conf_key = meta["conf_key"]
      pool = meta["pool"]

      # replace the vm disk id
      search_regex = rf"^({conf_key}:.+?)\d+"
      replace_regex = rf"\g<1>{next_id}"

      logger.debug(f"search regex: {search_regex}, replace regex {replace_regex}, vm_conf:\n{vm_conf}")
      vm_conf = re.sub(search_regex, replace_regex, vm_conf, flags=re.MULTILINE)

      logger.debug(f"updated vm conf:\n{vm_conf}")

      # check if the pool also needs to be replaced
      if pool in pool_update_map:
        update_pool = pool_update_map[pool]
        vm_conf = re.sub(rf"^({conf_key}:\s*)[^:]+", rf"\g<1>{update_pool}", vm_conf, flags=re.MULTILINE)


    # for writing the file
    sftp = ssh.open_sftp()

    if stack_meta["type"] == "qemu":
      with sftp.file(f"/etc/pve/qemu-server/{next_id}.conf", "w") as file:
        file.write(vm_conf)
    elif stack_meta["type"] == "lxc":
      with sftp.file(f"/etc/pve/lxc/{next_id}.conf", "w") as file:
        file.write(vm_conf)

    sftp.close()


    # restore all the images
    for meta in metas_group:
      logger.debug(f"meta {meta}")

      meta_type = meta["type"]
      image_name = meta["image_name"]
      pool = meta["pool"]

      new_image_name = re.sub(r"^(vm-)\d+", rf"\g<1>{next_id}", image_name)

      if pool in pool_update_map:
        pool = pool_update_map[pool]

      # extract the borg archive - borg extract always extracts to its working dir
      if args.backup_path:
        # we can use the absolute path provided
        full_borg_archive = f"{args.backup_path}borg-{meta_type}::{image_name}_{args.timestamp}"
      else:
        full_borg_archive = f"{os.getcwd()}/borg-{meta_type}::{image_name}_{args.timestamp}"
      
      logger.info(f"extracting borg archive {full_borg_archive} into rbd import {pool}/{new_image_name}")
      
      with subprocess.Popen(["borg", "extract", "--sparse", "--stdout", full_borg_archive], stdout=subprocess.PIPE) as proc:
        subprocess.run(["rbd", "import", "-", f"{pool}/{new_image_name}"], check=True, stdin=proc.stdout)
   

def get_stack_metas(args, timestamp, meta_types, unique_group_key):
  stack_meta_db = TinyDB(f"{args.backup_path}stack-meta-db.json")
  Meta = Query()

  stack_metas = stack_meta_db.search((Meta.timestamp == timestamp) & (Meta.type.one_of(meta_types)))

  keyed_stack_metas = {}

  for meta in stack_metas:
    if meta[unique_group_key] in keyed_stack_metas:
      raise Exception(f"duplicate key for meta {unique_group_key} {meta}")
    
    keyed_stack_metas[meta[unique_group_key]] = meta
  
  return keyed_stack_metas


def get_image_metas(args, timestamp_filter = None):
  image_meta_db = TinyDB(f"{args.backup_path}image-meta-db.json")

  archives = []

  for borg_repo_type in RBD_REPO_TYPES:
    list_result = subprocess.run(["borg", "list", f"{args.backup_path}/borg-{borg_repo_type}", "--json"], capture_output=True)
    archives.extend(json.loads(list_result.stdout)["archives"])

  timestamp_archives = {}
  for archive in archives:
    image = archive["archive"].split("_", 1)[0]
    timestamp = archive["archive"].split("_", 1)[1]

    if timestamp_filter is not None and timestamp_filter != timestamp:
      continue # skip filtered

    if timestamp not in timestamp_archives:
      timestamp_archives[timestamp] = []  

    Meta = Query()
    image_meta = image_meta_db.get((Meta.image_name == image) & (Meta.timestamp == timestamp))

    if image_meta is None:
      logger.error(f"None meta found {timestamp}, image_name {image}, archive {archive}")
      del timestamp_archives[timestamp]
      continue

    timestamp_archives[timestamp].append(image_meta)

  return timestamp_archives


def copy_backup_generic():
  source_dir = '/opt/bdd'
  for file in os.listdir(source_dir):
    if not file.startswith("."):
      full_source_path = os.path.join(source_dir, file)
      full_dest_path = os.path.join(BACKUP_DIR, file)

      if os.path.isfile(full_source_path):
        shutil.copy2(full_source_path, full_dest_path)


# try to mount any of the specified disks
def mount_disk():
  for disk_uuid in os.getenv("ENV_MODE").split(":")[1].split(","):
    try:
      subprocess.run(["mount", f"UUID={disk_uuid}", BACKUP_DIR], check=True, text=True, capture_output=True)
      break
    except subprocess.CalledProcessError as e:
      logger.info(f"Error mounting disk: {e.stdout + e.stderr}")

