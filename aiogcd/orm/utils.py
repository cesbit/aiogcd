"""utils.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""


class ProtectedList(list):

    def __init__(
            self,
            *args,
            protect=True):
        self._protect = protect
        super().__init__(*args)

    def __setitem__(self, key, value):
        if self._protect is True:
            raise TypeError('This list is protected.')
        elif callable(self._protect):
            self._protect(value)
        super().__setitem__(key, value)

    def append(self, p_object):
        if self._protect is True:
            raise TypeError('This list is protected.')
        elif callable(self._protect):
            self._protect(p_object)
        super().append(p_object)

    def extend(self, iterable):
        if self._protect is True:
            raise TypeError('This list is protected.')
        elif callable(self._protect):
            values = []
            for value in iterable:
                self._protect(value)
                values.append(value)
            iterable = iter(values)

        super().extend(iterable)

    def pop(self, index=None):
        if self._protect is True:
            raise TypeError('This list is protected.')
        return super().pop(index)

    def clear(self):
        if self._protect is True:
            raise TypeError('This list is protected.')
        return super().clear()

    def insert(self, index, p_object):
        if self._protect is True:
            raise TypeError('This list is protected.')
        elif callable(self._protect):
            self._protect(p_object)
        super().insert(index, p_object)

    def remove(self, value):
        if self._protect is True:
            raise TypeError('This list is protected.')
        return super().remove(value)

    def reverse(self):
        if self._protect is True:
            raise TypeError('This list is protected.')
        return super().reverse()

    def __add__(self, other):
        self.extend(other)
        return self

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __delitem__(self, key):
        if self._protect is True:
            raise TypeError('This list is protected.')
        return super().__delitem__(key)


if __name__ == '__main__':
    def check_int(val):
        if not isinstance(val, int):
            raise TypeError('Only integers are allowed.')

    l = [1, 2, 3]
    p = ProtectedList(l, protect=check_int) + [3]
    p.append(5)
    p.extend([6])
    p += [7]
    print(p)

    r = ProtectedList(l)
    del r[2]