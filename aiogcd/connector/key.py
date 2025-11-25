"""key.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@cesbit.com>
"""
import base64
from .buffer import Buffer
from .buffer import BufferDecodeError
from .path import Path
from .path import path_from_decoder
from .decoder import Decoder


class Key:
    KEY_INIT_MSG = """
        Key can be initialized by using a dictionary, for example:

            Key({
                "partitionId": {
                    "projectId": "my-project-id",
                    "namespaceId": "my-optional-namespace"
                },
                "path": [{
                  "kind": "Foo",
                  "id": "12345678"
                }]
            })

        Or by using a key string, for example:

            Key(ks="ag9zfm15LXByb2plY3QtaWRyDAsSA0ZvbxjOwvEFDA")

        Or, you can use arguments and set a project_id, for example:

            Key("Foo", 12345678, ..., project_id="my-project-id")

        Or you can use keyword arguments path and project_id, for example:

            Key(path=Path(...), project_id="my-project-id")
"""
    _ks = None
    path: Path

    def __init__(self, *args, ks: str | None = None,
                 path: Path | None = None,
                 project_id: str | None = None,
                 namespace_id: str | None = None):
        if len(args) == 1 and isinstance(args[0], dict):
            assert ks is None and path is None and project_id is None, \
                self.KEY_INIT_MSG

            res = args[0]
            partitionId = res['partitionId']
            self.project_id = partitionId['projectId']
            self.namespace_id = partitionId.get('namespaceId')
            self.path = Path(pairs=tuple(
                (pair['kind'], self._extract_id_or_name(pair))
                for pair in res['path']
            ))
            return

        if ks is not None:
            assert (not args) and path is None and project_id is None, \
                self.KEY_INIT_MSG
            self.project_id, self.namespace_id, self.path = \
                self._deserialize_ks(ks)
            return

        assert project_id is not None and ((not args) ^ (path is None)), \
            self.KEY_INIT_MSG

        assert len(args) % 2 == 0, self.KEY_INIT_MSG

        self.namespace_id = namespace_id  # namespace_id might be None
        self.project_id = project_id
        self.path = Path(pairs=zip(*[iter(args)]*2)) if path is None else path

    def get_path(self):
        return self.path.get_as_tuple()

    def __repr__(self):
        return self.path.__repr__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.ks == other.ks
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def encode(self):
        """Return a Buffer() object which is a byte-like object.

        For serializing the key object you can use the .ks property which uses
        this method for generating an urlsafe key string.
        """
        buffer = Buffer()
        buffer.add_var_int32(106)  # type: ignore

        # The project id in a key string is prefixed with s~
        buffer.add_prefixed_string(  # type: ignore
            's~{}'.format(self.project_id))

        self.path.encode(buffer)

        if self.namespace_id:
            buffer.add_var_int32(162)  # type: ignore
            buffer.add_prefixed_string(self.namespace_id)  # type: ignore

        return buffer

    @property
    def ks(self):
        if self._ks is None:
            self._ks = base64.b64encode(self.encode()) \
                    .rstrip(b'=') \
                    .replace(b'+', b'-') \
                    .replace(b'/', b'_') \
                    .decode('utf-8')
        return self._ks

    def get_dict(self):
        d = {'partitionId': {'projectId': self.project_id}}

        if self.namespace_id:
            d['partitionId']['namespaceId'] = self.namespace_id

        d.update(self.path.get_dict())
        return d

    @property
    def kind(self) -> str:
        """Shortcut for .path[-1].kind"""
        return self.path[-1].kind

    @property
    def id(self) -> int | str:
        """Shortcut for .path[-1].id"""
        return self.path[-1].id

    @staticmethod
    def _extract_id_or_name(pair) -> int | str:
        """Used on __init__."""
        if 'id' in pair:
            return int(pair['id'])

        if 'name' in pair:
            return pair['name']

        return ''

    @staticmethod
    def _deserialize_ks(ks: str) -> tuple[str | None, str | None, Path]:
        """Returns a tuple with the project_id, namespace_id and Path
        from a key string."""

        decoder = Decoder(ks=ks)
        project_id: str | None = None
        namespace_id: str | None = None
        path: Path | None = None

        while decoder:
            tt = decoder.get_var_int32()  # type: ignore

            if tt == 106:
                # The project id in a key string is prefixed with s~ which is
                # not part of the real project id.
                project_id = decoder.get_prefixed_string()[2:]  # type: ignore
                continue

            if tt == 114:
                sz = decoder.get_var_int32()  # type: ignore
                decoder.set_end(sz)  # type: ignore
                path = path_from_decoder(decoder)
                decoder.set_end()  # type: ignore
                continue

            if tt == 162:
                namespace_id = decoder.get_prefixed_string()  # type: ignore
                continue

            if tt == 0:
                raise BufferDecodeError('corrupt')

        assert path
        return project_id, namespace_id, path

    def get_parent(self):
        parent_pairs = self.path.get_as_tuple()[:-1]
        parent_path = Path(pairs=parent_pairs)
        return Key(path=parent_path, project_id=self.project_id)
