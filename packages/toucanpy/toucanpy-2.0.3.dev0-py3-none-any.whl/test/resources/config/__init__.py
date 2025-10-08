from pathlib import Path

import yaml

from test import RESOURCE_ROOT

DEFAULT_CONFIG_PATH = RESOURCE_ROOT / 'config' / 'config.yml'
TOUCAN_CONFIG = {}


def load_custom_config(config_file: Path):
    global TOUCAN_CONFIG
    with open(config_file, 'r') as f:
        TOUCAN_CONFIG = yaml.safe_load(f)
    return TOUCAN_CONFIG


load_custom_config(DEFAULT_CONFIG_PATH)
