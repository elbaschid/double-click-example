import re
import click


def validate_api_key(ctx, param, value):
    if not value:
        raise click.BadParameter('you need to provide an API key')

    if not re.match(r'[a-z0-9]{32}', str(value)):
        raise click.BadParameter('invalid API key format')

    return value


@click.command()
@click.option('--api-key', envvar='API_KEY', callback=validate_api_key)
def main(api_key):
    print(f'Your API key is: {api_key}')
