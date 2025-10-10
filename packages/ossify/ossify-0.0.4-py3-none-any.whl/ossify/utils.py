import logging
import os
import sys
from contextlib import contextmanager
from typing import Callable, Optional, Union

import fastremap
import numpy as np
import pandas as pd
from morphsync.base import DEFAULT_SPATIAL_COLUMNS
from scipy import sparse, stats


def majority_agg() -> Callable:
    """Return the most common value in x, ignoring NaNs. Used for "majority" aggregation"""

    def mode_func(x, nan_policy="omit"):
        return stats.mode(x, nan_policy=nan_policy)[0]

    return mode_func


def single_path_length(
    path: np.ndarray, vertices: np.ndarray, edges: np.ndarray
) -> float:
    """Path length of a single set of vertices specified by `path`."""
    vertices = np.asarray(vertices)
    edges = np.asarray(edges)
    return np.linalg.norm(vertices[path[1:]] - vertices[path[:-1]], axis=1).sum()


def remap_vertices_and_edges(
    id_list: np.ndarray,
    edgelist: np.ndarray,
) -> tuple[dict, np.ndarray]:
    """Remap unique ids in a list to 0-N-1 range and remap edges accordingly."""

    id_map = {int(lid): ii for ii, lid in enumerate(id_list)}
    edgelist_new = fastremap.remap(
        edgelist,
        id_map,
    )
    return id_map, edgelist_new


def process_spatial_columns(
    col_names: Optional[Union[str, list]] = None,
) -> list[str]:
    """
    Process spatial column names into a standard format.
    """
    if col_names is None:
        col_names = DEFAULT_SPATIAL_COLUMNS
    if isinstance(col_names, str):
        col_names = [
            f"{col_names}_x",
            f"{col_names}_y",
            f"{col_names}_z",
        ]
    return col_names


def process_vertices(
    vertices: Union[np.ndarray, pd.DataFrame],
    spatial_columns: Optional[list] = None,
    features: Optional[Union[dict, pd.DataFrame]] = None,
    vertex_index: Optional[Union[str, np.ndarray]] = None,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    "Process vertices and features into a DataFrame and column features."
    if isinstance(vertices, np.ndarray) or isinstance(vertices, list):
        spatial_columns = ["x", "y", "z"]
        vertices = pd.DataFrame(np.array(vertices), columns=spatial_columns)

    if spatial_columns is None:
        if vertices.shape[1] != 3:
            raise ValueError(
                '"Vertices must have 3 columns for x, y, z coordinates if no spatial_columns are provided.'
            )
        spatial_columns = vertices.columns
    else:
        if vertex_index:
            implicit_feature_columns = list(
                vertices.columns[
                    ~vertices.columns.isin(spatial_columns + [vertex_index])
                ]
            )
        else:
            implicit_feature_columns = list(
                vertices.columns[~vertices.columns.isin(spatial_columns)]
            )

    if isinstance(features, dict):
        features = pd.DataFrame(features, index=vertices.index)
        if features.shape[0] != vertices.shape[0]:
            raise ValueError("features must have the same number of rows as vertices.")
    elif features is None:
        features = pd.DataFrame(index=vertices.index)

    feature_columns = list(features.columns) + implicit_feature_columns

    vertices = vertices.merge(
        features,
        left_index=True,
        right_index=True,
        how="left",
    )
    if vertex_index is not None:
        vertices = vertices.set_index(vertex_index)
    return vertices, spatial_columns, feature_columns


def build_csgraph(
    vertices: np.ndarray,
    edges: np.ndarray,
    euclidean_weight: bool = True,
    directed: bool = False,
) -> sparse.csr_matrix:
    """
    Builds a csr graph from vertices and edges, with optional control
    over weights as boolean or based on Euclidean distance.
    """
    edges = edges[edges[:, 0] != edges[:, 1]]
    if euclidean_weight:
        xs = vertices[edges[:, 0]]
        ys = vertices[edges[:, 1]]
        weights = np.linalg.norm(xs - ys, axis=1)
        use_dtype = np.float32
    else:
        weights = np.ones((len(edges),)).astype(np.int8)
        use_dtype = np.int8

    if directed:
        edges = edges.T
    else:
        edges = np.concatenate([edges.T, edges.T[[1, 0]]], axis=1)
        weights = np.concatenate([weights, weights]).astype(dtype=use_dtype)

    csgraph = sparse.csr_matrix(
        (weights, edges),
        shape=[
            len(vertices),
        ]
        * 2,
        dtype=use_dtype,
    )

    return csgraph


def connected_component_slice(
    G: sparse.csr_matrix, ind: Optional[int] = None, return_boolean: bool = False
) -> np.ndarray:
    """
    Gets a numpy slice of the connected component corresponding to a
    given index. If no index is specified, the slice is of the largest
    connected component.
    """
    _, features = sparse.csgraph.connected_components(G)
    if ind is None:
        feature_vals, cnt = np.unique(features, return_counts=True)
        ind = np.argmax(cnt)
        feature = feature_vals[ind]
    else:
        feature = features[ind]

    if return_boolean:
        return features == feature
    else:
        return np.flatnonzero(features == feature)


def find_far_points_graph(
    mesh_graph: sparse.csr_matrix,
    start_ind: Optional[int] = None,
    multicomponent: bool = False,
) -> tuple:
    """
    Finds the maximally far point along a graph by bouncing from farthest point
    to farthest point.
    """
    d = 0
    dn = 1

    if start_ind is None:
        if multicomponent:
            a = connected_component_slice(mesh_graph)[0]
        else:
            a = 0
    else:
        a = start_ind
    b = 1

    k = 0
    pred = None
    ds = None
    while 1:
        k += 1
        dsn, predn = sparse.csgraph.dijkstra(
            mesh_graph, False, a, return_predecessors=True
        )
        if multicomponent:
            dsn[np.isinf(dsn)] = -1
        bn = np.argmax(dsn)
        dn = dsn[bn]
        if dn > d:
            b = a
            a = bn
            d = dn
            pred = predn
            ds = dsn
        else:
            break

    return b, a, pred, d, ds


def get_supervoxel_column(pt_column: str) -> str:
    return pt_column.replace("_root_id", "_supervoxel_id")


def get_l2id_column(pt_column: str) -> str:
    return pt_column.replace("_root_id", "_l2_id")


@contextmanager
def suppress_output(package: Optional[str] = None):
    """Context manager to suppress stdout and stderr output.

    Parameters
    ----------
    package : Optional[str]
        Logger name to suppress. If None, suppress root logger output which handles
        all loggers without their own handler.
    """
    # Save original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    logger = logging.getLogger(package)
    old_level = logger.level
    logger.setLevel(logging.CRITICAL)

    try:
        # Redirect to devnull or StringIO
        with open(os.devnull, "w") as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
    finally:
        # Restore original stdout and stderr
        logger.setLevel(old_level)
        sys.stdout = original_stdout
        sys.stderr = original_stderr
