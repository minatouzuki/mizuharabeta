import sys
import os
import time
import logging
import importlib
import redis
from pyrogram import Client

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.6!\n"
            "Multiple features depend on this. Bot quitting."
        )
    )
    quit(1)  # Quit the Script

# the secret configuration specific things
ENV = bool(os.environ.get('ENV', False))

if ENV:
# Redis Cache
REDIS_HOST = os.environ.get('REDIS_URI', None)
REDIS_PORT = os.environ.get('REDIS_PORT', None)
REDIS_PASS = os.environ.get('REDIS_PASS', None)
redisClient = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
TOKEN = os.environ.get('TOKEN', None)
# Account Related
APP_ID = os.environ.get('APP_ID', None)
API_HASH = os.environ.get('API_HASH', None)

# General Config
MESSAGE_DUMP = os.environ.get('MESSAGE_DUMP', None)
SUPPORT_GROUP = os.environ.get('SUPPORT_GROUP', None)
SUPPORT_CHANNEL = os.environ.get('SUPPORT_CHANNEL', None)

# Users Config
OWNER_ID = os.environ.get('OWNER_ID', None)
DEV_USERS = os.environ.get('DEV_USERS', None)
SUDO_USERS = os.environ.get('SUDO_USERS', None)
WHITELIST_USERS = os.environ.get('WHITELIST_USERS', None)
SUPPORT_STAFF = list(
    dict.fromkeys([OWNER_ID] + SUDO_USERS + DEV_USERS + WHITELIST_USERS)
)  # Remove duplicates!

# Plugins, DB and Workers
DB_URI = os.environ.get('DB_URI', None)
NO_LOAD = os.environ.get('NO_LOAD', None)
WORKERS = os.environ.get('WORKERS', None)

# Prefixes
PREFIX_HANDLER = os.environ.get('PREFIX_HANDLER', None)
DEV_PREFIX_HANDLER = os.environ.get('DEV_PREFIX_HANDLER', None)
ENABLED_LOCALES = os.environ.get('ENABLED_LOCALES', None)
VERSION = os.environ.get('VERSION', None)

HELP_COMMANDS = {}  # For help menu
UPTIME = time.time()  # Check bot uptime


def load_cmds(ALL_PLUGINS):
    for single in ALL_PLUGINS:
        imported_module = importlib.import_module("alita.plugins." + single)
        if not hasattr(imported_module, "__PLUGIN__"):
            imported_module.__PLUGIN__ = imported_module.__name__

        if not imported_module.__PLUGIN__.lower() in HELP_COMMANDS:
            if hasattr(imported_module, "__help__") and imported_module.__help__:
                HELP_COMMANDS[
                    imported_module.__PLUGIN__.lower()
                ] = imported_module.__help__
            else:
                continue
        else:
            raise Exception(
                "Can't have two plugins with the same name! Please change one"
            )

    return f"Plugins Loaded: {list(list(HELP_COMMANDS.keys()))}"
