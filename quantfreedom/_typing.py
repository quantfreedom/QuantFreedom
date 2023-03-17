import numpy as np
from pandas import Series as pdSeries, DataFrame as pdFrame, Index as pdIndex
from polars import Series as plSeries, DataFrame as plFrame
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
RecordArray = np.ndarray
AnyArray = Union[Array, pdSeries, pdFrame, plFrame, plSeries]
AnyArray1d = Union[Array1d, pdSeries, plSeries]
AnyArray2d = Union[Array2d, pdFrame, plFrame]
_ArrayLike = Union[Scalar, Sequence[Scalar], Sequence[Sequence[Any]], SupportsArray]
ArrayLike = Union[_ArrayLike, Array, pdIndex, pdSeries, pdFrame, plSeries, plFrame]
