import paramiko
import base64
import logging
import pickle
import subprocess
import json
import re
import yaml
import os
from pprint import pformat
from kubernetes import client
from kubernetes.config.kube_config import KubeConfigLoader
import net
import asyncio


logger = logging.getLogger("fetcher")

VM_DISK_PATTERNS = [r"scsi\d+", 
                    # special win vm keys
                    r"tpmstate\d+", r"efidisk\d+"]

LXC_DISK_PATTERNS = ["rootfs", r"mp\d+"]


# sshs into master k8s vms and fetches the there lying kubeconfigs
def get_kubernetes_clients(backup_config, proxmox, pkey):
  logger.info(f"getting k8s clients")

  k8s_stacks = backup_config["k8s_stacks"].keys()

  k8s_masters = {}
  # collect one master node per stack
  for node in proxmox.nodes.get():
    node_name = node["node"]

    if node["status"] == "offline":
      logger.info(f"skipping offline node {node_name}")
      continue
    
    for qemu in proxmox.nodes(node_name).qemu.get():
      if "tags" in qemu and any(tag in k8s_stacks for tag in qemu["tags"].split(";")) and 'master' in qemu["tags"].split(";"):
        # found a master
        logger.debug(f"found master {pformat(qemu)}")
        
        # find the stack tag
        stack_tag = None
        for tag in qemu["tags"].split(";"):
          for k8s_stack_tag in k8s_stacks:
            if tag == k8s_stack_tag:
              stack_tag = tag
        
        if stack_tag is None:
          raise Exception(f"something went terribly wrong, stack tag should never be none - qemu:\n{pformat(qemu)}")
        
        if stack_tag in k8s_masters:
          continue # we already saved a master for this stack

        k8s_masters[stack_tag] = {"pve_host": node_name, "vmid": qemu["vmid"]}

  logger.debug(f"collected masters:\n{pformat(k8s_masters)}")

  k8s_kubeconfigs = {}

  # now we can connect to each master via ssh and fetch the kubeconfig
  for k8s_stack, master in k8s_masters.items():
    ifaces = proxmox.nodes(master["pve_host"]).qemu(master["vmid"]).agent("network-get-interfaces").get()
    logger.debug(f"k8s stack master {k8s_stack} interfaces {pformat(ifaces)}")

    master_ipv4 = None

    for iface in ifaces["result"]:
      if iface["name"] == "lo":
        continue # skip the first loopback device

      # after that comes the primary interface
      for ip_address in iface["ip-addresses"]:
        if ip_address["ip-address-type"] == "ipv4":
          master_ipv4 = ip_address["ip-address"]
          break
      
      if master_ipv4 is None:
        raise Exception(f"could not get ipv4 for master {master} stack {k8s_stack}")

      break

    # now we can use that address to connect via ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    user = os.getenv("QEMU_ADMIN_USER", "admin")

    logger.info(f"connecting to master {master_ipv4} - {user}")
    ssh.connect(master_ipv4, username=user, pkey=pkey)

    # since we need root we cant use sftp and root via ssh is disabled
    _, stdout, _ = ssh.exec_command("sudo cat /etc/kubernetes/admin.conf")

    config = stdout.read().decode('utf-8')

    logger.debug(f"ssh sudo cat kubeconfig:\n{config}")

    k8s_kubeconfigs[k8s_stack] = { "raw_kubeconfig": config, "master_ip": master_ipv4 }
  
  return k8s_kubeconfigs


def get_vm_configs(metas, pkey):
  pve_vm_map = {}

  # group by host
  for meta in metas:
    host_ip = meta["host_ip"]
    
    if host_ip not in pve_vm_map:
      pve_vm_map[host_ip] = []

    pve_vm_map[host_ip].append(meta)

  vm_conf_map = {}

  for host_ip, metas in pve_vm_map.items():

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  
    ssh.connect(host_ip, username="root", pkey=pkey)
  
    for meta in metas:
      sftp = ssh.open_sftp()

      vmid = meta["vmid"]

      if meta["type"] == "lxc":
        config_path = f"/etc/pve/lxc/{vmid}.conf"
      elif meta["type"] == "qemu":
        config_path = f"/etc/pve/qemu-server/{vmid}.conf"
      
      with sftp.open(config_path, "r") as file:
        config = file.read() 
      
      sftp.close()

      vm_conf_map[vmid] = base64.b64encode(config).decode("utf-8")

    ssh.close()

  return vm_conf_map


