import dask.array as da
import numpy as np
from dask.array.utils import assert_eq

from fast_vindex import patched_vindex


def test_vindex_1d():
    arr = np.arange(9).reshape((9,))
    x = da.from_array(arr, chunks=(3,))
    indexes = (np.array([1, 2, 3]).reshape(1, 3),)

    with patched_vindex():
        result_fv = x.vindex[indexes]

    result = x.vindex[indexes]
    assert_eq(result_fv, result)


def test_vindex_2d():
    arr = np.arange(9 * 9).reshape((9, 9))
    x = da.from_array(arr, chunks=(3, 3))
    indexes = (
        np.array([1, 2, 3]).reshape(1, 3, 1),
        np.array([4, 5, 6]).reshape(1, 1, 3),
    )

    with patched_vindex():
        result_fv = x.vindex[indexes]

    result = x.vindex[indexes]
    assert_eq(result_fv, result)


def test_vindex_3d():
    arr = np.arange(9 * 9 * 9).reshape((9, 9, 9))
    x = da.from_array(arr, chunks=(3, 3, 3))
    indexes = (
        np.array([1, 2, 3]).reshape(1, 3, 1, 1),
        np.array([4, 5, 6]).reshape(1, 1, 3, 1),
        np.array([1, 2, 3]).reshape(1, 1, 1, 3),
    )

    with patched_vindex():
        result_fv = x.vindex[indexes]

    result = x.vindex[indexes]
    assert_eq(result_fv, result)


def test_vindex_4d():
    arr = np.arange(9 * 9 * 9 * 9).reshape((9, 9, 9, 9))
    x = da.from_array(arr, chunks=(3, 3, 3, 3))
    indexes = (
        np.array([1, 2, 3]).reshape(1, 3, 1, 1, 1),
        np.array([4, 5, 6]).reshape(1, 1, 3, 1, 1),
        np.array([1, 2, 3]).reshape(1, 1, 1, 3, 1),
        np.array([4, 5, 6]).reshape(1, 1, 1, 1, 3),
    )

    with patched_vindex():
        result_fv = x.vindex[indexes]

    result = x.vindex[indexes]
    assert_eq(result_fv, result)


def test_vindex_basic():
    """Official test from dask"""
    x = np.arange(56).reshape((7, 8))
    d = da.from_array(x, chunks=(3, 4))

    # cases where basic and advanced indexing coincide

    with patched_vindex():
        result = d.vindex[0]
    assert_eq(result, x[0])

    with patched_vindex():
        result = d.vindex[0, 1]
    assert_eq(result, x[0, 1])

    # Error
    # with patched_vindex():
    #    result = d.vindex[[0, 1], ::-1]  # slices last
    # assert_eq(result, x[:2, ::-1])


# def test_vindex_nd():
#     x = np.arange(56).reshape((7, 8))
#     d = da.from_array(x, chunks=(3, 4))

#     with patched_vindex():
#         result = d.vindex[[[0, 1], [6, 0]], [[0, 1], [0, 7]]]
#     assert_eq(result, x[[[0, 1], [6, 0]], [[0, 1], [0, 7]]])

#     #with patched_vindex():
#     result = d.vindex[np.arange(7)[:, None], np.arange(8)[None, :]]
#     assert_eq(result, x)

#     #with patched_vindex():
#     result = d.vindex[np.arange(7)[None, :], np.arange(8)[:, None]]
#     assert_eq(result, x.T)
