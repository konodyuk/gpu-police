import os
import pkg_resources
from pathlib import Path

import click
import shutil
from rich import print

from gpu_police.config import load_config, DEFAULT_FILENAME

config_option = click.option(
    '--config', 
    default=DEFAULT_FILENAME, 
    help='path to config.yaml; by default, ~/.gpu-police/config.yaml is used'
)


@click.group()
def cli():
    pass


@cli.command()
def init():
    path = Path('~/.gpu-police').expanduser()
    if not path.exists():
        print("Created [bold]~/.gpu-police[/] folder")
        os.mkdir(path)
    shutil.copy(pkg_resources.resource_filename('gpu_police', 'default_config.yaml'), path / 'config.yaml')
    print("Created [bold]~/.gpu-police/config.yaml[/] file")
    print("Please manually provide [bold]~/.gpu-police/credentials.json[/] or specify a custom path to it in the config")


@cli.command()
@config_option
def run(config):
    load_config(config)

    import gpu_police.tasks
    from gpu_police.scheduler import ts

    ts.run()


@click.command()
@click.option('--lines', default=None, help='output the last N lines instead of the whole logfile')
def wtf(lines):
    load_config(DEFAULT_FILENAME)

    from gpu_police.config import config

    if lines is None:
        command = f"tail {config.log.file}"
    else:
        command = f"tail -n {lines} {config.log.file}"
    os.system(command)
