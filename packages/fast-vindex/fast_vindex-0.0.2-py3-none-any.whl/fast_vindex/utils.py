import logging
from itertools import product
from pathlib import Path
from typing import Literal, Optional

import dask.array as da
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


def generate_dask_datacube_from_random(shape, chunks):
    """Générer un dask datacube à partir de valeur aléatoire"""
    return da.random.random(shape, chunks=chunks)


def generate_dask_datacube_from_indices(shape, chunks):
    """Générer un dask datacube avec les valeurs des index"""
    # Création d'un numpy array vide
    narray = np.empty((shape), dtype=object)

    # Remplissage de l'array avec les valeurs de ces indices
    # (Ex: narray[3, 4, 2] = (3, 4, 2)
    for indices in product(*(range(s) for s in shape)):
        narray[indices] = indices

    # Création d'un dask array à partir du numpy array
    darray = da.from_array(narray, chunks=chunks)
    return darray


def generate_dataset(n, shape, buffers):
    """Générer un Dataset de point d'observation (entier et non nombre décimaux)"""
    obj = xr.Dataset()
    obs = np.arange(n)
    obj["obs"] = ("obs", obs)
    for i, (size, buffer) in enumerate(zip(shape, buffers)):
        dim = f"x{i}"
        value = np.random.randint(buffer, size - (buffer + 1), n)
        obj[dim] = ("obs", value)

    return obj


def func_array(values, **kwargs):
    """
    Generates an array of ranges centered around each value with a
    specified buffer.
    """
    return np.array(
        [
            np.arange(value - kwargs["buffer"], value + kwargs["buffer"] + 1)
            for value in values
        ]
    )


def _array(dataarray: xr.DataArray, output_core_dims: str, buffer: dict[str, int]):
    """
    Generates an array of ranges centered around each value with a
    specified buffer.
    """
    return xr.apply_ufunc(
        func_array,
        dataarray,
        input_core_dims=[[]],
        output_core_dims=[[output_core_dims]],
        output_dtypes=[int],
        dask_gufunc_kwargs=dict(output_sizes={output_core_dims: 2 * buffer + 1}),
        dask="allowed",
        kwargs={"buffer": buffer},
    ).astype("int32")


def generate_array(dataset, buffers, output=None):
    """Génère à partir du dataset les array des minicubes:
    * 'dataset' pour obtenir un xarray.dataset avec les array des index
    * 'vindex' pour obtenir un tuple utilisable directement dans vindex dask"""
    array = dataset.copy()
    if output == "dataset":
        for idx, ((k, v), buffer) in enumerate(zip(array.data_vars.items(), buffers)):
            array[f"{k}_array"] = _array(v, f"_{k}", buffer)
        return array
    elif output == "vindex":
        size = len(array.data_vars)
        indices = {}
        for idx, ((k, v), buffer) in enumerate(zip(array.data_vars.items(), buffers)):
            n = len(v)
            new_shape = [1] * size
            new_shape[idx] = 2 * buffer + 1
            new_shape = [n] + new_shape
            new_array = _array(v, f"_{k}", buffer)
            indices[k] = new_array.values.reshape(new_shape)
        indices = tuple(indices.values())
        return indices
    else:
        raise ValueError("Choose an output between : 'dataset' and 'vindex'")


def generate_fancy_indexes(x, n, margin):
    offsets = np.arange(-margin, margin)
    indexes = []
    for axis, size in enumerate(x.shape):
        low, high = margin, size - margin
        base_indices = np.random.randint(low, high, size=(n, 1))
        expanded = base_indices + offsets
        shape = [1] * x.ndim
        shape[axis] = 2 * margin
        expanded = expanded.reshape((n, *shape))
        indexes.append(expanded)
    return tuple(indexes)


def estimate_graph_size(collections):
    from collections.abc import Iterator

    import dask
    from dask.base import collections_to_expr
    from dask.utils import format_bytes
    from distributed.protocol import serialize, to_serialize
    from distributed.protocol.serialize import Serialized
    from distributed.utils import nbytes

    # issue de distributed/client.py/compute()
    collections = tuple(
        (dask.delayed(a) if isinstance(a, (list, set, tuple, dict, Iterator)) else a)
        for a in collections
    )
    variables = [a for a in collections if dask.is_dask_collection(a)]

    kwargs = {}
    optimize_graph = True
    expr = collections_to_expr(variables, optimize_graph, **kwargs)

    # issue de distributed/client.py/_graph_to_futures()
    expr_ser = Serialized(*serialize(to_serialize(expr), on_error="raise"))
    pickled_size = sum(map(nbytes, [expr_ser.header] + expr_ser.frames))
    return pickled_size, format_bytes(pickled_size)


# Définition d'une seed pour que la génération des nombres aléatoires soit reproductible
rs = np.random.RandomState(123)


def arange_center(start, stop, size):
    step = (stop - start) / size
    return np.arange(start + step / 2, stop + step / 2, step)


# Datacube
def set_datacube(shape, chunks, n_var=1):
    dcb = xr.Dataset()

    dcb["time"] = ("time", pd.date_range("2020-01-01", periods=shape["time"], freq="d"))
    dcb["lon"] = ("lon", arange_center(-180, 180, shape["lon"]))
    dcb["lat"] = ("lat", arange_center(-90, 90, shape["lat"]))
    for n in range(n_var):
        dcb[f"data_{n}"] = (
            ["time", "lon", "lat"],
            generate_dask_datacube_from_random(
                tuple(shape.values()), tuple(chunks.values())
            ),
        )
    return dcb


