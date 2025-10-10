import math
from collections import defaultdict
from functools import reduce
from itertools import product
from numbers import Number
from operator import mul

import numpy as np
from dask._task_spec import List, Task, TaskRef
from dask.array import Array
from dask.array.slicing import replace_ellipsis
from dask.base import tokenize
from dask.highlevelgraph import HighLevelGraph
from dask.utils import cached_cumsum, cached_max


def _vindex(x, *indexes):
    """Point wise indexing with broadcasting.

    >>> x = np.arange(56).reshape((7, 8))
    >>> x
    array([[ 0,  1,  2,  3,  4,  5,  6,  7],
           [ 8,  9, 10, 11, 12, 13, 14, 15],
           [16, 17, 18, 19, 20, 21, 22, 23],
           [24, 25, 26, 27, 28, 29, 30, 31],
           [32, 33, 34, 35, 36, 37, 38, 39],
           [40, 41, 42, 43, 44, 45, 46, 47],
           [48, 49, 50, 51, 52, 53, 54, 55]])

    >>> d = from_array(x, chunks=(3, 4))
    >>> result = _vindex(d, [0, 1, 6, 0], [0, 1, 0, 7])
    >>> result.compute()
    array([ 0,  9, 48,  7])
    """

    indexes = replace_ellipsis(x.ndim, indexes)

    nonfancy_indexes = []
    reduced_indexes = []
    for ind in indexes:
        if isinstance(ind, Number):
            nonfancy_indexes.append(ind)
        elif isinstance(ind, slice):
            nonfancy_indexes.append(ind)
            reduced_indexes.append(slice(None))
        else:
            nonfancy_indexes.append(slice(None))
            reduced_indexes.append(ind)

    nonfancy_indexes = tuple(nonfancy_indexes)
    reduced_indexes = tuple(reduced_indexes)

    x = x[nonfancy_indexes]

    array_indexes = {}
    for i, (ind, size) in enumerate(zip(reduced_indexes, x.shape)):
        if not isinstance(ind, slice):
            ind = np.array(ind, copy=True)
            if ind.dtype.kind == "b":
                raise IndexError("vindex does not support indexing with boolean arrays")
            if ((ind >= size) | (ind < -size)).any():
                raise IndexError(
                    "vindex key has entries out of bounds for "
                    "indexing along axis %s of size %s: %r" % (i, size, ind)
                )
            ind %= size
            array_indexes[i] = ind

    if array_indexes:
        x = _vindex_array(x, array_indexes)

    return x


