import contextlib

import dask.array as da

from fast_vindex.array.core import _vindex


@contextlib.contextmanager
def patched_vindex():
    original = da.core._vindex
    da.core._vindex = _vindex
    try:
        yield
    finally:
        da.core._vindex = original