# Dataset
def set_dataset(obs, dim):
    dst = xr.Dataset()
    dst["obs"] = ("obs", np.arange(obs))
    dst["time"] = (
        "obs",
        pd.to_datetime(
            rs.choice(
                pd.date_range("2020-01-01", periods=dim["time"], freq="d"),
                size=obs,
                replace=True,
            )
        ),
    )
    dst["lon"] = ("obs", rs.uniform(-180, 180, size=obs))
    dst["lat"] = ("obs", rs.uniform(-90, 90, size=obs))
    return dst


class Array2D:
    """
    Surcouche Numpy pour représenter la sélection d'une zone dans un array 2D.

    arr = np.arange(81).reshape(9, 9)
    a2d = Array2D(arr)
    a2d[indexes]
    """

    def __init__(self, array2d):
        assert array2d.ndim == 2, "L'array doit être 2D"
        self.array = array2d
        self.dims = array2d.shape

    def __getitem__(self, key):
        selection = np.zeros(self.dims, dtype=bool)
        selection[key] = True

        fig, ax = plt.subplots()
        ax.imshow(np.ones(self.dims), cmap="Greys", alpha=0.1)  # fond gris clair
        ax.imshow(selection, cmap="Blues", alpha=0.6)

        # Ajout de la grille (lignes fines entre les cases)
        ax.set_xticks(np.arange(-0.5, self.dims[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.dims[0], 1), minor=True)
        ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)

        # Afficher les ticks principaux avec les indices
        ax.set_xticks(np.arange(self.dims[1]))
        ax.set_yticks(np.arange(self.dims[0]))
        ax.set_xticklabels(np.arange(self.dims[1]))
        ax.set_yticklabels(np.arange(self.dims[0]))

        # ax.invert_yaxis()
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
        plt.show()

    def __repr__(self):
        return self.array.__repr__()


class DaskArray2D:
    """
    arr = da.arange(81).reshape(9, 9).rechunk((3, 3))
    da2d = DaskArray2D(arr)
    da2d[indexes]
    """

    def __init__(self, dask_array):
        if not isinstance(dask_array, da.Array):
            raise TypeError("L'argument doit être un dask.array.Array")
        if dask_array.ndim != 2:
            raise ValueError("DaskArray2D ne supporte que les arrays 2D")

        self.arr = dask_array
        self.dims = dask_array.shape
        self.chunk_sizes = dask_array.chunks  # tuple de tuples (par dimension)

    def __getitem__(self, key):
        selection = np.zeros(self.dims, dtype=bool)
        selection[key] = True

        fig, ax = plt.subplots()
        ax.imshow(np.ones(self.dims), cmap="Greys", alpha=0.1)
        ax.imshow(selection, cmap="Blues", alpha=0.6)

        # Ticks majeurs centrés sur les pixels (indices)
        ax.set_xticks(np.arange(self.dims[1]), minor=False)
        ax.set_yticks(np.arange(self.dims[0]), minor=False)

        # Labels pour ticks
        ax.set_xticklabels(np.arange(self.dims[1]))
        ax.set_yticklabels(np.arange(self.dims[0]))

        # Grille mineure entre pixels
        ax.set_xticks(np.arange(-0.5, self.dims[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, self.dims[0], 1), minor=True)
        ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)

        # Fonction utilitaire pour positions cumulées des chunks
        def cumsum_chunks(chunks):
            positions = [0]
            for size in chunks:
                positions.append(positions[-1] + size)
            return positions

        # Positions lignes chunks (à -0.5 pour coller à la grille)
        x_chunk_lines = cumsum_chunks(self.chunk_sizes[1])
        y_chunk_lines = cumsum_chunks(self.chunk_sizes[0])
        x_chunk_lines_shifted = [x - 0.5 for x in x_chunk_lines]
        y_chunk_lines_shifted = [y - 0.5 for y in y_chunk_lines]

        # Tracer lignes de séparation des chunks avec axvline et axhline
        for x in x_chunk_lines_shifted:
            ax.axvline(x=x, color="red", linewidth=2)
        for y in y_chunk_lines_shifted:
            ax.axhline(y=y, color="red", linewidth=2)

        # ax.invert_yaxis()
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
        plt.show()


def setup_logging(
    app_logger: logging.Logger,
    level: str = "info",
    logfile: Optional[Path] = None,
    fmt: str = "%(message)s",
    log_to: Literal["stream", "file", "both"] = "stream",
) -> bool:
    """
    Configure logging output destination and format.

    :param app_logger: Logger to configure
    :param level: Logging level ('debug', 'info', 'warning', 'error')
    :param logfile: Path to log file (required if log_to includes 'file')
    :param fmt: Log message format
    :param log_to: Where to log: 'stream', 'file', or 'both'
    :return: True if setup is successful
    """

    app_logger.setLevel(logging.DEBUG)
    app_logger.handlers.clear()

    handlers = []

    if log_to in ("file", "both"):
        if not logfile:
            raise ValueError("logfile must be provided when log_to is 'file' or 'both'")
        abs_path = logfile.resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            abs_path, mode="a", encoding="utf-8", delay=True
        )
        handlers.append(file_handler)

    if log_to in ("stream", "both"):
        stream_handler = logging.StreamHandler()
        handlers.append(stream_handler)

    log_level = level.lower()
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    if log_level not in level_map:
        app_logger.error(f'Unknown log level "{level}"')
        return False

    for handler in handlers:
        handler.setLevel(level_map[log_level])
        handler.setFormatter(logging.Formatter(fmt=fmt))
        app_logger.addHandler(handler)

    return True
