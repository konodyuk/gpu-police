from pathlib import Path

from box import Box

DEFAULT_FILENAME = "~/.gpu-police/config.yaml"

config = None

def load_config(filename):
    global config
    config = Box.from_yaml(open(Path(filename).expanduser()).read())
    print(config)
