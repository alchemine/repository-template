"""Configuration constants for the project."""

from os import getenv
from pathlib import Path
from logging import getLogger

import yaml
from easydict import EasyDict


logger = getLogger(__name__)


##################################################
# Environments
##################################################
ENV = getenv("ENV", "dev")
SERVICE_NAME = getenv("SERVICE_NAME", "service")
VERSION = getenv("VERSION", "v1")
SEED = getenv("SEED", 42)


##################################################
# PATH
##################################################
ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
CACHE_DIR = ROOT_DIR / "cache"


##################################################
# Configurations
##################################################
with open(CONFIG_DIR / "config.yaml", "r") as f:
    CFG = EasyDict(yaml.safe_load(f))


if __name__ == "__main__":
    print(
        f"""
ENV: {ENV}
ROOT_DIR: {ROOT_DIR}
"""
    )