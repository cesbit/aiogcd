"""model.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import functools
from ..connector.entity import Entity
from ..orm.properties.value import Value
from ..connector.key import Key
from .filter import Filter
from ..connector.timestampvalue import TimestampValue


class _PropertyClass(dict):
    """Custom dictionary for a GcdModel."""

    def __init__(self, *args):
        self._props = {}
        super().__setitem__('model_props', self._props)

    def __setitem__(self, key, value):
        """Sets the name property for each orm property. Each property is
        added to the 'model_props' dictionary which is bound to the model
        class.
        """
        if isinstance(value, Value):
            value.name = key
            self._props[key] = value
        super().__setitem__(key, value)


class _ModelClass(type):
    """Used as a meta class and uses the __preprare__ method to return a custom
    class dictionary object.
    """
    @classmethod
    def __prepare__(mcs, name, bases):
        return _PropertyClass()

    def __new__(mcs, name, *args, **kwargs):
        result = super().__new__(mcs, name, *args, **kwargs)
        result.__class__.__name__ = name
        return result


class GcdModel(Entity, metaclass=_ModelClass):
    ALLOW_NEW_PROPERTIES = False
    BASE_MODEL_INIT = """
    Model can be initialized using an entity object or by using keyword
    arguments and a key object.

    Examples:
        MyModel(Entity(...))
        MyModel(name='foo', age=3, ..., key=Key(...))
"""
    __kind__ = None

    def __init__(self, entity=None, key=None, **template):
        """Initialize a GcdModel.

        You can initialize a model by using either an Entity OR a Key and
        template.

        :param entity: Entity object.
        :param key: Key object.
        :param template: keyword arguments defining the model properties.
        """
        props = set(self.model_props.keys())

        if entity is not None:
            assert key is None and len(template) == 0, self.BASE_MODEL_INIT
            self.__dict__.update(entity.__dict__)
            props -= set(self.__dict__.keys())

        else:
            assert isinstance(key, Key), self.BASE_MODEL_INIT
            self._properties = set()
            self.key = key

            for name, value in template.items():
                if name in props:
                    props.remove(name)
                    setattr(self, name, value)

        if self.__kind__ != self.key.kind:
            raise TypeError(
                'Expecting kind {expect!r} for model {model} but got {got!r}. '
                'Optionally you can set {model}.__kind__ to {got!r} or to '
                'None if you want to ignore the kind check.'
                .format(
                    expect=self.__kind__,
                    model=self.__class__.__name__,
                    got=self.key.kind))

        for prop in props:
            prop = self.model_props[prop]
            if prop.default is not None:
                setattr(
                    self,
                    prop.name,
                    prop.default() if callable(prop.default) else prop.default)
            elif prop.required:
                raise TypeError(
                    'Missing required property: {}'.format(prop.name))
            else:
                super().__setattr__(prop.name, None)

    def __new__(mcs, *args, **kwargs):
        if getattr(mcs, '__kind__') is None:
            mcs.__kind__ = mcs.__name__
        return super().__new__(mcs)

    def __getattribute__(self, key):
        if key != 'model_props' and key in self.model_props:
            return self.model_props[key].get_value(self)
        return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in self.model_props:
            self.model_props[key].set_value(self, value)
        else:
            super().__setattr__(key, value)

    def set_property(self, prop, value):
        if prop in self.model_props:
            self.model_props[prop].set_value(self, value)
        elif not self.ALLOW_NEW_PROPERTIES:
            raise RuntimeError(
                'Adding new properties on this model is not allowed. '
                'Set {}.ALLOW_NEW_PROPERTIES to True if you really want add '
                'property {!r} to this model.'
                .format(self.__class__.__name__, prop))
        super().set_property(prop, value)

    @classmethod
    def filter(cls, *filters, has_ancestor=None, key=None):
        return Filter(
            cls,
            *filters,
            has_ancestor=has_ancestor,
            key=key)

    @classmethod
    def get_kind(cls):
        if cls.__kind__ is None:
            cls.__kind__ = cls.__name__
        return cls.__kind__

    @classmethod
    async def get_entities(cls, gcd):
        return await Filter(cls).get_entities(gcd)

    def serializable_dict(self, key_as=None):
        data = {
            prop.name: self._serialize_value(prop.get_value(self))
            for prop in self.model_props.values()
            if prop.get_value(self) is not None
        }

        if isinstance(key_as, str):
            data[key_as] = self.key.ks

        return data

    @classmethod
    def _serialize_value(cls, val):
        if isinstance(val, TimestampValue):
            return str(val)
        if isinstance(val, Key):
            return val.ks
        if isinstance(val, list):
            return [cls._serialize_value(v) for v in val]
        return val
