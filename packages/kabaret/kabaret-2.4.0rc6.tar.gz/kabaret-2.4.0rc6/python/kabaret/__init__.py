__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from . import _version
__version__ = _version.get_versions()['version']
