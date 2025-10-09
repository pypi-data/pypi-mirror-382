import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "compressed-lists"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .partition import Partitioning
from .base import CompressedList
from .integer_list import CompressedIntegerList
from .string_list import CompressedStringList, CompressedCharacterList
from .bool_list import CompressedBooleanList
from .float_list import CompressedFloatList
from .numpy_list import CompressedNumpyList
from .biocframe_list import CompressedBiocFrameList
from .split_generic import splitAsCompressedList
