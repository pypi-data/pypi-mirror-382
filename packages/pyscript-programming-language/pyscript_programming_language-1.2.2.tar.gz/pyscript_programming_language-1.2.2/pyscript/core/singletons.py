from .bases import Pys

_singleton_objects = {}

class PysSingleton(Pys):
    pass

class UndefinedType(PysSingleton):

    __slots__ = ()

    def __new__(cls):
        if _singleton_objects.get('undefined', None) is None:
            _singleton_objects['undefined'] = super().__new__(cls)

        return _singleton_objects['undefined']

    def __repr__(self):
        return 'undefined'

    def __bool__(self):
        return False

class VersionInfo(PysSingleton, tuple):

    __slots__ = ()

    def __new__(cls):
        if _singleton_objects.get('version_info', None) is None:
            from .version import __version__
            _singleton_objects['version_info'] = super().__new__(cls, map(int, __version__.split('.')))

        return _singleton_objects['version_info']

    def __repr__(self):
        return 'VersionInfo(major={!r}, minor={!r}, micro={!r})'.format(
            self.major, self.minor, self.micro
        )

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1]

    @property
    def micro(self):
        return self[2]

class Hook(PysSingleton):

    __slots__ = ('display', 'exception')

    def __new__(cls):
        if _singleton_objects.get('hook', None) is None:
            _singleton_objects['hook'] = self = super().__new__(cls)

            self.display = None
            self.exception = None

        return _singleton_objects['hook']

undefined = UndefinedType()