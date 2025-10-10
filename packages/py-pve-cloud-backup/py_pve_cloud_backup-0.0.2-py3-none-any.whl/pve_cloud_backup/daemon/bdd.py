from tinydb import TinyDB
import subprocess
from pathlib import Path
import logging
from shared import IMAGE_META_DB_PATH, STACK_META_DB_PATH, BACKUP_DIR, copy_backup_generic, RBD_REPO_TYPES
import os
from enum import Enum
import asyncio
import struct
import pickle
import zstandard as zstd


log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(level=log_level)
logger = logging.getLogger("bdd")

ENV = os.getenv("ENV", "TESTING")

FILE_REPO_TYPES = ["nextcloud", "git"] # different borg archives for each


def init_backup_dir():
  if ENV == "TESTING":
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

  for repo_type in RBD_REPO_TYPES:
    repo_path = f"{BACKUP_DIR}/borg-{repo_type}"
    Path(repo_path).mkdir(parents=True, exist_ok=True)

    # init borg repo, is ok to fail if it already exists
    subprocess.run(["borg", "init", "--encryption=none", repo_path])

  for file_type in FILE_REPO_TYPES:
    repo_path = f"{BACKUP_DIR}/borg-{file_type}"
    Path(repo_path).mkdir(parents=True, exist_ok=True)

    # init borg repo, is ok to fail if it already exists
    subprocess.run(["borg", "init", "--encryption=none", repo_path])

  if ENV == 'PRODUCTION':
    copy_backup_generic()


class Command(Enum):
  ARCHIVE = 1
  IMAGE_META = 2
  STACK_META = 3


lock_dict = {}

def get_lock(lock_type):
  if lock_type not in RBD_REPO_TYPES and lock_type not in FILE_REPO_TYPES and lock_type not in ["stack", "image"]:
    raise Exception(f"Unknown type {lock_type}")
  
  if lock_type not in lock_dict:
    lock_dict[lock_type] = asyncio.Lock()
  
  return lock_dict[lock_type]


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
  addr = writer.get_extra_info('peername')
  logger.info(f"Connection from {addr}")
  
  command = Command(struct.unpack('B', await reader.read(1))[0])
  logger.info(f"{addr} send command: {command}")

  try:
    match command:
      case Command.ARCHIVE:
        # each archive request starts with a pickled dict containing parameters
        dict_size = struct.unpack('!I', (await reader.readexactly(4)))[0]
        req_dict = pickle.loads((await reader.readexactly(dict_size)))
        logger.info(req_dict)

        # extract the parameters
        borg_archive_type = req_dict["borg_archive_type"] # borg locks 
        archive_name = req_dict["archive_name"]
        timestamp = req_dict["timestamp"]

        # lock locally, we have one borg archive per archive type
        async with get_lock(borg_archive_type):
          borg_archive = f"{BACKUP_DIR}/borg-{borg_archive_type}::{archive_name}_{timestamp}"
          logger.info(f"accuired lock {borg_archive_type}")

          # send continue signal, meaning we have the lock and export can start.
          writer.write(b'\x01')  # signal = 0x01 means "continue"
          await writer.drain()
          logger.debug("send go")

          # initialize the borg subprocess we will pipe the received content to
          # decompressor = zlib.decompressobj()
          decompressor = zstd.ZstdDecompressor().decompressobj()
          borg_proc = await asyncio.create_subprocess_exec(
            "borg", "create", "--compression", "zstd,1",
            "--stdin-name", req_dict["stdin_name"],
            borg_archive, "-",
            stdin=asyncio.subprocess.PIPE
          )

          # read compressed chunks
          while True:
            # client first always sends chunk size
            chunk_size = struct.unpack("!I", (await reader.readexactly(4)))[0]
            if chunk_size == 0:
              break # client sends 0 chunk size at the end to signal that its finished uploading
            chunk = await reader.readexactly(chunk_size)
            
            # decompress and write
            decompressed_chunk = decompressor.decompress(chunk)
            if decompressed_chunk:
              borg_proc.stdin.write(decompressed_chunk)
              await borg_proc.stdin.drain()

          # the decompressor does not always return a decompressed chunk but might retain 
          # and return empty. at the end we need to call flush to get everything out
          borg_proc.stdin.write(decompressor.flush())
          await borg_proc.stdin.drain()

          # close the proc stdin pipe, writer gets closed in finally
          borg_proc.stdin.close()
          exit_code = await borg_proc.wait()

          if exit_code != 0:
            raise Exception(f"Borg failed with code {exit_code}")

      case Command.STACK_META:
        # read meta dict size
        dict_size = struct.unpack('!I', (await reader.readexactly(4)))[0]
        meta_dict = pickle.loads((await reader.readexactly(dict_size)))

        async with get_lock("stack"):
          meta_db = TinyDB(STACK_META_DB_PATH)
          meta_db.insert(meta_dict)

      case Command.IMAGE_META:
        dict_size = struct.unpack('!I', (await reader.readexactly(4)))[0]
        meta_dict = pickle.loads((await reader.readexactly(dict_size)))

        async with get_lock("image"):
          meta_db = TinyDB(IMAGE_META_DB_PATH)
          meta_db.insert(meta_dict)

  except asyncio.IncompleteReadError as e:
    logger.error("Client disconnected", e)
  finally:
    writer.close()
    # dont await on server side


async def run():
  init_backup_dir()

  server = await asyncio.start_server(handle_client, "0.0.0.0", 8888)
  addr = server.sockets[0].getsockname()
  logger.info(f"Serving on {addr}")
  async with server:
      await server.serve_forever()


def main():
  asyncio.run(run())

  

