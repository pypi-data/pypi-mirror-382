
"""
NSO1212v1 package
"""

from importlib.metadata import version, PackageNotFoundError

try:
  __version__ = version("NSO1212v1")
except PackageNotFoundError:
  __version__ = "0.0.0"

from .module import sectors, subsectors, tables, table, data

__all__ = ["sectors", "subsectors", "tables", "table", "data", "__version__"]
