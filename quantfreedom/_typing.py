import numpy as np
from pandas import Series, DataFrame as Frame, Index
from typing import *

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

Scalar = Union[str, float, int, complex, bool, object, np.generic]

class SupportsArray(Protocol):
    def __array__(self) -> np.ndarray: ...

Array = np.ndarray  # ready to be used for n-dim data
Array1d = np.ndarray
Array2d = np.ndarray
Array3d = np.ndarray
Record = np.void
RecordArray = np.ndarray
RecArray = np.recarray
AnyArray = Union[Array, Series, Frame]
AnyArray1d = Union[Array1d, Series]
AnyArray2d = Union[Array2d, Frame]
_ArrayLike = Union[Scalar, Sequence[Scalar], Sequence[Sequence[Any]], SupportsArray]
ArrayLike = Union[_ArrayLike, Array, Index, Series, Frame]
