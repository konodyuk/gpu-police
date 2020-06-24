from pathlib import Path

from box import Box

DEFAULT_FILENAME = "~/.gpu-police/config.toml"

config = None

def load_config(filename):
    global config
    config = Box.from_toml(open(Path(filename).expanduser()).read())
    print(config)
