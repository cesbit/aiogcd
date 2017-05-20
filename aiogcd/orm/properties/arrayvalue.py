"""arrayvalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from .value import Value
from ..utils import ProtectedList


class ArrayValue(Value):

    def __init__(self, default=None, required=True, accept=None):
        """Initialize an array property.

        When 'accept' is None any type in the list is accepted. A tuple can be
        used to force each list item to be one of the specified types.

        For example:

        # my_array will only accept Key objects.
        my_array = ArrayValue(accept=(Key,))

        :param default: list or None
        :param required: boolean
        :param accept: None or tuple
        """
        self._accept = accept
        super().__init__(default=default, required=required)

    def check_value(self, value):
        if not isinstance(value, list):
            raise TypeError(
                'Expecting an value of type \'int\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

        if self._accept and \
                not all([isinstance(item, self._accept) for item in value]):
            raise TypeError(
                'At least one item in array property {!r} has an invalid type.'
                .format(self.name))

    def _protect(self, value):
        if self._accept and not isinstance(value, self._accept):
            raise TypeError('Invalid type {!r} for array property {!r}.'
                            .format(value.__class__.__name__, self.name))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, ProtectedList(value, protect=self._protect))
