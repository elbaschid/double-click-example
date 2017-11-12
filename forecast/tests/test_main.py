import pytest
import click

from forecast.cli import validate_api_key


@pytest.mark.parametrize('value', [None, 12])
def test_validate_api_key(value):
    with pytest.raises(click.ClickException):
        validate_api_key(value)


def test_valid_api_key_validation():
    key = '00ee52f44f3350c73f2684a0f23f2805'
    assert validate_api_key(key) == key
