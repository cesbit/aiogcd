from .buffer import BufferDecodeError

TYPE_ID = 0
TYPE_NAME = 1


def path_element_from_decoder(decoder):
    kind = None
    name_or_id = None

    while True:
        tt = decoder.get_var_int32()

        if tt == 12:
            break
        if tt == 18:
            kind = decoder.get_prefixed_string()
            continue
        if tt == 24:
            name_or_id = decoder.get_var_int64()
            continue
        if tt == 34:
            name_or_id = decoder.get_prefixed_string()
            continue
        if tt == 0:
            raise BufferDecodeError('corrupt')

    assert kind is not None and name_or_id is not None, \
        'Expecting a path element with a kind and name/id.'

    return PathElement(kind, name_or_id)


class PathElement:

    def __init__(self, kind, name_or_id):
        assert name_or_id is None or isinstance(name_or_id, (int, str)), \
            'Expecting a str or int type but got: {}'.format(
                type(name_or_id))
        self.kind = kind
        self.id = name_or_id

    @property
    def name(self):
        raise TypeError('Use .id instead of .name')

    def encode(self, buffer):
        buffer.add_var_int32(18)
        buffer.add_prefixed_string(self.kind)
        if isinstance(self.id, int):
            buffer.add_var_int32(24)
            buffer.add_var_int64(self.id)
        else:
            buffer.add_var_int32(34)
            buffer.add_prefixed_string(self.id)

    @property
    def byte_size(self):
        n = self._size_str(self.kind)
        if isinstance(self.id, int):
            n += 1 + self._size_var_int(self.id)
        else:
            n += 1 + self._size_str(self.id)

        return n + 1

    def get_dict(self):
        if isinstance(self.id, int):
            return {'kind': self.kind, 'id': str(self.id)}

        if isinstance(self.id, str):
            return {'kind': self.kind, 'name': self.id}

        return {'kind': self.kind}

    @classmethod
    def _size_str(cls, s):
        l = len(s)
        return cls._size_var_int(l) + l

    @staticmethod
    def _size_var_int(n):
        if n < 0:
            return 10

        result = 0
        while True:
            result += 1
            n >>= 7
            if n == 0:
                break
        return result
