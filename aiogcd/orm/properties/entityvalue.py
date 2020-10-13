from .value import Value


class EntityValue(Value):

    def check_value(self, value):
        if not isinstance(value, dict):
            raise TypeError(
                'Expecting an value of type \'dict\' for property {!r} '
                'but received type {!r}.'
                .format(self.name, value.__class__.__name__))

    def set_value(self, model, value):
        self.check_value(value)
        super().set_value(model, value)
