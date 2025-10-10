from .config_loader import ConfigLoader
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pyconfiglite")
except PackageNotFoundError:
    __version__ = "0.0.0"
    __all__ = ["ConfigLoader"]
