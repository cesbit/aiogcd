"""entity.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import json
from .key import Key
from .timestampvalue import TimestampValue
from .utils import value_from_dict
from .utils import value_to_dict


class Entity:

    def __init__(self, entity_res):
        """Initialize an Entity object.

        Example:
        {
            'properties': {
                'name': {'stringValue': 'Example'},
                ...
            },
            'key': {
                'partitionId': {'projectId': 'my_project_id'},
                'path': [
                    {'kind': 'Foo', 'id': 1234},
                    ...
                ]
            }
        }

        See the following link for more information:
        https://cloud.google.com/datastore/docs/reference/rest/v1/Entity
        """
        self.key = Key(entity_res['key'])
        self._properties = set()

        for prop, val in entity_res['properties'].items():
            self._properties.add(prop)
            setattr(self, prop, value_from_dict(val))

    def __str__(self):
        return json.dumps(self.serializable_dict())

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def get_dict(self):
        """Returns dictionary object which can be used to insert, upsert or
        update the entity in the google cloud datastore."""

        # We use __dict__ instead of getattr() since the Entity class might be
        # sub-classed and then getattr() could access a computed property
        # instead of the variable we really want.

        return {
            'key': self.key.get_dict(),
            'properties': {
                prop: value_to_dict(self.__dict__[prop])
                for prop in self._properties
            }
        }

    def serializable_dict(self, key_as=None):
        data = {
            prop: _serialize_value(self.__dict__[prop])
            for prop in self._properties
        }
        if isinstance(key_as, str):
            data[key_as] = self.key.ks
        return data

    def set_property(self, prop, value):
        """Use this method to set a new or change an existing property.

        If you are sure the property already exists, its possible to set the
        property directly. This method must be used for new properties.
        """
        self.__dict__[prop] = value
        self._properties.add(prop)


def _serialize_value(val):
    if isinstance(val, TimestampValue):
        return str(val)
    if isinstance(val, Key):
        return val.ks
    if isinstance(val, list):
        return [_serialize_value(v) for v in val]
    return val
