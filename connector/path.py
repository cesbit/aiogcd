"""path.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from .pathelement import PathElement
from .pathelement import path_element_from_decoder
from .buffer import BufferDecodeError


def path_from_decoder(decoder):
    pairs = []
    while decoder:
        tt = decoder.get_var_int32()
        if tt == 11:
            pairs.append(path_element_from_decoder(decoder))
            continue

        if tt == 0:
            raise BufferDecodeError('corrupted')

    return Path(pairs=pairs)


class Path:

    def __init__(self, pairs):
        self._path = tuple(
            pe if isinstance(pe, PathElement) else PathElement(*pe)
            for pe in pairs)

    def encode(self, buffer):
        buffer.add_var_int32(114)
        buffer.add_var_int32(self.byte_size)

        for path_element in self._path:
            buffer.add_var_int32(11)
            path_element.encode(buffer)
            buffer.add_var_int32(12)

    def __getitem__(self, item):
        return self._path.__getitem__(item)

    def __repr__(self):
        return str(tuple((pe.kind, pe.id) for pe in self._path))

    def get_dict(self):
        return {'path': [pe.get_dict() for pe in self._path]}

    @property
    def byte_size(self):
        n = 2 * len(self._path)
        for path_element in self._path:
            n += path_element.byte_size
        return n
