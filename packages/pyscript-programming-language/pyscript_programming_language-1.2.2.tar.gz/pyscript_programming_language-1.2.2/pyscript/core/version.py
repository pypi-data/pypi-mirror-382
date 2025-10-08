from .singletons import VersionInfo

__version__ = '1.2.2'
__date__ = '7 October 2025, 21:00 UTC+7'

version = '{} ({})'.format(__version__, __date__)
version_info = VersionInfo()

del VersionInfo