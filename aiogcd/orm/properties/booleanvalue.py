"""booleanvalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from .value import Value


class BooleanValue(Value):

    def check_value(self, value):
        if not isinstance(value, bool):
            raise TypeError(
                'Expecting an value of type \'bool\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, value)
