Async Google Cloud Datastore API
================================
Package aiogcd includes both a Connector and ORM layer for communicating with Google Cloud Datastore without using App Engine.
> By design the connector has no dependencies to the ORM layer. This makes it possible to use the
connector without the orm layer if this is preferred.

---------------------------------------
  * [Installation](#installation)
  * [Connector](#connector)
    * [Quick usage](#quick-usage)
    * [Entity](#entity)
  * [ORM](#orm-layer)
  * [Namespaces](#namespaces)
  * [Emulator](#emulater)

---------------------------------------

## Installation
The most easy way is to install this package using PyPI:
```
pip install aiogcd
```

To install from source code:
```
python setup.py install
```

## Connector
The connector is designed so that it can be used without using the ORM layer.

### Quick usage:

```python
import asyncio
from aiogcd.connector import GcdConnector

async def example():

    # create a Google Cloud Datastore connector
    gcd = GcdConnector(
        project_id='my_project_id_or_app_id',
        client_id='my_client_id',
        client_secret='my_client_secret',
        token_file='token_file.json')

    # make at least one call to gcd using the connect() function. this function
    # creates the token file in case it does not exists and might prompt the
    # user for a code.
    await gcd.connect()

loop = asyncio.get_event_loop()
loop.run_until_complete(example())


```

### Entity

Create a new entity:

```python
import asyncio
from aiogcd.connector import GcdConnector
from aiogcd.connector.entity import Entity

async def insert_alice():
    gcd = GcdConnector(
        project_id='my_project_id_or_app_id',
        client_id='my_client_id',
        client_secret='my_client_secret',
        token_file='token_file.json')

    await gcd.connect()

    alice = Entity({
        'properties': {
            'name': {'stringValue': 'Alice'},
            'age': {'integerValue': 26}
        },
        'key': {
            'partitionId': {'projectId': gcd.project_id},
            'path': [{'kind': 'User'}]
        }
    })

    await gcd.insert_entity(alice)

loop = asyncio.get_event_loop()
loop.run_until_complete(insert_alice())

```

ORM Layer
=========

```python
import asyncio
from aiogcd.connector import GcdConnector
from aiogcd.connector.key import Key
from aiogcd.orm import GcdModel
from aiogcd.orm.properties import StringValue
from aiogcd.orm.properties import IntegerValue

# Create a GcdModel for kind 'User'
class User(GcdModel):
    name = StringValue()
    age = IntegerValue()

# If you want a model for a specific kind and use a different class name
# you can set __kind__ to the required kind name. For example:

#  class UserModel(GcdModel):
#      __kind__ = 'User'
#      ...

# example insert
async def insert_alice():
    # Create a key. As name/id we are allowed to use None since this is
    # a new key. Gcd will assign a new id to the key.
    key = Key('User', None, project_id=gcd.project_id)

    # Create a new User entity.
    alice = User(name='Alice', age=26, key=key)

    # note that the key has no id assigned yet.
    assert alice.key.id is None

    # Insert the new entity.
    await gcd.insert_entity(alice)

    # The key now has an id assigned
    assert isinstance(alice.key.id, int)

    # return the key, we can use this later
    return alice.key

# example query
async def query_users():
    # query all user entities:
    users = await User.filter().get_entities(gcd)

    # create a Key from a key string:
    key = Key(ks='<key_string>')

    # use the Key to get the User entity:
    user = await User.filter(key=key).get_entity(gcd)

    # get all user entities with name 'Bob' and age greater than 3
    users = await User.filter(
        User.name == 'Bob',
        User.age > 3).get_entities(gcd)

    # get all user entities with name 'Alice' and an ancestor key
    users = await User.filter(
        User.name == 'Alice',
        has_ancestor= Key('Foo', 123)).get_entities(gcd)

    # get all user entities with name 'Alice' and sort on age
    users = await User.filter(
        User.name == 'Alice'
        ).order_by(
            User.age.ascending
        ).get_entities(gcd)

    # get first 2 user entities with name 'Alice' and sort on age
    users = await User.filter(
        User.name == 'Alice'
        ).order_by(
            User.age.ascending
        ).limit(2).get_entities(gcd)

# example update
async def update_age(ks, new_age):
    # get the user by key string
    user = await User.filter(key=Key(ks=ks)).get_entity(gcd)

    # change the age
    user.age = new_age

    # save the changes
    await gcd.update_entity(user)


gcd = GcdConnector(
    project_id='my_project_id_or_app_id',
    client_id='my_client_id',
    client_secret='my_client_secret',
    token_file='token_file.json')

loop = asyncio.get_event_loop()
loop.run_until_complete(gcd.connect())
loop.run_until_complete(insert_alice())
loop.run_until_complete(query_users())

```


Namespaces
==========

As of version 0.11.4, aiogcd has support for namespaces. For using namespaces the `Key` and `GcdModel`

### Key

When initializing a key from a *key-string*, the `namespace_id` is automatically unpacked.
If instead a `path` is used, the namespace can be given using the `namespace_id=<my_namespace>` keyword argument.

It is also possible to set the namespace using a dictionary, like in the example below:

```json
{
    "partitionId": {
        "projectId": "my-project-id",
        "namespaceId": "my-namespace"
    }
    ...
}
```

### GcdModel

If a `GcdModel` is used, it is possible to set the *namespace* on the model. For example:

```python
class Example(GcdModel):
    __namespace__ = 'my-namespace'
```

With the above solution, queries like `Example.get_entities(gcd)` will automatically query the correct namespace.

As an alternative, the `GcdConnector` can be initialized using the `namespace_id=...` keyword argument.
If the `namespace_id` argument is used, all queries will use the given namespace unless explicitly overwritten by a `GcdModel`.


Emulator
========

The Google Datastore emulator is supported by `aiogcd` and thus reads the `DATASTORE_EMULATOR_HOST` environment variable.
Note that the `DATASTORE_PROJECT_ID` will be ignored and still needs to be set using the initialization of the `GcdConnector`.
See https://cloud.google.com/datastore/docs/tools/datastore-emulator for documentation on how to start the emulator.

