"""decoder.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import base64
from .buffer import Buffer
from .buffer import BufferDecodeError


class Decoder(Buffer):

    _idx = None
    _end = None

    def __new__(cls, *args, ks=None):
        assert ks is not None, \
            'Key string is required, for example: Decoder(ks=<ket_string>)'

        decoder = super().__new__(cls)

        if isinstance(ks, str):
            ks = ks.encode('utf8')

        ks += b'=' * (4 - len(ks) % 4)
        ks = base64.b64decode(ks.replace(b'-', b'+').replace(b'_', b'/'))
        decoder.fromstring(ks)
        decoder._idx = 0
        decoder.set_end()
        return decoder

    def set_end(self, end=None):
        """Set a new _end relative to the current index or restore the original
        _end if no end is given."""
        self._end = len(self) if end is None else self._idx + end

    def __bool__(self):
        return self._idx < self._end

    def _get8(self):
        if not self:
            raise BufferDecodeError('truncated')
        c = self[self._idx]
        self._idx += 1
        return c

    def get_var_int32(self):
        b = self._get8()

        if not (b & 128):
            return b

        result = 0
        shift = 0

        while True:
            result |= ((b & 127) << shift)
            shift += 7

            if not (b & 128):
                if result >= 0x10000000000000000:
                    raise BufferDecodeError('corrupted')
                break

            if shift >= 64:
                raise BufferDecodeError('corrupted')

            b = self._get8()

        if result >= 0x8000000000000000:
            result -= 0x10000000000000000

        if result >= 0x80000000 or result < -0x80000000:
            raise BufferDecodeError('corrupted')

        return result

    def get_var_int64(self):
        result = 0
        shift = 0
        while True:
            if shift >= 64:
                raise BufferDecodeError('corrupted')

            b = self._get8()
            result |= (b & 127) << shift
            shift += 7

            if not (b & 128):
                if result >= 1 << 64:
                    raise BufferDecodeError('corrupted')

                break

        if result >= 1 << 63:
            result -= 1 << 64

        return result

    def get_prefixed_string(self):
        l = self.get_var_int32()
        if self._idx + l > len(self):
            raise BufferDecodeError('truncated')
        r = self[self._idx: self._idx + l]
        self._idx += l
        return r.tostring().decode('utf-8')
