"""integervalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from .value import Value


class IntegerValue(Value):

    def check_value(self, value):
        if not isinstance(value, int):
            raise TypeError(
                'Expecting an value of type \'int\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        # wrap value so booleans are converted to int type
        super().set_value(model, int(value))
