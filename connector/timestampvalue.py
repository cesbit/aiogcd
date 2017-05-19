"""pathelement.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""


class TimestampValue:

    def __init__(self, timestamp_value):
        self._timestamp_value = timestamp_value

    def __str__(self):
        """Returns the formatted timestamp value."""
        return self._timestamp_value
