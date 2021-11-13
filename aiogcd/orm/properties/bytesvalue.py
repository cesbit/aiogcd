"""bytesvalue.py

Created on: Nov 13, 2021
    Author: Jeroen van der Heijden <jeroen@cesbit.com>
"""
from .value import Value


class BytesValue(Value):

    def check_value(self, value):
        if not isinstance(value, bytes):
            raise TypeError(
                'Expecting an value of type \'bytes\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, value)
