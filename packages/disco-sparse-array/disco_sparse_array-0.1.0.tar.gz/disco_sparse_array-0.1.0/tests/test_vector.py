import numpy as np
import pytest

from sparse_array import Vector
from sparse_array import Matrix


def test_vector_iadd_vector():
    a = Vector(np.array([1, 2, 3], dtype=np.uint32), np.array([1., 2., 3.], dtype=np.double))
    b = Vector(np.array([1, 3], dtype=np.uint32), np.array([1., 3.], dtype=np.double))

    a += b

    assert np.array_equal(a.values, np.array([2., 2., 6.], dtype=np.double))


def test_vector_iadd_scalar():
    a = Vector(np.array([1, 2, 3], dtype=np.uint32), np.array([1., 2., 3.], dtype=np.double))
    a += 1

    assert np.array_equal(a.values, np.array([2., 3., 4.], dtype=np.double))


def test_vector_isub_vector():
    a = Vector(np.array([1, 2, 3], dtype=np.uint32), np.array([2., 2., 6.], dtype=np.double))
    b = Vector(np.array([1, 3], dtype=np.uint32), np.array([1., 3.], dtype=np.double))

    a -= b

    assert np.array_equal(a.values, np.array([1., 2., 3.], dtype=np.double))


def test_vector_add_vector_subset():
    a = Vector(np.array([1, 2, 3], dtype=np.uint32), np.array([1., 2., 3.], dtype=np.double))
    b = Vector(np.array([1, 3], dtype=np.uint32), np.array([1., 3.], dtype=np.double))

    c = a + b

    assert np.array_equal(c.values, np.array([2., 2., 6.], dtype=np.double))
    assert np.array_equal(a.values, np.array([1., 2., 3.], dtype=np.double))


def test_vector_add_vector_intersect():
    a = Vector(np.array([1, 2, 3], dtype=np.uint32), np.array([1., 2., 3.], dtype=np.double))
    b = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([1., 1., 1., 1.], dtype=np.double))

    c = a + b

    assert np.array_equal(c.values, np.array([1., 3., 4., 1., 1.], dtype=np.double))
    assert np.array_equal(c.indices, np.array([1, 2, 3, 4, 5], dtype=np.double))


def test_split():
    a = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([1., -1., 1., 0.], dtype=np.double))
    x, y = a.split()

    assert x == Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([0., -1., 0., 0.], dtype=np.double))
    assert y == Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([1., 0., 1., 0.], dtype=np.double))


def test_dot_product_vm():
    v = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([2., 3., 4., 5.], dtype=np.double))
    m = Matrix(np.arange(10, dtype=np.uint32),
               np.array([5, 5, 4, 4, 3, 3, 2, 2, 1, 1], dtype=np.uint32, order='c'),
               np.ones(10, dtype=np.double, order='c'))

    test = Vector(np.array([3, 4], dtype=np.uint32),
                  np.array([9., 5.], dtype=np.double))

    result = v @ m
    assert np.array_equal(test.indices, result.indices)
    assert np.array_equal(test.values, result.values)

    assert result == test


def test_diff():
    a = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([1., 1., 1., 1.], dtype=np.double))
    b = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))

    test = Vector(np.array([2, 3], dtype=np.uint32), np.array([3., 2.], dtype=np.double))

    result = a.diff(b)

    assert result == test


def test_update():
    a = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([1., 1., 1., 1.], dtype=np.double))
    b = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))

    test = Vector(np.array([2, 3, 4, 5], dtype=np.uint32), np.array([3., 2., 1., 1.], dtype=np.double))

    a.update(b)

    assert a == test


def test_add_array():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))
    b = np.array([1., 2., 3.], dtype=np.double)

    test = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([4., 4., 4.], dtype=np.double))

    c = a + b

    assert c == test


def test_subtract_array():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))
    b = np.array([1., 2., 3.], dtype=np.double)

    test = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([2., 0., -2.], dtype=np.double))

    c = a - b

    assert c == test


def test_iadd_array():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))
    b = np.array([1., 2., 3.], dtype=np.double)

    test = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([4., 4., 4.], dtype=np.double))

    a += b

    assert a == test


def test_isub_array():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))
    b = np.array([1., 2., 3.], dtype=np.double)

    test = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([2., 0., -2.], dtype=np.double))

    a -= b

    assert a == test


def test_minmult_array():
    a = Vector(indices=[1, 2, 3], values=[10, 12, 14])
    minimum = np.array([4, 0, 0])
    multiple = np.array([0, 5, 10])

    test = Vector(indices=[1, 2, 3], values=[10, 15, 20])
    result = a.minmult(minimum, multiple)

    assert result == test


def test_minmult_vector():
    a = Vector(indices=[1, 2, 3], values=[10, 12, 14])
    minimum = Vector(indices=[1], values=[4])
    multiple = Vector(indices=[2, 3], values=[5, 10])

    test = Vector(indices=[1, 2, 3], values=[10, 15, 20])
    result = a.minmult(minimum, multiple)

    assert result == test


def test_minmult_vector_0():
    a = Vector(indices=[1, 2, 3], values=[0, 0, 14])
    minimum = Vector(indices=[1], values=[4])
    multiple = Vector(indices=[2, 3], values=[5, 10])

    test = Vector(indices=[1, 2, 3], values=[0, 0, 20])
    result = a.minmult(minimum, multiple)

    assert result == test


def test_setter():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))

    a.values = np.array([3, 2, 1])

    assert np.array_equal(a.values, np.array([3., 2., 1.], dtype=np.double))


def test_setter_fail():
    a = Vector(np.array([2, 3, 5], dtype=np.uint32), np.array([3., 2., 1.], dtype=np.double))

    with pytest.raises(TypeError):
        a.values = np.array([4, 3, 2, 1])
