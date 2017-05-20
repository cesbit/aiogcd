"""anyvalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from .value import Value


class AnyValue(Value):

    def __init__(self, default=None, required=True, accept=None):
        """Initialize a mapped property.

        When 'accept' is None any type is accepted. A tuple can be
        used to force one of the specified types.

        :param default: default value, all types allowed
        :param required: boolean
        :param accept: None or tuple
        """
        self._accept = accept
        super().__init__(default=default, required=required)

    def check_value(self, value):
        if self._accept and not isinstance(value, self._accept):
            raise TypeError(
                'Received value for property {!r} is of invalid type: {!r}'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, value)
