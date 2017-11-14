import os
import re
import click
import requests

from dateutil.parser import parse
from collections import namedtuple

from .parameters import LOCATION

Config = namedtuple('Config', ['config_file', 'api_key'])

session = requests.Session()


def validate_api_key(value):
    if not value:
        raise click.ClickException('you need to provide an API key')

    if not re.match(r'[a-z0-9]{32}', str(value)):
        raise click.ClickException('invalid API key format')

    return value


@click.group(chain=True)
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


@main.command('find')
@click.pass_obj
@click.argument('location', type=LOCATION)
@click.argument('output', type=click.File('w'), default='-')
def find_city_id(obj, location, output):
    api_key = obj.api_key

    if location.type is 'id':
        output.write(f"{location.value}")
        return

    url = 'https://api.openweathermap.org/data/2.5/find'
    params = {
        'APPID': api_key,
        'q': location.value,
    }

    response = session.get(url, params=params)
    data = response.json()
    output.write(f"{data['list'][0]['id']}")


@main.command()
@click.pass_obj
@click.argument('location', type=click.File('r'), default='-')
def forecast(obj, location):
    api_key = obj.api_key

    value = location.read()
    try:
        value = int(value)
    except ValueError:
        query = 'q'
    else:
        query = 'id'

    url = 'https://api.openweathermap.org/data/2.5/forecast'

    params = {
        'APPID': api_key,
        query: value,
        'units': 'metric',
    }

    response = session.get(url, params=params)
    data = response.json()

    time = 'Time'
    description = 'Description'
    temp_min = 'Min Temp'
    temp_max = 'Max Temp'

    click.echo(f'{time:^20}{description:^20}{temp_min:>10}{temp_max:>10}')
    click.echo('=' * 60)

    for data in data['list']:
        time = parse(data['dt_txt']).strftime('%a, %b %d @ %Hh')

        description = data['weather'][0]['description']

        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']

        click.echo(
            f'{time:<20}{description:^20}{temp_min:>10.1f}{temp_max:>10.1f}'
        )
