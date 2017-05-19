"""jsonvalue.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import json
from .value import Value


class JsonValue(Value):

    def __init__(self, default=None, required=True, accept=None):
        """Initialize an json property.

        When 'accept' is None any type is accepted as long as the value is
        JSON serializable. A tuple can be used to force each value to be one of
        the specified types.

        For example:

        # my_json_prop will only accept dictionary objects.
        my_json_prop = JsonValue(accept=(dict,))

        :param default: list or None
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
        try:
            data = json.dumps(value)
        except TypeError as e:
            raise TypeError('Value for property {!r} could not be parsed: {}'
                            .format(self.name, e))
        model.__dict__['__orig__{}'.format(self.name)] = value
        super().set_value(model, data)

    def get_value(self, model):
        key = '__orig__{}'.format(self.name)

        if key not in model.__dict__:
            try:
                model.__dict__[key] = json.loads(model.__dict__[self.name])
            except Exception as e:
                raise Exception(
                    'Error reading property {!r} '
                    '(see above exception for more info).'
                    .format(self.name)) from e

        return model.__dict__[key]
