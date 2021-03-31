"""utils.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import base64
import json
from .key import Key
from .timestampvalue import TimestampValue

# Max string length in bytes. (strings are converted to blob values when larger
# than _MAX_STRING_LENGTH)
_MAX_STRING_LENGTH = 1500


def value_to_dict(val):
    if val is None:
        return {'nullValue': None}
    if isinstance(val, bool):
        return {'booleanValue': val}
    if isinstance(val, int):
        return {'integerValue': str(val)}
    if isinstance(val, float):
        return {'doubleValue': val}
    if isinstance(val, str):
        encoded = val.encode('utf-8')
        if len(encoded) > _MAX_STRING_LENGTH:
            return {
                'excludeFromIndexes': True,
                'blobValue': base64.b64encode(encoded)
                .replace(b'+', b'-')
                .replace(b'/', b'_')
                .rstrip(b'=')
                .decode('utf-8')}
        return {'stringValue': val}
    if isinstance(val, Key):
        return {'keyValue': val.get_dict()}
    if isinstance(val, list):
        return {'arrayValue': {'values': [value_to_dict(v) for v in val]}}
    if isinstance(val, TimestampValue):
        return {'timestampValue': str(val)}
    if isinstance(val, dict):
        return {
            'entityValue': {
                'properties': {k: value_to_dict(v) for k, v in val.items()}}}

    raise TypeError('Unsupported type: {}'.format(type(val)))


def value_from_dict(val):
    if 'nullValue' in val:
        return None  # val['nullValue'] is None
    if 'booleanValue' in val:
        return val['booleanValue']
    if 'integerValue' in val:
        return int(val['integerValue'])
    if 'doubleValue' in val:
        return val['doubleValue']
    if 'stringValue' in val:
        return val['stringValue']
    if 'keyValue' in val:
        return Key(val['keyValue'])
    if 'arrayValue' in val:
        return [
            value_from_dict(v)
            for v in val['arrayValue'].get('values', [])]
    if 'timestampValue' in val:
        return TimestampValue(val['timestampValue'])
    if 'blobValue' in val:
        val = val['blobValue'].encode('utf-8')
        pad = b'=' * (4 - len(val) % 4)
        data = base64.b64decode(
            (val + pad).replace(b'-', b'+').replace(b'_', b'/'))
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data
    if 'entityValue' in val:
        return {
            k: value_from_dict(v)
            for k, v in val['entityValue'].get('properties', {}).items()}

    raise TypeError('Unexpected or unsupported value: {}'.format(val))


def make_read_options(transaction=None, eventual=True):
    """Reference:
        https://cloud.google.com/datastore/docs/reference/rest/v1/ReadOptions
    """
    read_options = {
        'readConsistency': 'EVENTUAL' if eventual else 'STRONG',
    }
    if transaction is not None:
        read_options['transaction'] = transaction

    return read_options