def _vindex_array(x, dict_indexes):
    """Fancy indexing with only NumPy Arrays."""

    token = tokenize(x, dict_indexes)
    try:
        broadcast_shape = np.broadcast_shapes(
            *(arr.shape for arr in dict_indexes.values())
        )

    except ValueError as e:
        # note: error message exactly matches numpy
        shapes_str = " ".join(str(a.shape) for a in dict_indexes.values())
        raise IndexError(
            "shape mismatch: indexing arrays could not be "
            "broadcast together with shapes " + shapes_str
        ) from e
    npoints = math.prod(broadcast_shape)
    axes = [i for i in range(x.ndim) if i in dict_indexes]

    def _subset_to_indexed_axes(iterable):
        for i, elem in enumerate(iterable):
            if i in axes:
                yield elem

    bounds2 = tuple(
        np.array(cached_cumsum(c, initial_zero=True))
        for c in _subset_to_indexed_axes(x.chunks)
    )
    # axis = _get_axis(tuple(i if i in axes else None for i in range(x.ndim)))
    out_name = "vindex-merge-" + token

    # Now compute indices of each output element within each input block
    # The index is relative to the block, not the array.
    block_idxs = tuple(
        np.searchsorted(b, ind, side="right") - 1
        for b, ind in zip(bounds2, dict_indexes.values())
    )
    starts = (b[i] for i, b in zip(block_idxs, bounds2))
    inblock_idxs = []
    for idx, start in zip(dict_indexes.values(), starts):
        a = idx - start
        if len(a) > 0:
            dtype = np.min_scalar_type(np.max(a, axis=None))
            inblock_idxs.append(a.astype(dtype, copy=False))
        else:
            inblock_idxs.append(a)

    chunks = [c for i, c in enumerate(x.chunks) if i not in axes]

    # determine number of points in one single output block.
    # Use the input chunk size to determine this.
    max_chunk_point_dimensions = reduce(
        mul, map(cached_max, _subset_to_indexed_axes(x.chunks))
    )

    n_chunks, remainder = divmod(npoints, max_chunk_point_dimensions)
    chunks.insert(
        0,
        (
            (max_chunk_point_dimensions,) * n_chunks
            + ((remainder,) if remainder > 0 else ())
            if npoints > 0
            else (0,)
        ),
    )
    chunks = tuple(chunks)

    unis = []
    for block_idxs_dim in block_idxs:
        N = block_idxs_dim.shape[0]
        arr = block_idxs_dim.reshape(N, -1)
        uni = [np.unique(arr[i]) for i in range(N)]
        unis.append(uni)

    def cartesian_product_linewise(line):
        return np.array(tuple(product(*line)))

    # Represents for each observation, which chunk should be opened
    chunk_idxs = [cartesian_product_linewise(row) for row in zip(*unis)]

    # --- Prepare working structures ---
    # Each observation may require opening one or more input chunks.
    # Les parties représente les valeurs d'une observation au sein d'un chunk
    input_blocks = (
        []
    )  # For each part, the source chunk to open (coordinates in the chunk grid)
    obs_ids = []  # Observation ID corresponding to this part
    input_slices = []  # For each part, the slice to extract from the source chunk
    output_slices = []  # For each part, the slice to write in the output chunk
    reshape_defs = (
        []
    )  # For each part, the reshape dimensions to apply to index before extraction.

    # --- Loop over observations ---
    for obs_id, (block_coords, block_indices, candidate_chunks) in enumerate(
        zip(zip(*block_idxs), zip(*inblock_idxs), chunk_idxs)
    ):
        # For each candidate chunk associated with this observation
        for chunk_coords in candidate_chunks:
            chunk_coords = tuple(chunk_coords)

            # Per-chunk, per-dimension temporary storage
            reshape_per_dim = []  # reshape definitions per dimension for this chunk
            input_slices_per_dim = []  # input slices per dimension for this chunk
            output_slices_per_dim = []  # output slices per dimension for this chunk

            obs_ids.append(obs_id)

            # --- Loop over dimensions ---
            for dim, coord in enumerate(chunk_coords):
                # Start with a default reshape vector of 1's for all dimensions
                reshape = [1] * len(chunk_coords)

                # Input indices in the chunk (where block_indices match coord)
                mask = block_coords[dim] == coord
                idx_in_chunk = block_indices[dim][mask]

                # Output indices (location in the output chunk)
                size = block_coords[dim].size
                dtype = np.min_scalar_type(size)
                idx_in_output = np.arange(size, dtype=dtype).reshape(
                    block_coords[dim].shape
                )[mask]

                # Update reshape definition for this dimension
                reshape[dim] = len(idx_in_chunk)
                reshape_per_dim.append(reshape)

                # Build slices (assume step = 1)
                input_slices_per_dim.append(
                    (int(idx_in_chunk[0]), int(idx_in_chunk[-1] + 1), None)
                )
                output_slices_per_dim.append(
                    (int(idx_in_output[0]), int(idx_in_output[-1] + 1), None)
                )

            # Save results for this chunk
            input_blocks.append(tuple(int(c) for c in chunk_coords))
            input_slices.append(tuple(input_slices_per_dim))
            output_slices.append(tuple(output_slices_per_dim))
            reshape_defs.append(tuple(reshape_per_dim))

    # --- Build task names ---
    slice_task_name = "vindex-slice-" + token
    merge_task_name = "vindex-merge-" + token
    dsk = {}

    # Single output chunk coordinates (one output chunk for now)
    out_block_coords = (0,) * len(broadcast_shape)

    # --- Group parts by input chunk ---
    grouped = defaultdict(
        lambda: {
            "in_slices": [],
            "out_slices": [],
            "obs_ids": [],
            "reshape_defs": [],
        }
    )

    for in_blk, in_sl, out_sl, obs_id, resh in zip(
        input_blocks, input_slices, output_slices, obs_ids, reshape_defs
    ):
        grouped[in_blk]["in_slices"].append(in_sl)
        grouped[in_blk]["out_slices"].append(out_sl)
        grouped[in_blk]["obs_ids"].append(obs_id)
        grouped[in_blk]["reshape_defs"].append(resh)

    # --- Create _vindex_slice tasks ---
    merge_slices = defaultdict(list)
    merge_values = defaultdict(list)
    merge_obs_ids = defaultdict(list)
    merge_reshape_defs = defaultdict(list)

    for task_idx, (in_blk, data) in enumerate(grouped.items()):
        task_key = (slice_task_name, task_idx)

        dsk[task_key] = Task(
            task_key,
            _vindex_slice,
            TaskRef((x.name,) + in_blk),  # source chunk
            data["in_slices"],  # slice definitions
            data["reshape_defs"],  # reshape definitions
        )

        merge_slices[out_block_coords].append(data["out_slices"])
        merge_values[out_block_coords].append(TaskRef(task_key))
        merge_obs_ids[out_block_coords].append(data["obs_ids"])
        merge_reshape_defs[out_block_coords].append(data["reshape_defs"])

    # --- Create _vindex_merge tasks ---
    for blk_coords in merge_values.keys():
        task_key = (merge_task_name,) + blk_coords

        dsk[task_key] = Task(
            task_key,
            _vindex_merge,
            broadcast_shape,
            List(merge_slices[blk_coords]),
            List(merge_values[blk_coords]),
            List(merge_obs_ids[blk_coords]),
            List(merge_reshape_defs[blk_coords]),
        )

    array = Array(
        HighLevelGraph.from_collections(out_name, dsk, dependencies=[x]),
        out_name,
        chunks=tuple((i,) for i in broadcast_shape),
        dtype=x.dtype,
        meta=x._meta,
    )

    return array


