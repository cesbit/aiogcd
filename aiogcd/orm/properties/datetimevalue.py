from .value import Value
from ...connector.timestampvalue import TimestampValue
import re

RFC3339_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:(?:[\+\-]\d{2}:\d{2})|Z)$')  # nopep8


class DatetimeValue(Value):

    def check_value(self, value):
        if not isinstance(value, TimestampValue):
            raise TypeError(
                'Expecting an value of type \'TimestampValue\' for property '
                '{!r} but received type {!r}.'
                .format(self.name, value.__class__.__name__))

        if not RFC3339_RE.search(str(value)):
            raise TypeError(
                'Expecting a value of type \'str\' in RFC3339 datetime format '
                'for property {!r}.'
                .format(self.name))

    def set_value(self, model, value):
        if isinstance(value, str):
            value = TimestampValue(value)

        self.check_value(value)
        super().set_value(model, value)
