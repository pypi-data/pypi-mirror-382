# pip install kiarina-utils-common
from importlib.metadata import version

from ._parse_config_string import parse_config_string

__version__ = version("kiarina-utils-common")

__all__ = [
    "parse_config_string",
]