def _vindex_slice(block, slice_group, reshape_group):
    """
    Extract slices from a block according to slice and reshape definitions.

    Parameters
    ----------
    block : np.ndarray
        The data block to slice.
    slice_group : list[list[tuple[int, int, Optional[int]]]]
        Slice definitions, where each slice is a tuple (start, stop, step).
    reshape_group : list[list[tuple[int, ...]]]
        Reshape definitions corresponding to each slice.

    Returns
    -------
    list[np.ndarray]
        Extracted sub-arrays from the block.
    """
    if len(slice_group) != len(reshape_group):
        raise ValueError(
            f"Mismatched lengths: got {len(slice_group)} slice groups "
            f"but {len(reshape_group)} reshape groups."
        )

    results = []
    for slice_defs, reshape_defs in zip(slice_group, reshape_group):
        index_arrays = [
            np.arange(start, stop, step or 1).reshape(shape)
            for (start, stop, step), shape in zip(slice_defs, reshape_defs)
        ]
        results.append(block[tuple(index_arrays)])

    return results


def _vindex_merge(
    output_shape, slices_groups, values_groups, obs_index_groups, reshape_groups
):
    """
    Merge values from different blocks into a single NumPy array,
    according to provided slices and reshape information.

    Parameters
    ----------
    output_shape : tuple[int]
        Shape of the final merged array.
    slices_groups : list[list[tuple[int, int, int]]]
        List of groups of slice definitions for each observation.
    values_groups : list[list[np.ndarray]]
        List of groups of arrays corresponding to slices.
    obs_index_groups : list[list[int]]
        Indices of the observations in the final output.
    reshape_groups : list[list[tuple[int]]]
        Shapes used to reshape the index arrays.

    Returns
    -------
    np.ndarray
        A NumPy array of shape `output_shape` with merged values.
    """

    # Allocate final result array
    first_dtype = values_groups[0][0].dtype
    merged_array = np.empty(output_shape, dtype=first_dtype)

    # Iterate over groups of slices/values/indices/reshapes
    for slice_group, value_group, obs_group, reshape_group in zip(
        slices_groups, values_groups, obs_index_groups, reshape_groups
    ):
        # Each group corresponds to one chunk
        for slice_defs, value, obs_index, reshape_defs in zip(
            slice_group, value_group, obs_group, reshape_group
        ):
            # Build index arrays for this slice
            index_arrays = [
                np.arange(start, stop, step or 1).reshape(shape)
                for (start, stop, step), shape in zip(slice_defs, reshape_defs)
            ]

            # Place the values in the appropriate position of the merged array
            merged_array[obs_index][tuple(index_arrays)] = value

    return merged_array
