import pytest
import click

from click.testing import CliRunner

from forecast.cli import validate_api_key
from forecast.cli import main


@pytest.mark.parametrize('value', [None, 12])
def test_validate_api_key(value):
    with pytest.raises(click.ClickException):
        validate_api_key(value)


def test_valid_api_key_validation():
    key = '00ee52f44f3350c73f2684a0f23f2805'  # not a real API key
    assert validate_api_key(key) == key


def test_writing_config_file():
    runner = CliRunner()

    with runner.isolated_filesystem() as env:
        api_key = '00ee52f44f3350c73f2684a0f23f2805'

        filename = f'{env}/forecast.cfg'

        result = runner.invoke(
            main,
            ['--config-file', filename, 'config'],
            input=api_key,
        )

        assert result.exit_code == 0, result.output
        assert api_key in result.output

        with open(filename) as cfg_file:
            assert cfg_file.read() == api_key
