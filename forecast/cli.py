import os
import re
import click

from collections import namedtuple
from configparser import ConfigParser

Config = namedtuple('Config', ['config_file', 'api_key'])


def validate_api_key(value):
    if not value:
        raise click.ClickException('you need to provide an API key')

    if not re.match(r'[a-z0-9]{32}', str(value)):
        raise click.ClickException('invalid API key format')

    return value


@click.group()
@click.pass_context
@click.option(
    '--config-file',
    '-c',
    type=click.Path(),
    default=os.path.expanduser('~/.forecast.cfg'))
@click.option('--api-key', envvar='API_KEY', default='')
def main(ctx, config_file, api_key):

    if os.path.exists(config_file):
        with open(config_file) as cfg:
            api_key = cfg.readline()

    ctx.obj = Config(config_file, api_key)


@main.command()
@click.pass_context
def config(ctx):
    config_file = ctx.obj.config_file
    api_key = ctx.obj.api_key

    api_key = click.prompt('Please enter your API key', default=api_key)

    validate_api_key(api_key)

    with open(config_file, 'w') as cfg:
        cfg.write(api_key)


@main.command()
@click.pass_context
def today(ctx):
    api_key = ctx.obj.api_key
    print(f'Your API key is: {api_key}')