# collect all pvc and pv information
def collect_raw_k8s_meta(backup_config, k8s_kubeconfigs):

  k8s_stack_meta = {}

  k8s_stack_namespace_secrets = {}

  for k8s_stack, k8s_backup_config in backup_config["k8s_stacks"].items():

    if k8s_backup_config["exclude_namespaces"] is not None and k8s_backup_config["include_namespaces"] is not None:
      raise Exception(f"cannot specify include and exclude for k8s_stack {k8s_stack}")
      
    kubeconfig = k8s_kubeconfigs[k8s_stack]
    master_ipv4 = kubeconfig["master_ip"]
    kubeconfig_dict = yaml.safe_load(kubeconfig["raw_kubeconfig"])

    # override the connection ip as it is set to localhost on the machines
    kubeconfig_dict["clusters"][0]["cluster"]["server"] = f"https://{master_ipv4}:6443"
    logger.debug(f"kubeconfig dict {pformat(kubeconfig_dict)}")

    # init kube client
    loader = KubeConfigLoader(config_dict=kubeconfig_dict)
    configuration = client.Configuration()
    loader.load_and_set(configuration)

    # Create a client from this configuration
    api_client = client.ApiClient(configuration)
    v1 = client.CoreV1Api(api_client=api_client)

    # Use it
    k8s_backup_meta = []

    # sub dict for secrets of each namespace
    k8s_stack_namespace_secrets[k8s_stack] = {}

    for namespace_item in v1.list_namespace().items:
      namespace = namespace_item.metadata.name

      if k8s_backup_config["exclude_namespaces"] is not None and namespace in k8s_backup_config["exclude_namespaces"]:
        continue

      if k8s_backup_config["include_namespaces"] is not None and namespace not in k8s_backup_config["include_namespaces"]:
        continue  
      
      # collect secrets of namespace
      k8s_stack_namespace_secrets[k8s_stack][namespace] = [secret.to_dict() for secret in v1.list_namespaced_secret(namespace=namespace).items]

      pvc_list = v1.list_namespaced_persistent_volume_claim(namespace=namespace)
      
      for pvc in pvc_list.items:
        pvc_name = pvc.metadata.name
        volume_name = pvc.spec.volume_name
        status = pvc.status.phase
    
        if volume_name:
          pv = v1.read_persistent_volume(name=volume_name)
          pv_dict_b64 = base64.b64encode(pickle.dumps(pv.to_dict())).decode('utf-8') 

          pvc_dict_b64 = base64.b64encode(pickle.dumps(pvc.to_dict())).decode('utf-8') 
          
          k8s_backup_meta.append({"type": "k8s", "namespace": namespace, "pvc_name": pvc_name, "namespace": namespace, 
                                  "image_name": pv.spec.csi.volume_attributes["imageName"], "pool": pv.spec.csi.volume_attributes["pool"],
                                  "pvc_dict_b64": pvc_dict_b64, "pv_dict_b64": pv_dict_b64, "storage_class": pvc.spec.storage_class_name})
        else:
          logger.debug(f"PVC: {pvc_name} -> Not bound to a PV [Status: {status}]")
    
    k8s_stack_meta[k8s_stack] = k8s_backup_meta
  
  return k8s_stack_meta, k8s_stack_namespace_secrets


