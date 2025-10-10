from .array import Array
from .vector import Vector
from .matrix import Matrix

# Expose package version (set via setuptools-scm write_to)
try:
    from ._version import version as __version__
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

# Public API: classes only
__all__ = ["Array", "Vector", "Matrix", "__version__"]
