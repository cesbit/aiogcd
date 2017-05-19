"""buffer.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import array


class BufferEncodeError(Exception):
    pass


class BufferDecodeError(Exception):
    pass


class Buffer(array.array):

    def __new__(cls, *args):
        return super().__new__(cls, 'B')

    def add_var_int32(self, val):
        if val & 127 == val:
            self.append(val)
            return

        if val >= 0x80000000 or val < -0x80000000:
            raise BufferEncodeError('int32 too big')

        if val < 0:
            val += 0x10000000000000000

        while True:
            bits = val & 127
            val >>= 7

            if val:
                bits |= 128

            self.append(bits)

            if not val:
                break

    def add_var_int64(self, val):
        if val >= 0x8000000000000000 or val < -0x8000000000000000:
            raise BufferEncodeError('int64 too big')

        if val < 0:
            val += 0x10000000000000000

        while True:
            bits = val & 127
            val >>= 7

            if val:
                bits |= 128

            self.append(bits)

            if not val:
                break

    def add_prefixed_string(self, val):
        assert isinstance(val, str), \
            'Expecting a str value but got {}'.format(type(val))
        self.add_var_int32(len(val))
        self.fromstring(val)
