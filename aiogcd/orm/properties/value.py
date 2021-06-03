"""value.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from ...connector.entity import Entity
from ...connector.utils import value_to_dict


class Value:

    def __init__(self, default=None, required=True):
        self.default = default
        self.required = required
        self.name = None

    @property
    def ascending(self):
        return self.name, 'ASCENDING'

    @property
    def descending(self):
        return self.name, 'DESCENDING'

    def check_value(self, value):
        raise NotImplementedError()

    def check_compare(self, value):
        return self.check_value(value)

    def get_value(self, model):
        return model.__dict__.get(self.name, None)

    def set_value(self, model, value):
        Entity.set_property(model, self.name, value)

    def _compare(self, other, op):
        self.check_compare(other)
        return {
            'property': {
                'name': self.name
            },
            'value': value_to_dict(other),
            'op': op
        }

    def __eq__(self, other):
        return self._compare(other, 'EQUAL')

    def __ne__(self, other):
        raise Exception('Cannot use NOT EQUAL in a filter expression')

    def __lt__(self, other):
        return self._compare(other, 'LESS_THAN')

    def __le__(self, other):
        return self._compare(other, 'LESS_THAN_OR_EQUAL')

    def __gt__(self, other):
        return self._compare(other, 'GREATER_THAN')

    def __ge__(self, other):
        return self._compare(other, 'GREATER_THAN_OR_EQUAL')
