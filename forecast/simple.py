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
@click.pass_obj
def config(obj):
    config_file = obj.config_file
    api_key = obj.api_key

    api_key = click.prompt('Please enter your API key', default=api_key)

    validate_api_key(api_key)

    with open(config_file, 'w') as cfg:
        cfg.write(api_key)


@main.command('find')
@click.pass_obj
@click.argument('location', type=LOCATION)
def find_city_id(obj, location):
    api_key = obj.api_key

    if location.type is 'id':
        click.echo(f"City ID: {location.value}")
        return

    url = 'https://api.openweathermap.org/data/2.5/find'
    params = {
        'APPID': api_key,
        'q': location.value,
    }

    response = session.get(url, params=params)
    data = response.json()
    click.echo(f"City ID: {data['list'][0]['id']}")


@main.command()
@click.pass_obj
@click.argument('location', type=LOCATION)
def today(obj, location):
    api_key = obj.api_key

    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        'APPID': api_key,
        location.query: location.value,
        'units': 'metric',
    }

    response = session.get(url, params=params)

    data = response.json()

    name = data.get('name', location.value)
    description = data['weather'][0]['description']

    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']

    click.secho(f'Weather for {name}: {description.capitalize()}')
    click.secho(f'Temperature (C): {temp_min} to {temp_max}')


@main.command()
@click.pass_obj
@click.argument('location', type=LOCATION)
def forecast(obj, location):
    api_key = obj.api_key

    url = 'https://api.openweathermap.org/data/2.5/forecast'

    params = {
        'APPID': api_key,
        location.query: location.value,
        'units': 'metric',
    }

    response = session.get(url, params=params)

    data = response.json()

    time = 'Time'
    description = 'Description'
    temp_min = 'Min Temp'
    temp_max = 'Max Temp'

    click.echo('')
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
