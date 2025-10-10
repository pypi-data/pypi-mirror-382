from typing import Self
import numpy as np
import pandas as pd

from ._core import *
from .array import Array


class Matrix(Array):
    __slots__ = ("_rows", "_columns", "_values")

    def __init__(
        self, rows: np.ndarray, columns: np.ndarray, values: np.ndarray, validate=True
    ):
        super().__init__()

        if validate:
            self._rows = self._check_prepare_indices(rows, "rows")
            self._columns = self._check_prepare_indices(columns, "columns")
            self._values = self._check_prepare_values(values)
            if not (self._rows.shape == self._columns.shape == self._values.shape):
                raise TypeError("Rows, columns and values must have the same shape.")
            self._check_order(self._rows, self._columns)

        else:
            self._rows = rows
            self._rows.flags.writeable = False
            self._columns = columns
            self._columns.flags.writeable = False
            self._values = values

    @staticmethod
    def _check_order(rows, columns):
        if np.any(rows[1:] < rows[:-1]):
            raise TypeError("Row indices must be increasing.")

        if not np.all((rows[1:] > rows[:-1]) | (columns[1:] > columns[:-1])):
            raise TypeError("Column indices for a row must be increasing.")

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._columns

    @property
    def values(self):
        return self._values

    def __iadd__(self, other):
        if isinstance(other, Matrix):
            _add_inplace_2d(
                self._rows,
                self._columns,
                self._values,
                other._rows,
                other._columns,
                other._values,
            )
        elif np.isscalar(other):
            self._values += other
        else:
            raise TypeError(f"Cannot add Matrix and {str(type(other))}.")

        return self

    def __isub__(self, other):
        if isinstance(other, Matrix):
            _add_inplace_2d(
                self._rows,
                self._columns,
                self._values,
                other._rows,
                other._columns,
                -other._values,
            )
        elif np.isscalar(other):
            self._values -= other
        else:
            raise TypeError(f"Cannot subtract Matrix and {str(type(other))}.")

        return self

    def __copy__(self):
        return Matrix(
            self._rows.copy(order="C"),
            self._columns.copy(order="C"),
            self._values.copy(order="C"),
            validate=False,
        )

    def __add__(self, other):
        if isinstance(other, Matrix):
            result = self._copy_with_other_indices(other)
            result += other
        elif np.isscalar(other):
            result = self.__copy__()
            result._values += other
        else:
            raise TypeError(f"Cannot add Matrix and {str(type(other))}.")

        return result

    def __sub__(self, other):
        if isinstance(other, Matrix):
            result = self._copy_with_other_indices(other)
            result -= other
        elif np.isscalar(other):
            result = self.__copy__()
            result._values -= other
        else:
            raise TypeError(f"Cannot add Matrix and {str(type(other))}.")

        return result

    def _copy_with_other_indices(self, other):
        assert isinstance(other, Matrix)

        n = self._rows.shape[0] + other._rows.shape[0]
        rows = np.empty(n, dtype=np.uint32, order="c")
        columns = np.empty(n, dtype=np.uint32, order="c")
        values = np.empty(n, dtype=np.double, order="c")
        n = _intersect_indices_2d(
            rows,
            columns,
            values,
            self._rows,
            self._columns,
            self._values,
            other._rows,
            other._columns,
            strict=False,
        )
        rows.resize((n,), refcheck=False)
        columns.resize((n,), refcheck=False)
        values.resize((n,), refcheck=False)

        return Matrix(rows, columns, values, validate=False)

    def split(self, value=0.0):
        return (
            Matrix(
                self._rows.copy(),
                self._columns.copy(),
                np.minimum(self._values, value),
                validate=False,
            ),
            Matrix(
                self._rows.copy(),
                self._columns.copy(),
                np.maximum(self._values, value),
                validate=False,
            ),
        )

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError(f"Cannot compare Matrix with {str(type(other))}.")
        return (
            np.array_equal(self._rows, other._rows)
            and np.array_equal(self._columns, other._columns)
            and np.array_equal(self._values, other._values)
        )

    @classmethod
    def from_dataframe(
        cls, df: pd.DataFrame, values: str, rows: str, columns: str, prune: bool = False
    ) -> Self:
        values = df[values].to_numpy(dtype=np.double, copy=False)
        rows = df[rows].to_numpy(dtype=np.uint32, copy=False)
        columns = df[columns].to_numpy(dtype=np.uint32, copy=False)

        if prune:
            nonzero = values != 0
            return Matrix(
                values=values[nonzero].copy(),
                rows=rows[nonzero],
                columns=columns[nonzero],
            )
        else:
            return Matrix(values=values.copy(), rows=rows, columns=columns)

    # noinspection PyArgumentList
    def to_dense(self, m: int = None, n: int = None):
        if m is None:
            m = self._rows.max() + 1
        elif m <= self._rows.max():
            raise TypeError(f"Row indices exceed `m`.")

        if n is None:
            n = self._columns.max() + 1
        elif n <= self._columns.max():
            raise TypeError(f"Column indices exceed `n`.")

        result = np.zeros((m, n), dtype=np.double, order="c")

        _to_dense_matrix(
            result_values=result,
            rows=self._rows,
            columns=self._columns,
            values=self._values,
        )

        return result

    def transpose(self):
        order = np.argsort(self._columns)
        return Matrix(
            rows=self._columns[order],
            columns=self._rows[order],
            values=self._values[order],
            validate=False,
        )

    def __pow__(self, power, modulo=None):
        if np.isscalar(power):
            nz = self._values != 0

            values = np.power(self._values[nz], power, order="c")
            if modulo:
                values = np.mod(values, modulo, order="c")

            return Matrix(
                rows=self._rows[nz],
                columns=self._columns[nz],
                values=values,
                validate=False,
            )

        else:
            raise TypeError(
                f"Cannot raise Matrix to the power of type `{type(power)}`."
            )

    def __repr__(self):
        return f"Matrix(rows={repr(self._rows)}, columns={repr(self._columns)}, values={repr(self._values)})"

    def __len__(self):
        return self._rows.shape[0]

    def conform_indices(self, other: Self, strict=False):
        if not isinstance(other, Matrix):
            raise TypeError(f"Can only conform to indices of other Matrix.")

        if strict:
            m = other._values.shape[0]
        else:
            m = self._values.shape[0] + other._values.shape[0]

        rows = np.empty((m,), dtype=np.uint32, order="c")
        columns = np.empty((m,), dtype=np.uint32, order="c")
        values = np.empty((m,), dtype=np.double, order="c")

        n = _intersect_indices_2d(
            result_rows=rows,
            result_columns=columns,
            result_values=values,
            self_rows=self._rows,
            self_columns=self._columns,
            self_values=self._values,
            other_rows=other._rows,
            other_columns=other._columns,
            strict=strict,
        )

        if strict:
            assert m == n
        else:
            rows.resize((n,), refcheck=False)
            columns.resize((n,), refcheck=False)
            values.resize((n,), refcheck=False)

        return Matrix(rows=rows, columns=columns, values=values, validate=False)

    @property
    def mutable(self) -> bool:
        return self._values.flags.writeable

    @mutable.setter
    def mutable(self, value: bool):
        self._values.flags.writeable = value
