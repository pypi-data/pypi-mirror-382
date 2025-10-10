from abc import ABC, abstractmethod
from typing import Self
import numpy as np
from ._core import _isin


INDEX_TYPE = np.uint32
VALUE_TYPE = np.double


class Array(ABC):
    @staticmethod
    def _check_prepare_indices(indices: np.ndarray, dimension: str) -> np.ndarray:
        indices = np.ascontiguousarray(indices, dtype=np.uint32)

        if indices.ndim != 1:
            raise TypeError(
                f"Expected {dimension} with single dimension. Got {indices.ndim} dimensions."
            )

        indices.flags.writeable = False

        return indices

    @staticmethod
    def _check_prepare_values(values: np.ndarray) -> np.ndarray:
        values = np.ascontiguousarray(values, dtype=np.double)

        if not values.flags.writeable:
            values = values.copy()

        if values.ndim != 1:
            raise TypeError(
                f"Expected values with single dimension. Got {values.ndim} dimensions."
            )

        return values

    @abstractmethod
    def __copy__(self) -> Self:
        ...

    def copy(self) -> Self:
        return self.__copy__()

    @abstractmethod
    def __len__(self):
        ...

    @staticmethod
    def _minmult(a: np.ndarray, amin: np.ndarray, amult: np.ndarray) -> np.ndarray:
        assert a.shape == amin.shape == amult.shape

        nz = a > 0
        c = np.zeros_like(a)
        c[nz] = np.maximum(a[nz], amin[nz])

        hasmult = (amult > 0) & nz
        m, r = np.divmod(a[hasmult], amult[hasmult])
        c[hasmult] = m * amult[hasmult] + (r > 0) * amult[hasmult]

        return c

    @staticmethod
    def ind_isin(
        indices: np.ndarray, test_indices: np.ndarray, validate: bool = True
    ) -> np.ndarray:
        if validate:
            indices = Array._check_prepare_indices(indices, "indices")
            test_indices = Array._check_prepare_indices(test_indices, "test_indices")

        result = np.empty(indices.shape, dtype=np.bool_)

        _isin(result, indices, test_indices)

        return result

    @property
    @abstractmethod
    def mutable(self) -> bool:
        ...
