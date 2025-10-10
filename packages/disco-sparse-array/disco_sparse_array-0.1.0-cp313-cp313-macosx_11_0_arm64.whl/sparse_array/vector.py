from typing import Self
import numpy as np
import pandas as pd

from ._core import (
    _add_inplace,
    _intersect_indices,
    _dotproduct_vm,
    _changes,
    _to_dense_vector,
)
from .array import Array
from .matrix import Matrix


class Vector(Array):
    __slots__ = ("_indices", "_values")

    def __init__(self, indices: np.ndarray, values: np.ndarray, validate=True):
        super().__init__()

        if validate:
            self._indices = self._check_prepare_indices(indices, "indices")
            self._values = self._check_prepare_values(values)
            if self._indices.shape != self._values.shape:
                raise TypeError("Indices and values must have the same shape.")
            self._check_order(self._indices)

        else:
            self._indices = indices
            self._indices.flags.writeable = False
            self._values = values

    @staticmethod
    def _check_order(indices):
        if not np.all(indices[1:] > indices[:-1]):
            raise TypeError(f"Indices must be strictly increasing.")

    @property
    def indices(self):
        return self._indices

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, v):
        v = self._check_prepare_values(v)
        if self._indices.shape != v.shape:
            raise TypeError("Values must have the same shape.")
        self._values = v

    def __iadd__(self, other):
        if not self._values.flags.writeable:
            raise PermissionError("Vector is made read-only.")

        if isinstance(other, Vector):
            _add_inplace(self._indices, self._values, other._indices, other._values)
        elif isinstance(other, np.ndarray):
            if other.dtype == np.double and other.shape == self._values.shape:
                self._values += other
            else:
                raise TypeError(
                    "When adding an array to a Vector, it must have dtype `double` and same size."
                )
        elif np.isscalar(other):
            self._values += other
        else:
            raise TypeError(f"Cannot add Vector and {str(type(other))}.")

        return self

    def __isub__(self, other):
        if not self._values.flags.writeable:
            raise PermissionError("Vector is made read-only.")

        if isinstance(other, Vector):
            _add_inplace(self._indices, self._values, other._indices, -other._values)
        elif isinstance(other, np.ndarray):
            if other.dtype == np.double and other.shape == self._values.shape:
                self._values -= other
            else:
                raise TypeError(
                    "When subtracting an array from a Vector, it must have dtype `double` and same size."
                )
        elif np.isscalar(other):
            self._values -= other
        else:
            raise TypeError(f"Cannot subtract Vector and {str(type(other))}.")

        return self

    def __copy__(self):
        return Vector(
            self._indices.copy(order="C"), self._values.copy(order="C"), validate=False
        )

    def __add__(self, other):
        if isinstance(other, Vector):
            result = self._copy_with_other_indices(other)
            result += other
        elif isinstance(other, np.ndarray):
            if other.dtype == np.double and other.shape == self._values.shape:
                result = self.__copy__()
                result._values += other
            else:
                raise TypeError(
                    "When adding an array to a Vector, it must have dtype `double` and same size."
                )
        elif np.isscalar(other):
            result = self.__copy__()
            result._values += other
        else:
            raise TypeError(f"Cannot add Vector and {str(type(other))}.")

        return result

    def __sub__(self, other):
        if isinstance(other, Vector):
            result = self._copy_with_other_indices(other)
            result -= other
        elif isinstance(other, np.ndarray):
            if other.dtype == np.double and other.shape == self._values.shape:
                result = self.__copy__()
                result._values -= other
            else:
                raise TypeError(
                    "When subtracting an array from a Vector, it must have dtype `double` and same size."
                )
        elif np.isscalar(other):
            result = self.__copy__()
            result._values -= other
        else:
            raise TypeError(f"Cannot add Vector and {str(type(other))}.")

        return result

    def _copy_with_other_indices(self, other):
        assert isinstance(other, Vector)

        n = self._indices.shape[0] + other._indices.shape[0]
        indices = np.empty(n, dtype=np.uint32, order="c")
        values = np.empty(n, dtype=np.double, order="c")
        n = _intersect_indices(
            indices, values, self._indices, self._values, other._indices, strict=False
        )
        indices.resize((n,), refcheck=False)
        values.resize((n,), refcheck=False)

        return Vector(indices, values, validate=False)

    def split(self, value=0.0):
        return self.upper_cap(value=value), self.lower_cap(value=value)

    def conform_indices(self, other: Self | np.ndarray | list, strict=False):
        """
        Returns a Vector with the combined indices of self and other, and the values of self. For indices only in other,
        value is set to 0.
        If strict is True, drops the indices in self that are not in other (intersection). Result shape must be other
        shape.
        If strict is False, just ensures that other indices are present but keeps all own indices (union). Result shape
        must be the sum of self and other shapes.
        Returns the number of indices in the result.
        other shape.
        :param other:
        :param strict:
        :return:
        """

        if isinstance(other, Vector):
            other = other._indices
        elif isinstance(other, list):
            other = np.array(other, dtype=np.uint32, order="c")

        if strict:
            m = other.shape[0]
        else:
            m = self._values.shape[0] + other.shape[0]

        indices = np.empty((m,), dtype=np.uint32, order="c")
        values = np.empty((m,), dtype=np.double, order="c")

        n = _intersect_indices(
            result_indices=indices,
            result_values=values,
            self_indices=self._indices,
            self_values=self._values,
            other_indices=other,
            strict=strict,
        )
        if strict:
            assert m == n
        else:
            indices.resize((n,), refcheck=False)
            values.resize((n,), refcheck=False)

        # if n != other.shape[0] and strict:
        #     keep = np.isin(indices, other)
        #     return Vector(indices=indices[keep], values=values[keep], validate=False)
        # else:
        #     return Vector(indices=indices, values=values, validate=False)
        return Vector(indices=indices, values=values, validate=False)

    def upper_cap(self, value: float | Self = 0.0):
        if isinstance(value, Vector):
            result = self.conform_indices(value, strict=True)
            result._values = np.minimum(result._values, value._values)
            return result
        else:
            return Vector(
                self._indices.copy(), np.minimum(self._values, value), validate=False
            )

    def lower_cap(self, value=0.0):
        if isinstance(value, Vector):
            result = self.conform_indices(value, strict=True)
            result._values = np.maximum(result._values, value._values)
            return result
        else:
            return Vector(
                self._indices.copy(), np.maximum(self._values, value), validate=False
            )

    def nz(self, precision: float = 1e-6):
        nonzero = (self._values > precision) | (self._values < -precision)
        return Vector(
            indices=self._indices[nonzero],
            values=self._values[nonzero].copy(order="C"),
            validate=False,
        )

    def __eq__(self, other):
        if isinstance(other, Vector):
            return np.array_equal(self._indices, other._indices) and np.array_equal(
                self._values, other._values
            )

    def __matmul__(self, other):
        if isinstance(other, Matrix):
            result_indices = np.sort(np.unique(other.columns))
            result_values = np.zeros(
                result_indices.shape[0], dtype=np.double, order="c"
            )

            if (
                self._indices.shape[0] == 0
                or other.rows.shape[0] == 0
                or other.columns.shape[0] == 0
            ):
                return Vector.null()

            _dotproduct_vm(
                result_indices,
                result_values,
                self._indices,
                self._values,
                other.rows,
                other.columns,
                other.values,
            )

            non_zero = result_values != 0

            return Vector(result_indices[non_zero], result_values[non_zero])

    @staticmethod
    def null():
        return Vector(
            indices=np.empty((0,), dtype=np.uint32),
            values=np.empty((0,), dtype=np.double),
            validate=False,
        )

    def __mul__(self, other):
        if isinstance(other, Vector):
            result_indices = np.empty(
                self._indices.shape[0] + other._indices.shape[0], dtype=np.uint32
            )
            result_values = np.empty(
                self._indices.shape[0] + other._indices.shape[0], dtype=np.double
            )
            n = _intersect_indices(
                result_indices=result_indices,
                result_values=result_values,
                self_indices=self._indices,
                self_values=self._values,
                other_indices=other._indices,
                strict=False,
            )
            result_indices = result_indices.resize((n,), refcheck=False)
            result_values = result_values.resize((n,), refcheck=False)

            # noinspection PyTypeChecker
            return Vector(indices=result_indices, values=result_values, validate=False)

        elif np.isscalar(other):
            return Vector(
                indices=self._indices, values=self._values * other, validate=False
            )

        else:
            raise TypeError(f"Cannot multiply Vector with `{type(other)}`.")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __repr__(self):
        return f"Vector(indices={repr(self._indices)}, values={repr(self._values)})"

    def update(self, other) -> None:
        """
        Update values in vector with values given in other. Indices not in other are not updated.
        Other's indices must be a subset of self's.
        :param other:
        :return:
        """
        self.diff(other, update=True)

    def diff(self, other: Self, update: bool = False, precision: float = 1e-6) -> Self:
        """
        Return values in other that are different from self.
        Other's indices must be a subset of self's.
        :param other:
        :param update:
        :param precision:
        :return:
        """

        indices = np.empty(shape=self._indices.shape, dtype=np.uint32, order="c")
        values = np.empty_like(indices, dtype=np.double)

        n = _changes(
            indices,
            values,
            self._indices,
            self._values,
            other._indices,
            other._values,
            update=update,
            precision=precision,
        )

        indices.resize((n,), refcheck=False)
        values.resize((n,), refcheck=False)

        return Vector(indices=indices, values=values, validate=False)

    @classmethod
    def from_dataframe(
        cls, df: pd.DataFrame, values: str, indices: str, prune: bool = False
    ) -> Self:
        values = df[values].fillna(0.0).to_numpy(dtype=np.double, copy=False)
        indices = df[indices].to_numpy(dtype=np.uint32, copy=False)

        sorting = np.argsort(indices)
        indices = indices[sorting]
        values = values[sorting]

        if prune:
            nonzero = values != 0
            return Vector(values=values[nonzero].copy(), indices=indices[nonzero])
        else:
            return Vector(values=values.copy(), indices=indices)

    @classmethod
    def zeros(cls, indices: np.ndarray):
        values = np.zeros_like(indices, dtype=np.double)
        return Vector(indices, values)

    # noinspection PyArgumentList
    def to_dense(self, m: int = None):
        if m is None:
            m = self._indices.max() + 1
        elif m <= self._indices.max():
            raise TypeError(f"Indices exceed `m`.")

        result = np.zeros((m,), dtype=np.double, order="c")

        _to_dense_vector(
            result_values=result, indices=self._indices, values=self._values
        )

        return result

    def __pow__(self, power, modulo=None):
        if np.isscalar(power):
            values = np.power(self._values, power, order="c")
            if modulo:
                values = np.mod(values, modulo, order="c")

            return Vector(indices=self._indices, values=values, validate=False)

        else:
            raise TypeError(
                f"Cannot raise Matrix to the power of type `{type(power)}`."
            )

    def __len__(self):
        return self._indices.shape[0]

    # noinspection PyArgumentList
    def __getitem__(self, item):
        if isinstance(item, int):
            indices = np.flatnonzero(self._indices == item)
        else:
            # item is anything that can be converted to indices
            candidates = np.arange(self._indices.max() + 1, dtype=np.uint32)[item]
            # indices = np.isin(self._indices, candidates, assume_unique=True)

            # next we take the cross-section of own indices with the candidates
            indices = Vector.ind_isin(self._indices, candidates)

        return self._values[indices]

    def minmult(self, minimum: Self | np.ndarray, multiple: Self | np.ndarray) -> Self:
        if isinstance(minimum, Vector):
            minimum = minimum.conform_indices(self, strict=True)
            minimum = minimum.values
        elif not (
            isinstance(minimum, np.ndarray) and minimum.shape == self._values.shape
        ):
            raise TypeError(f"`minimum` must be a Vector or an array with same shape.")

        if isinstance(multiple, Vector):
            multiple = multiple.conform_indices(self, strict=True)
            multiple = multiple.values
        elif not (
            isinstance(multiple, np.ndarray) and multiple.shape == self._values.shape
        ):
            raise TypeError(f"`multiple` must be a Vector or an array with same shape.")

        return Vector(
            indices=self._indices,
            values=self._minmult(self._values, minimum, multiple),
            validate=False,
        )

    @property
    def mutable(self) -> bool:
        return self._values.flags.writeable

    @mutable.setter
    def mutable(self, value: bool):
        self._values.flags.writeable = value