# collect all existing vms / lxcs that we want to backup
def collect_raw_vm_meta(proxmox, backup_config):
  backup_vm_meta = []

  # collect vm stacks to know what vm to backup
  vm_stacks = []
  if backup_config["other_stacks"] is not None:
    vm_stacks.extend(backup_config["other_stacks"])
  else:
    logger.info("no other stacks to backup defined, skipping")
  vm_stacks.extend(backup_config["k8s_stacks"].keys())

  # k8s exclude include logic
  exclude_vms = {}
  include_vms = {}
  for stack_name, k8s_conf in backup_config["k8s_stacks"].items():
    if k8s_conf["exclude_hostnames"] is not None and k8s_conf["include_hostnames"] is not None:
      raise Exception(f"Cannot both include and exclude hostnames {stack_name}")

    if k8s_conf["exclude_hostnames"] is not None:
      exclude_vms[stack_name] = k8s_conf["exclude_hostnames"]

    if k8s_conf["include_hostnames"] is not None:
      include_vms[stack_name] = k8s_conf["include_hostnames"]

  ceph_storage_pools = [storage['pool'] + ":" for storage in proxmox.storage.get() if storage['type'] == 'rbd'] # added : for easy filtering of vm confs
  
  for node in proxmox.nodes.get():
    node_name = node["node"]
    logger.info("collecting node " + node_name)

    if node["status"] == "offline":
      logger.info(f"skipping offline node {node_name}")
      continue

    # we later need to connect to the node via ssh and fetch lxc/qemu config for backup
    ifaces = proxmox.nodes(node_name).network.get()
    node_ip_address = None
    for iface in ifaces:
      if 'gateway' in iface:
        if node_ip_address is not None:
          raise Exception(f"found multiple ifaces with gateways for node {node_name}")
        node_ip_address = iface.get("address")

    if node_ip_address is None:
      raise Exception(f"Could not find ip for node {node_name}")

    for qemu in proxmox.nodes(node_name).qemu.get():
      logger.debug(f"processing qemu {qemu}")
      if "tags" not in qemu:
        continue # non stack vm

      stack_tag = next((tag for tag in qemu["tags"].split(";") if tag in vm_stacks), None)

      if stack_tag:
        if stack_tag in exclude_vms and qemu["name"] in exclude_vms[stack_tag]:
          logger.debug("continue due to exclude")
          continue

        if stack_tag in include_vms and qemu["name"] not in include_vms[stack_tag]:
          logger.debug("continue due to include")
          continue

        vm_config = proxmox.nodes(node_name).qemu(qemu["vmid"]).config.get()
        
        # collect disk configs
        disk_confs = {}

        for key in vm_config:
          for disk_pattern in VM_DISK_PATTERNS:
            # only append disks that match pattern and are actually managed by ceph
            if re.search(disk_pattern, key) and any(storage_pool in vm_config[key] for storage_pool in ceph_storage_pools):
              disk_confs[key] = vm_config[key]
              break

        if not disk_confs:
          raise Exception(f"No disk could be identified for {vm_config}")

        backup_vm_meta.append({"type": "qemu", "qemu_raw": qemu, "vmid": qemu["vmid"], "disk_confs": disk_confs, "tags": vm_config["tags"], "host_ip": node_ip_address})
      
    
    for lxc in proxmox.nodes(node_name).lxc.get():
      if "tags" not in lxc:
        continue # non stack vm
      
      if backup_config["other_stacks"] is not None and any(tag in backup_config["other_stacks"] for tag in lxc["tags"].split(";")):

        lxc_config = proxmox.nodes(node_name).lxc(lxc["vmid"]).config.get()

        # collect disk configs
        disk_confs = {}
        for key in lxc_config:
          for disk_pattern in LXC_DISK_PATTERNS:
            if re.search(disk_pattern, key) and any(storage_pool in lxc_config[key] for storage_pool in ceph_storage_pools):
              disk_confs[key] = lxc_config[key]

        if not disk_confs:
          raise Exception(f"No disk could be identified for {lxc_config}")

        backup_vm_meta.append({"type": "lxc", "lxc_raw": lxc, "vmid": lxc["vmid"], "disk_confs": disk_confs, "tags": lxc_config["tags"], "host_ip": node_ip_address})
  
  return backup_vm_meta


