"""doublevalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@cesbit.com>
"""
from .value import Value


class DoubleValue(Value):

    def check_value(self, value):
        if not isinstance(value, float):
            raise TypeError(
                'Expecting an value of type \'float\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, value)
