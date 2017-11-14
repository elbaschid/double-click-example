import click

from collections import namedtuple

Location = namedtuple('Location', ['type', 'value', 'query'])


class LocationType(click.ParamType):
    name = 'location'

    def convert(self, value, param, ctx):
        try:
            value = int(value)
        except ValueError:
            location_type = 'name'
            query = 'q'
        else:
            location_type = 'id'
            query = 'id'
        return Location(location_type, value, query)


LOCATION = LocationType()