def pool_images(raw_vm_meta, raw_k8s_meta):
  # initialize for images grouped by pool
  unique_pools = set()

  # collect pools from vms
  for vm_meta in raw_vm_meta:
    for disk_conf in vm_meta["disk_confs"].values():
      pool = disk_conf.split(",")[0].split(":")[0]
      unique_pools.add(pool)

  # collect pools from k8s volumes
  for k8s_stack, k8s_metas in raw_k8s_meta.items():
    for k8s_meta in k8s_metas:
      unique_pools.add(k8s_meta["pool"])

  # create rbd groups 
  for pool in unique_pools:
    try:
      # check for errors, capture stderr output as text
      subprocess.run(["rbd", "group", "create", f"{pool}/backups"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      logger.warning(e.stdout + e.stderr) # no problem if group already exists, cleanup failed tho

  logger.info("adding images to groups")
  # add all vm disks to the groups
  for vm_meta in raw_vm_meta:
    for disk_conf in vm_meta["disk_confs"].values():
      image = disk_conf.split(",")[0].split(":")[1]
      pool = disk_conf.split(",")[0].split(":")[0]
      try:
        subprocess.run(["rbd", "group", "image", "add", f"{pool}/backups", f"{pool}/{image}"], check=True, capture_output=True, text=True)
      except subprocess.CalledProcessError as e:
        logger.error(e.stdout + e.stderr) # proper error printing
        raise
  
  # add rbds from pvcs
  for k8s_metas in raw_k8s_meta.values():
    for k8s_meta in k8s_metas:
      pool = k8s_meta["pool"]
      image = k8s_meta["image_name"]
      try:
        subprocess.run(["rbd", "group", "image", "add", f"{pool}/backups", f"{pool}/{image}"], check=True, capture_output=True, text=True)
      except subprocess.CalledProcessError as e:
        logger.error(e.stdout + e.stderr) # proper error printing
        raise

  return unique_pools


def clone(pool, image, timestamp):
  try:
    command = subprocess.run(["rbd", "snap", "ls", "--all", "--format", "json", f"{pool}/{image}"], check=True, capture_output=True, text=True)
    snaps = json.loads(command.stdout)
    # doesnt logger.info anything on success
  except subprocess.CalledProcessError as e:
    logger.error(e.stdout + e.stderr)
    raise
  
  for snap in snaps:
    if snap["namespace"]["type"] == "group" and snap["namespace"]["group snap"] == timestamp: 
      snap_id = snap["id"]
      break

  logger.debug(f"image {image} snap id {snap_id}")

  # create temporary clone
  try:
    subprocess.run(["rbd", "clone", "--snap-id", str(snap_id), f"{pool}/{image}", f"{pool}/temp-clone-{timestamp}-{image}", "--rbd-default-clone-format", "2"], check=True, capture_output=True, text=True)
  except subprocess.CalledProcessError as e:
    logger.error(e.stdout + e.stderr)
    raise


def snap_and_clone(raw_vm_meta, raw_k8s_meta, timestamp, unique_pools):
  logger.info("creating snaps")
  for pool in unique_pools:
    try:
      subprocess.run(["rbd", "group", "snap", "create", f"{pool}/backups@{timestamp}"], check=True, capture_output=True, text=True)
      # doesnt logger.info anything on success
    except subprocess.CalledProcessError as e:
      logger.error(e.stdout + e.stderr)
      raise

  logger.info("creating clones")

  # clone all the snapshots into new images so we can export them
  # sadly there isnt yet a direct export function for group snapshots
  for vm_meta in raw_vm_meta:
    for disk_conf in vm_meta["disk_confs"].values():
      image = disk_conf.split(",")[0].split(":")[1]
      pool = disk_conf.split(",")[0].split(":")[0]
      clone(pool, image, timestamp)

  for k8s_metas in raw_k8s_meta.values():
    for k8s_meta in k8s_metas:
      pool = k8s_meta["pool"]
      image = k8s_meta["image_name"]
      clone(pool, image, timestamp)


async def send_exports(commands):
  for send_command in commands:
    backup_addr = send_command["backup_addr"]
    params = send_command["params"]

    request_dict = {
      "borg_archive_type": params["type"],
      "archive_name": params["image_name"],
      "timestamp": params["timestamp"],
      "stdin_name": params["image_name"] + ".raw"
    }
    logger.info(request_dict)

    # to get full performance we need to have the subprocess reading async aswell
    async def async_chunk_generator():
        proc = await asyncio.create_subprocess_exec(
            *send_command["subprocess_args"],
            stdout=asyncio.subprocess.PIPE
        )

        while True:
            chunk = await proc.stdout.read(4 * 1024 * 1024 * 10)  # 4MB
            if not chunk:
                break
            yield chunk

        await proc.wait()

    await net.archive_async(backup_addr, request_dict, async_chunk_generator)


async def send_backups(raw_vm_meta, raw_k8s_meta, timestamp, backup_addr):
  send_commands = []

  typed_send_commands = {}
  for stype in ["k8s", "lxc", "qemu"]:
    typed_send_commands[stype] = []

  for vm_meta in raw_vm_meta:
    for disk_conf in vm_meta["disk_confs"].values():
      image = disk_conf.split(",")[0].split(":")[1]
      pool = disk_conf.split(",")[0].split(":")[0]

      params = {"timestamp": timestamp, "image_name": image, "pool": pool, "type": vm_meta["type"]}

      typed_send_commands[vm_meta["type"]].append({"params": params, "backup_addr": backup_addr, "subprocess_args": ["rbd", "export", f"{pool}/temp-clone-{timestamp}-{image}", "-"]})


  for k8s_metas in raw_k8s_meta.values():
    for k8s_meta in k8s_metas:
      pool = k8s_meta["pool"]
      image = k8s_meta["image_name"]

      params = {"timestamp": timestamp, "image_name": image, "pool": pool, "type": k8s_meta["type"]}

      typed_send_commands[k8s_meta["type"]].append({"params": params, "backup_addr": backup_addr, "subprocess_args": ["rbd", "export", f"{pool}/temp-clone-{timestamp}-{image}", "-"]})

  # start one thread per type, since borg on bdd side is single threaded per archive
  export_tasks = []
  for commands in typed_send_commands.values():
    export_tasks.append(asyncio.create_task(send_exports(commands)))

  await asyncio.gather(*export_tasks)


async def post_image_meta(raw_vm_meta, raw_k8s_meta, timestamp, backup_config, backup_addr):
  # post meta for vms
  vm_stacks = []
  if backup_config["other_stacks"] is not None:
    vm_stacks.extend(backup_config["other_stacks"])
    
  vm_stacks.extend(backup_config["k8s_stacks"].keys())

  for vm_meta in raw_vm_meta:
    stack_tag = None
    for tag in vm_meta["tags"].split(";"):
      if tag in vm_stacks:
        stack_tag = tag

    if stack_tag is None:
      raise Exception(f"stack tag for {vm_meta} could not be found! {vm_stacks}")

    for conf_key, disk_conf in vm_meta["disk_confs"].items():
      image = disk_conf.split(",")[0].split(":")[1]
      pool = disk_conf.split(",")[0].split(":")[0]

      body = {"timestamp": timestamp, "image_name": image, "pool": pool, "stack": stack_tag, "type": vm_meta["type"], "conf_key": conf_key, 
              "disk_conf": disk_conf, "vmid": vm_meta["vmid"]}
      logger.debug(f"posting {body}")
      await net.image_meta(backup_addr, body)


  for k8s_stack, k8s_metas in raw_k8s_meta.items():
    for k8s_meta in k8s_metas:
      pool = k8s_meta["pool"]
      image = k8s_meta["image_name"]
      body = {"timestamp": timestamp, "image_name": image, "pool": pool, "stack": k8s_stack, "type": k8s_meta["type"], "namespace": k8s_meta["namespace"],
              "pvc_dict_b64": k8s_meta['pvc_dict_b64'], "pv_dict_b64": k8s_meta['pv_dict_b64'], "pvc_name": k8s_meta["pvc_name"], "storage_class": k8s_meta["storage_class"]}

      logger.debug(f"posting {body}")
      await net.image_meta(backup_addr, body)


async def post_k8s_stack_meta(k8s_kubeconfigs, k8s_stack_namespace_secrets, timestamp, backup_addr):
  for k8s_stack, kubeconfig in k8s_kubeconfigs.items():
    namespace_secret_dict_b64 = base64.b64encode(pickle.dumps(k8s_stack_namespace_secrets[k8s_stack])).decode('utf-8') 
    body = {"timestamp": timestamp, "stack": k8s_stack, "type": "k8s", "raw_kubeconfig": kubeconfig["raw_kubeconfig"], "master_ip": kubeconfig["master_ip"], "namespace_secret_dict_b64": namespace_secret_dict_b64}
    logger.debug(f"posting {body}")

    await net.stack_meta(backup_addr, body)


async def post_vm_stack_meta(raw_vm_meta, vm_conf_map, backup_config, backup_addr, timestamp):
  # post meta for vms
  vm_stacks = []
  if backup_config["other_stacks"] is not None:
    vm_stacks.extend(backup_config["other_stacks"])

  vm_stacks.extend(backup_config["k8s_stacks"].keys())

  # group raw meta by vmid
  vmid_vm_meta = {}
  for vm_meta in raw_vm_meta:
    vmid_vm_meta[vm_meta["vmid"]] = vm_meta

  for vmid, vm_conf in vm_conf_map.items():
    vm_meta = vmid_vm_meta[vmid]
    stack_tag = None
    for tag in vm_meta["tags"].split(";"):
      if tag in vm_stacks:
        stack_tag = tag

    if stack_tag is None:
      raise Exception(f"stack tag for {vm_meta} could not be found! {vm_stacks}")
    
    body = {"timestamp": timestamp, "stack": stack_tag, "type": vm_meta["type"], "vmid": vmid, "vm_conf": vm_conf}
    logger.debug(f"posting {body}")

    await net.stack_meta(backup_addr, body)

    
def cleanup(raw_vm_meta, raw_k8s_meta, timestamp, unique_pools):
  logger.info("cleanup")
  # delete tmp images
  if raw_vm_meta is not None:
    for vm_meta in raw_vm_meta:
      for disk_conf in vm_meta["disk_confs"].values():
        image = disk_conf.split(",")[0].split(":")[1]
        pool = disk_conf.split(",")[0].split(":")[0]
        try:
          subprocess.run(["rbd", "rm", f"{pool}/temp-clone-{timestamp}-{image}"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
          logger.warning(e.stdout + e.stderr)


  if raw_k8s_meta is not None:
    for k8s_stack, k8s_metas in raw_k8s_meta.items():
      for k8s_meta in k8s_metas:
        pool = k8s_meta["pool"]
        image = k8s_meta["image_name"]
        try:
          subprocess.run(["rbd", "rm", f"{pool}/temp-clone-{timestamp}-{image}"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
          logger.warning(e.stdout + e.stderr)


  if unique_pools is not None:
    # delete snaps
    for pool in unique_pools:
      logger.debug("removing snaps from pool " + pool)
      try:
        subprocess.run(["rbd", "group", "snap", "rm", f"{pool}/backups@{timestamp}"], check=True, capture_output=True, text=True)
        # doesnt logger.info anything on success
      except subprocess.CalledProcessError as e:
        logger.warning(e.stdout + e.stderr)

    # delete groups
    for pool in unique_pools:
      logger.debug("removing backup group from pool " + pool)
      try:
        subprocess.run(["rbd", "group", "rm", f"{pool}/backups"], check=True, capture_output=True, text=True)
        # doesnt logger.info anything on success
      except subprocess.CalledProcessError as e:
        logger.warning(e.stdout + e.stderr)