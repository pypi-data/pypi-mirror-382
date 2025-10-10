from numbers import Number
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import Colormap, ListedColormap, Normalize

from .base import Cell, GraphLayer, MeshLayer, PointCloudLayer, SkeletonLayer

__all__ = [
    "plot_cell_2d",
    "plot_morphology_2d",
    "plot_annotations_2d",
    "plot_cell_multiview",
    "plot_skeleton",
    "plot_points",
    "single_panel_figure",
    "multi_panel_figure",
    "add_scale_bar",
]


def _is_discrete_data(
    values: np.ndarray, max_unique_ratio: float = 0.05, max_unique_count: int = 20
) -> bool:
    """Detect if data should be treated as discrete/categorical.

    Parameters
    ----------
    values : np.ndarray
        Array of values to analyze
    max_unique_ratio : float, default 0.05
        Maximum ratio of unique values to total values for discrete classification
    max_unique_count : int, default 20
        Maximum number of unique values for discrete classification

    Returns
    -------
    bool
        True if data appears to be discrete/categorical
    """
    values = np.asarray(values)

    # Always treat string/object data as discrete
    if values.dtype.kind in ["U", "S", "O"]:
        return True

    # Always treat boolean data as discrete
    if values.dtype == bool:
        return True

    # For numeric data, check uniqueness
    unique_vals = np.unique(values[~pd.isna(values)])
    n_unique = len(unique_vals)
    n_total = len(values)

    if n_total == 0:
        return False

    unique_ratio = n_unique / n_total

    # Consider discrete if few unique values OR low unique ratio
    return n_unique <= max_unique_count or unique_ratio <= max_unique_ratio


def _get_discrete_colormap(colormap_name: str, n_colors: int) -> ListedColormap:
    """Get a discrete colormap with specified number of colors.

    Parameters
    ----------
    colormap_name : str
        Name of the colormap or 'auto' for automatic selection
    n_colors : int
        Number of discrete colors needed

    Returns
    -------
    ListedColormap
        Discrete colormap with n_colors
    """
    # Automatic colormap selection based on number of colors
    if colormap_name == "auto":
        if n_colors <= 10:
            colormap_name = "tab10"
        elif n_colors <= 20:
            colormap_name = "tab20"
        else:
            colormap_name = "hsv"  # For many categories, use HSV

    # Handle standard qualitative colormaps
    qualitative_maps = {
        "Set1": 9,
        "Set2": 8,
        "Set3": 12,
        "Pastel1": 9,
        "Pastel2": 8,
        "Dark2": 8,
        "Accent": 8,
        "tab10": 10,
        "tab20": 20,
        "tab20b": 20,
        "tab20c": 20,
    }

    if colormap_name in qualitative_maps:
        base_cmap = plt.get_cmap(colormap_name)
        max_colors = qualitative_maps[colormap_name]

        if n_colors <= max_colors:
            # Use the colormap as-is
            colors = [base_cmap(i) for i in range(n_colors)]
        else:
            # Repeat colors if we need more than available
            colors = [base_cmap(i % max_colors) for i in range(n_colors)]

        return ListedColormap(colors)

    # For continuous colormaps, sample evenly
    base_cmap = plt.get_cmap(colormap_name)
    if n_colors == 1:
        colors = [base_cmap(0.5)]  # Use middle color for single category
    else:
        colors = [base_cmap(i / (n_colors - 1)) for i in range(n_colors)]

    return ListedColormap(colors)


def _create_discrete_color_dict(
    values: np.ndarray,
    colormap: Union[str, Colormap, ListedColormap] = "auto",
    missing_color: Union[str, Tuple[float, ...]] = "gray",
) -> Dict:
    """Create a color dictionary for discrete/categorical data.

    Parameters
    ----------
    values : np.ndarray
        Array of discrete values
    colormap : str, Colormap, or ListedColormap, default 'auto'
        Colormap specification
    missing_color : str or tuple, default 'gray'
        Color to use for missing/unmapped values

    Returns
    -------
    Dict
        Dictionary mapping values to colors
    """
    values = np.asarray(values)
    unique_vals = np.unique(values[~pd.isna(values)])
    n_unique = len(unique_vals)

    if n_unique == 0:
        return {}

    # Get discrete colormap
    if isinstance(colormap, str):
        discrete_cmap = _get_discrete_colormap(colormap, n_unique)
    elif isinstance(colormap, ListedColormap):
        discrete_cmap = colormap
    else:
        # Convert continuous colormap to discrete
        if n_unique == 1:
            colors = [colormap(0.5)]
        else:
            colors = [colormap(i / (n_unique - 1)) for i in range(n_unique)]
        discrete_cmap = ListedColormap(colors)

    # Create color dictionary
    color_dict = {}
    for i, val in enumerate(unique_vals):
        color_dict[val] = discrete_cmap.colors[i % len(discrete_cmap.colors)]

    # Add missing value color if needed
    if missing_color is not None:
        color_dict["__missing__"] = missing_color

    return color_dict


def _map_value_to_colors(
    values: np.ndarray,
    colormap: Union[str, Colormap, Dict] = "cmc.hawaii",
    color_norm: Optional[Tuple[float, float]] = None,
    alpha: Union[float, np.ndarray] = 1.0,
    force_discrete: Optional[bool] = None,
    missing_color: Union[str, Tuple[float, ...]] = "gray",
) -> np.ndarray:
    """Map values to colors with automatic discrete/continuous detection.

    Parameters
    ----------
    values : np.ndarray
        Array of values to map to colors
    colormap : str, Colormap, or Dict, default "cmc.hawaii"
        Colormap specification
    color_norm : tuple of float, optional
        (min, max) tuple for color normalization (continuous data only)
    alpha : float or np.ndarray, default 1.0
        Alpha value(s) for colors
    force_discrete : bool, optional
        Force discrete (True) or continuous (False) mapping. If None, auto-detect.
    missing_color : str or tuple, default 'gray'
        Color for unmapped values in discrete mode

    Returns
    -------
    np.ndarray
        RGBA color array
    """
    values = np.asarray(values)

    # Handle alpha
    if isinstance(alpha, (list, np.ndarray)):
        alpha = np.asarray(alpha)
        if len(alpha) != len(values):
            raise ValueError("Alpha array must have same length as values")
    else:
        alpha = np.full(len(values), alpha)

    # Convert boolean to integer for processing
    if values.dtype == bool:
        values = values.astype(int)

    # Handle explicit dictionary colormap (always discrete)
    if isinstance(colormap, dict):
        rgba_colors = np.zeros((len(values), 4))
        rgba_colors[:, 3] = alpha  # Set alpha channel

        # Handle missing color
        missing_rgb = (
            cm.colors.to_rgb(missing_color)
            if isinstance(missing_color, str)
            else missing_color[:3]
        )

        for i, val in enumerate(values):
            if pd.isna(val):
                rgba_colors[i, :3] = missing_rgb
            elif val not in colormap:
                rgba_colors[i, :3] = missing_rgb
            else:
                color = colormap[val]
                # Convert various color formats to RGB
                if isinstance(color, str):
                    if color.startswith("#"):
                        # Hex color
                        rgb = tuple(
                            int(color[j : j + 2], 16) / 255.0 for j in (1, 3, 5)
                        )
                    else:
                        # Named color - use matplotlib
                        rgb = cm.colors.to_rgb(color)
                else:
                    # Assume RGB tuple or RGBA tuple
                    rgb = color[:3]
                rgba_colors[i, :3] = rgb

        # Return RGB for consistency with original behavior, unless alpha varies or is not 1.0
        if isinstance(alpha, np.ndarray):
            if not np.allclose(alpha, 1.0):
                return rgba_colors
        elif not np.isclose(alpha, 1.0):
            return rgba_colors
        return rgba_colors[:, :3]

    # Determine if data should be treated as discrete
    is_discrete = force_discrete
    if is_discrete is None:
        is_discrete = _is_discrete_data(values)

    if is_discrete:
        # Create discrete color dictionary and map
        color_dict = _create_discrete_color_dict(values, colormap, missing_color)
        return _map_value_to_colors(
            values, color_dict, alpha=alpha, missing_color=missing_color
        )

    # Handle continuous mapping
    if isinstance(colormap, str):
        cmap = plt.get_cmap(colormap)
    else:
        cmap = colormap

    # Clean values for continuous mapping (remove NaNs)
    clean_values = values.copy().astype(float)
    nan_mask = pd.isna(clean_values)

    # Apply normalization
    if color_norm is not None:
        vmin, vmax = color_norm
        norm = Normalize(vmin=vmin, vmax=vmax)
        normalized_values = norm(clean_values)
    else:
        # Auto-normalize to [0, 1]
        valid_values = clean_values[~nan_mask]
        if len(valid_values) == 0:
            normalized_values = np.zeros_like(clean_values)
        else:
            vmin, vmax = np.nanmin(valid_values), np.nanmax(valid_values)
            if vmin == vmax:
                normalized_values = np.zeros_like(clean_values)
            else:
                normalized_values = (clean_values - vmin) / (vmax - vmin)

    # Map to colors
    rgba_colors = cmap(normalized_values)

    # Handle NaN values by setting them to missing color
    if np.any(nan_mask):
        missing_rgb = (
            cm.colors.to_rgb(missing_color)
            if isinstance(missing_color, str)
            else missing_color[:3]
        )
        rgba_colors[nan_mask, :3] = missing_rgb

    # Apply alpha
    rgba_colors[:, 3] = alpha

    # Return RGB for consistency with original behavior, unless alpha varies or is not 1.0
    if isinstance(alpha, np.ndarray):
        if not np.allclose(alpha, 1.0):
            return rgba_colors
    elif not np.isclose(alpha, 1.0):
        return rgba_colors
    return rgba_colors[:, :3]


def _should_invert_y_axis(projection: Union[str, Callable]) -> bool:
    """Determine if y-axis should be inverted based on projection.

    Parameters
    ----------
    projection : str or Callable
        Projection specification

    Returns
    -------
    bool
        True if y-axis should be inverted (when 'y' is present in projection)
    """
    if isinstance(projection, str):
        return "y" in projection
    return False


def _apply_y_inversion_to_axes(
    ax: plt.Axes, projection: Union[str, Callable], invert_y: bool = True
) -> plt.Axes:
    """Apply y-axis inversion if needed based on projection.

    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to potentially invert
    projection : str or Callable
        Projection specification
    invert_y : bool, default True
        Whether to enable automatic y-axis inversion for projections containing 'y'

    Returns
    -------
    plt.Axes
        Axes with y-axis inverted if needed
    """
    if invert_y and _should_invert_y_axis(projection):
        # Only invert if not already inverted to avoid double-inversion
        if projection[1] == "y":
            if not ax.yaxis_inverted():
                ax.invert_yaxis()
        elif projection[0] == "y":
            if not ax.xaxis_inverted():
                ax.invert_xaxis()
    return ax


def projection_factory(
    proj: Union[str, Callable],
) -> Callable:
    # If already a callable, return as-is
    if callable(proj):
        return proj

    # Handle string projections
    match proj:
        case "xy":
            return lambda pts: np.array(pts)[:, [0, 1]]
        case "yx":
            return lambda pts: np.array(pts)[:, [1, 0]]
        case "zx":
            return lambda pts: np.array(pts)[:, [2, 0]]
        case "xz":
            return lambda pts: np.array(pts)[:, [0, 2]]
        case "zy":
            return lambda pts: np.array(pts)[:, [2, 1]]
        case "yz":
            return lambda pts: np.array(pts)[:, [1, 2]]
    raise ValueError(
        f"Unknown projection {proj}, expected a callable or one of 'xy', 'yx', 'yz', 'zy', 'zx', or 'xz'"
    )


def _plotted_bounds(
    vertices: np.ndarray,
    projection: Union[str, Callable],
    offset_h: float = 0.0,
    offset_v: float = 0.0,
) -> np.ndarray:
    """Get the plotted bounds of the vertices after applying the projection.

    Parameters
    ----------
    vertices : np.ndarray
        (N, 3) array of 3D points
    projection : Callable
        Projection function to apply to the points

    Returns
    -------
    np.ndarray
        (2, 2) array with [[xmin, xmax], [ymin, ymax]] of the projected points
    """
    projection = projection_factory(proj=projection)
    projected = projection(vertices).astype(
        float
    )  # Ensure float type for offset operations
    projected[:, 0] += offset_h
    projected[:, 1] += offset_v
    xmin, xmax = projected[:, 0].min(), projected[:, 0].max()
    ymin, ymax = projected[:, 1].min(), projected[:, 1].max()
    return np.array([[xmin, xmax], [ymin, ymax]])


def plot_skeleton(
    skel: SkeletonLayer,
    projection: Union[str, Callable] = "xy",
    colors: Optional[np.ndarray] = None,
    alpha: Optional[np.ndarray] = None,
    linewidths: Optional[np.ndarray] = None,
    offset_h: float = 0.0,
    offset_v: float = 0.0,
    zorder: int = 2,
    invert_y: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot skeleton with explicit arrays for styling.

    Parameters
    ----------
    skel : SkeletonLayer
        SkeletonLayer to plot
    projection : str or Callable, default "xy"
        Projection function or string
    colors : np.ndarray, optional
        (N, 3) or (N, 4) RGB/RGBA color array for vertices
    alpha : np.ndarray, optional
        (N,) alpha values for vertices
    linewidths : np.ndarray, optional
        (N,) linewidth values for vertices
    offset_h : float, default 0.0
        Horizontal offset for projection
    offset_v : float, default 0.0
        Vertical offset for projection
    zorder : int, default 2
        Drawing order for line collection
    invert_y : bool, default True
        Whether to automatically invert y-axis for projections containing 'y'
    ax : plt.Axes, optional
        Matplotlib axes

    Returns
    -------
    plt.Axes
        Matplotlib axes with skeleton plotted
    """
    if ax is None:
        ax = plt.gca()
    do_autoscale_at_end = not ax.has_data()

    # Store original projection for y-axis inversion detection
    orig_projection = projection
    projection = projection_factory(proj=projection)

    for path in skel.cover_paths_positional:
        # Convert vertex index to positional index for parent_node_array access
        path_end_vertex = path[-1]
        match skel.parent_node_array[path_end_vertex]:
            case -1:
                path_plus = path
            case parent:
                # Convert parent positional index back to vertex index
                path_plus = np.concat((path, [parent]))

        # Convert vertex indices to positional indices for vertices array access
        path_spatial = projection(skel.vertices[path_plus])
        path_spatial[:, 0] = path_spatial[:, 0] + offset_h
        path_spatial[:, 1] = path_spatial[:, 1] + offset_v
        path_segs = [
            (path_spatial[i], path_spatial[i + 1]) for i in range(len(path_spatial) - 1)
        ]

        # Extract styling for this path
        lc_kwargs = {}
        if colors is not None:
            # Convert vertex indices to positional indices for colors array access
            lc_kwargs["colors"] = colors[path_plus]
        if alpha is not None:
            # Convert vertex indices to positional indices for alpha array access
            lc_kwargs["alpha"] = alpha[path_plus]
        if linewidths is not None:
            # Convert vertex indices to positional indices for linewidths array access
            lc_kwargs["linewidths"] = linewidths[path]
        if zorder is not None:
            lc_kwargs["zorder"] = zorder

        lc = LineCollection(path_segs, capstyle="round", joinstyle="round", **lc_kwargs)
        ax.add_collection(lc)

    ax.set_aspect("equal")

    # Apply y-axis inversion if needed
    ax = _apply_y_inversion_to_axes(ax, orig_projection, invert_y)
    if do_autoscale_at_end:
        ax.autoscale()
    return ax


def _resolve_color_parameter(
    color_param: Union[str, np.ndarray, tuple, Any], skel: SkeletonLayer
) -> Union[np.ndarray, str, tuple, None]:
    """Resolve color parameter - try features first, then matplotlib colors.

    Parameters
    ----------
    color_param : str, np.ndarray, tuple, or Any
        Color specification to resolve
    skel : SkeletonLayer
        Skeleton layer to look up features from

    Returns
    -------
    np.ndarray, str, tuple, or None
        Resolved color parameter - array if feature found, original value otherwise
    """
    if isinstance(color_param, str):
        # Try to get as feature first
        try:
            return skel.get_feature(color_param)
        except (KeyError, AttributeError):
            # Fall back to matplotlib color
            return color_param
    else:
        # Return as-is (array, tuple, etc.)
        return color_param


def plot_points(
    points: np.ndarray,
    sizes: Optional[np.ndarray] = None,
    colors: Optional[np.ndarray] = None,
    palette: Optional[Union[str, Dict]] = None,
    color_norm: Optional[Tuple[float, float]] = None,
    projection: Union[str, Callable] = "xy",
    offset_h: float = 0.0,
    offset_v: float = 0.0,
    invert_y: bool = True,
    ax: Optional[plt.Axes] = None,
    zorder: int = 2,
    **scatter_kws,
) -> plt.Axes:
    if ax is None:
        ax = plt.gca()

    # Store original projection for y-axis inversion detection
    orig_projection = projection
    projection = projection_factory(
        proj=projection,
    )
    points_proj = projection(points)
    points_proj[:, 0] = points_proj[:, 0] + offset_h
    points_proj[:, 1] = points_proj[:, 1] + offset_v
    if scatter_kws is None:
        scatter_kws = {}
    if "linewidths" not in scatter_kws:
        scatter_kws["linewidths"] = 0
    if isinstance(palette, str):
        scatter_kws["cmap"] = palette
        if color_norm is not None:
            scatter_kws["vmin"], scatter_kws["vmax"] = color_norm
    elif isinstance(palette, dict) and colors:
        colors = [palette[feature] for feature in colors]
    if colors is not None:
        if isinstance(colors, str):
            # Single color string
            scatter_kws["color"] = colors
        else:
            scatter_kws["c"] = colors

    ax.scatter(
        x=points_proj[:, 0],
        y=points_proj[:, 1],
        s=sizes,
        zorder=zorder,
        **scatter_kws,
    )

    # Apply y-axis inversion if needed
    ax = _apply_y_inversion_to_axes(ax, orig_projection, invert_y)

    return ax


def _rescale_scalar(
    value: np.ndarray,
    norm: Optional[Tuple[float, float]],
    out_range: Optional[Tuple[float, float]],
) -> np.ndarray:
    """Linearly rescale a scalar value to a new range with clipping

    Parameters
    ----------
    value : np.ndarray
        Value to rescale
    norm : tuple of float
        (min, max) tuple for normalization

    Returns
    -------
    np.ndarray
        Rescaled value
    """
    if norm is None:
        norm = (np.min(value), np.max(value))
    if out_range is None:
        out_range = (np.min(value), np.max(value))
    return (out_range[1] - out_range[0]) * np.asarray(
        Normalize(*norm, clip=True)(value)
    ) + out_range[0]


def plot_annotations_2d(
    annotation: PointCloudLayer,
    color: Optional[Union[str, np.ndarray, tuple]] = None,
    palette: Union[str, dict] = "coolwarm",
    color_norm: Optional[Tuple[float, float]] = None,
    alpha: float = 1,
    size: Optional[Union[str, np.ndarray, float]] = None,
    size_norm: Optional[Tuple[float, float]] = None,
    sizes: Optional[np.ndarray] = (1, 30),
    projection: Union[str, Callable] = "xy",
    offset_h: float = 0.0,
    offset_v: float = 0.0,
    invert_y: bool = True,
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    if ax is None:
        ax = plt.gca()
    if isinstance(annotation, PointCloudLayer):
        vertices = annotation.vertices
        if isinstance(color, str):
            color = color or annotation.get_feature(color)
        if isinstance(size, str):
            size = annotation.get_feature(size)
    else:
        vertices = np.asarray(annotation)

    if isinstance(size, Number) or size is None:
        sizes_out = size
    else:
        sizes_out = _rescale_scalar(size, size_norm, sizes)

    return plot_points(
        points=vertices,
        sizes=sizes_out,
        colors=color,
        palette=palette,
        color_norm=color_norm,
        projection=projection,
        offset_h=offset_h,
        offset_v=offset_v,
        invert_y=invert_y,
        alpha=alpha,
        ax=ax,
        **kwargs,
    )


def plot_morphology_2d(
    cell: Union[Cell, SkeletonLayer],
    color: Optional[Union[str, np.ndarray, tuple]] = None,
    palette: Union[str, dict] = "coolwarm",
    color_norm: Optional[Tuple[float, float]] = None,
    alpha: Optional[Union[str, np.ndarray, float]] = 1.0,
    alpha_norm: Optional[Tuple[float, float]] = None,
    alpha_extent: Optional[Tuple[float, float]] = None,
    linewidth: Optional[Union[str, np.ndarray, float]] = 1.0,
    linewidth_norm: Optional[Tuple[float, float]] = None,
    widths: Optional[tuple] = (1, 50),
    projection: Union[str, Callable] = "xy",
    offset_h: float = 0.0,
    offset_v: float = 0.0,
    root_marker: bool = False,
    root_size: float = 100.0,
    root_color: Optional[Union[str, tuple]] = None,
    zorder: int = 2,
    invert_y: bool = True,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot 2D skeleton with flexible styling options.

    Parameters
    ----------
    cell : Cell or SkeletonLayer
        Cell or SkeletonLayer to plot
    projection : str or Callable, default "xy"
        Projection function or string mapping 3d points to a 2d projection.
    color : str, np.ndarray, or tuple, optional
        Color specification - can be feature name, array of values, or matplotlib color
    palette : str or dict, default "coolwarm"
        Colormap for mapping array values to colors
    color_norm : tuple of float, optional
        (min, max) tuple for color normalization
    alpha : str, np.ndarray, or float, default 1.0
        Alpha specification - can be feature name, array, or single value
    alpha_norm : tuple of float, optional
        (min, max) tuple for alpha normalization
    linewidth : str, np.ndarray, or float, default 1.0
        Linewidth specification - can be feature name, array, or single value
    linewidth_norm : tuple of float, optional
        (min, max) tuple for linewidth normalization
    widths : tuple, optional
        (min, max) tuple for final linewidth scaling
    ax : plt.Axes, optional
        Matplotlib axes

    Returns
    -------
    plt.Axes
        Matplotlib axes with skeleton plotted
    """
    if isinstance(cell, Cell):
        skel = cell.skeleton
    else:
        skel = cell

    # Resolve color parameter
    resolved_color = _resolve_color_parameter(color, skel)

    # Process colors
    colors_array = None
    if resolved_color is not None:
        if isinstance(resolved_color, np.ndarray):
            # Array of values - map through colormap
            colors_array = _map_value_to_colors(
                resolved_color, colormap=palette, color_norm=color_norm
            )
        else:
            # Single color (string, tuple) - use matplotlib to convert
            import matplotlib.colors as mcolors

            single_color = mcolors.to_rgba(resolved_color)
            colors_array = np.tile(single_color, (skel.n_vertices, 1))

    # Process alpha (similar to existing logic)
    alpha_array = None
    if alpha_extent is None:
        alpha_extent = (0.1, 1.0)
    if isinstance(alpha, str):
        alpha_values = skel.get_feature(alpha)
        if alpha_norm is None:
            alpha_norm = (np.min(alpha_values), np.max(alpha_values))
        alpha_array = np.asarray(Normalize(*alpha_norm, clip=True)(alpha_values))
        alpha_array = alpha_array[0] + alpha_array * (alpha_extent[1] - alpha_extent[0])
    elif isinstance(alpha, (np.ndarray, list, pd.Series)):
        if alpha_norm is not None:
            alpha_array = np.asarray(Normalize(*alpha_norm, clip=True)(alpha))
            alpha_array = alpha_extent[0] + alpha_array * (
                alpha_extent[1] - alpha_extent[0]
            )
        else:
            alpha_array = np.asarray(alpha)
    elif isinstance(alpha, Number):
        alpha_array = np.full(skel.n_vertices, alpha)

    # Process linewidth (similar to existing logic)
    linewidth_array = None
    if isinstance(linewidth, str):
        linewidth_values = skel.get_feature(linewidth)
        if linewidth_norm is None:
            linewidth_norm = (np.min(linewidth_values), np.max(linewidth_values))
        normalized = Normalize(*linewidth_norm, clip=True)(linewidth_values)
        if widths is None:
            widths = (np.min(linewidth_values), np.max(linewidth_values))
        linewidth_array = widths[0] + (widths[1] - widths[0]) * normalized
    elif isinstance(linewidth, (np.ndarray, list, pd.Series)):
        if linewidth_norm is None:
            linewidth_norm = (np.min(linewidth), np.max(linewidth))
        normalized = Normalize(*linewidth_norm, clip=True)(linewidth)
        if widths is None:
            widths = (np.min(linewidth), np.max(linewidth))
        linewidth_array = widths[0] + (widths[1] - widths[0]) * normalized
    elif isinstance(linewidth, Number):
        linewidth_array = np.full(skel.n_vertices, linewidth)

    # Call the core plotting function
    ax = plot_skeleton(
        skel=skel,
        projection=projection,
        colors=colors_array,
        alpha=alpha_array,
        linewidths=linewidth_array,
        offset_h=offset_h,
        offset_v=offset_v,
        zorder=zorder,
        invert_y=invert_y,
        ax=ax,
    )
    if root_marker:
        if skel.root_location is not None:
            root_location = np.atleast_2d(skel.root_location)
            if root_color is None:
                if skel.base_root in skel.vertex_index:
                    root_color = (
                        colors_array[skel.root_positional]
                        if colors_array is not None
                        else None
                    )
                else:
                    raise ValueError(
                        "root_color must be provided explicitly if root is not in skeleton vertices"
                    )
            ax = plot_points(
                root_location,
                colors=root_color,
                sizes=[root_size],
                invert_y=invert_y,
                ax=ax,
                zorder=zorder + 1,
                projection=projection,
                offset_h=offset_h,
                offset_v=offset_v,
            )
    return ax


def plot_cell_2d(
    cell: Cell,
    color: Optional[Union[str, np.ndarray, tuple]] = None,
    palette: Union[str, dict] = "coolwarm",
    color_norm: Optional[Tuple[float, float]] = None,
    alpha: Optional[Union[str, np.ndarray, float]] = 1.0,
    alpha_norm: Optional[Tuple[float, float]] = None,
    linewidth: Optional[Union[str, np.ndarray, float]] = 1.0,
    linewidth_norm: Optional[Tuple[float, float]] = None,
    widths: Optional[tuple] = (1, 50),
    root_marker: bool = False,
    root_size: float = 100.0,
    root_color: Optional[Union[str, tuple]] = None,
    synapses: Literal["pre", "post", "both", True, False] = False,
    pre_anno: str = "pre_syn",
    pre_color: Optional[Union[str, tuple]] = None,
    pre_palette: Union[str, dict] = None,
    pre_color_norm: Optional[Tuple[float, float]] = None,
    syn_alpha: float = 1,
    syn_size: Optional[Union[str, np.ndarray, float]] = None,
    syn_size_norm: Optional[Tuple[float, float]] = None,
    syn_sizes: Optional[np.ndarray] = (1, 30),
    post_anno: str = "post_syn",
    post_color: Optional[Union[str, tuple]] = None,
    post_palette: Union[str, dict] = None,
    post_color_norm: Optional[Tuple[float, float]] = None,
    projection: Union[str, Callable] = "xy",
    offset_h: float = 0.0,
    offset_v: float = 0.0,
    invert_y: bool = True,
    ax: Optional[plt.Axes] = None,
    units_per_inch: Optional[float] = None,
    dpi: Optional[float] = None,
    despine: bool = True,
    **syn_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    if units_per_inch is not None:
        bounds = _plotted_bounds(cell.skeleton.vertices, projection, offset_h, offset_v)
        _, ax = single_panel_figure(
            data_bounds_min=bounds[:, 0],
            data_bounds_max=bounds[:, 1],
            units_per_inch=units_per_inch,
            despine=despine,
            dpi=dpi,
        )

    ax = plot_morphology_2d(
        cell,
        color=color,
        palette=palette,
        color_norm=color_norm,
        alpha=alpha,
        alpha_norm=alpha_norm,
        linewidth=linewidth,
        linewidth_norm=linewidth_norm,
        widths=widths,
        root_marker=root_marker,
        root_size=root_size,
        root_color=root_color,
        projection=projection,
        offset_h=offset_h,
        offset_v=offset_v,
        invert_y=invert_y,
        ax=ax,
    )
    if synapses == "both" or synapses == "pre" or synapses is True:
        if pre_anno in cell.annotations.names:
            ax = plot_annotations_2d(
                cell.annotations[pre_anno],
                color=pre_color,
                palette=pre_palette,
                color_norm=pre_color_norm,
                alpha=syn_alpha,
                size=syn_size,
                size_norm=syn_size_norm,
                sizes=syn_sizes,
                ax=ax,
                offset_h=offset_h,
                offset_v=offset_v,
                invert_y=invert_y,
                projection=projection,
                **syn_kwargs,
            )
    if synapses == "both" or synapses == "post" or synapses is True:
        if post_anno in cell.annotations.names:
            ax = plot_annotations_2d(
                cell.annotations[post_anno],
                color=post_color,
                palette=post_palette,
                color_norm=post_color_norm,
                alpha=syn_alpha,
                size=syn_size,
                size_norm=syn_size_norm,
                sizes=syn_sizes,
                ax=ax,
                offset_h=offset_h,
                offset_v=offset_v,
                invert_y=invert_y,
                projection=projection,
                **syn_kwargs,
            )
    return ax


def plot_cell_multiview(
    cell: Cell,
    layout: Literal["stacked", "side_by_side", "three_panel"] = "three_panel",
    color: Optional[Union[str, np.ndarray, tuple]] = None,
    palette: Union[str, dict] = "coolwarm",
    color_norm: Optional[Tuple[float, float]] = None,
    alpha: Optional[Union[str, np.ndarray, float]] = 1.0,
    alpha_norm: Optional[Tuple[float, float]] = None,
    linewidth: Optional[Union[str, np.ndarray, float]] = 1.0,
    linewidth_norm: Optional[Tuple[float, float]] = None,
    widths: Optional[tuple] = (1, 50),
    root_marker: bool = False,
    root_size: float = 100.0,
    root_color: Optional[Union[str, tuple]] = None,
    synapses: Literal["pre", "post", "both", True, False] = False,
    pre_anno: str = "pre_syn",
    pre_color: Optional[Union[str, tuple]] = None,
    pre_palette: Union[str, dict] = None,
    pre_color_norm: Optional[Tuple[float, float]] = None,
    syn_alpha: float = 1,
    syn_size: Optional[Union[str, np.ndarray, float]] = None,
    syn_size_norm: Optional[Tuple[float, float]] = None,
    syn_sizes: Optional[np.ndarray] = (1, 30),
    post_anno: str = "post_syn",
    post_color: Optional[Union[str, tuple]] = None,
    post_palette: Union[str, dict] = None,
    post_color_norm: Optional[Tuple[float, float]] = None,
    invert_y: bool = True,
    despine: bool = True,
    units_per_inch: float = 100_000,
    dpi: Optional[float] = None,
    **syn_kwargs,
) -> Tuple[plt.Figure, dict]:
    fig, axes = multi_panel_figure(
        data_bounds_min=cell.skeleton.bbox[0],
        data_bounds_max=cell.skeleton.bbox[1],
        units_per_inch=units_per_inch,
        layout=layout,
        despine=despine,
        dpi=dpi,
    )
    for proj in axes:
        ax = axes[proj]
        plot_cell_2d(
            cell,
            color=color,
            palette=palette,
            color_norm=color_norm,
            alpha=alpha,
            alpha_norm=alpha_norm,
            linewidth=linewidth,
            linewidth_norm=linewidth_norm,
            widths=widths,
            root_marker=root_marker,
            root_size=root_size,
            root_color=root_color,
            projection=proj,
            invert_y=invert_y,
            synapses=synapses,
            syn_alpha=syn_alpha,
            syn_size=syn_size,
            syn_size_norm=syn_size_norm,
            syn_sizes=syn_sizes,
            pre_anno=pre_anno,
            pre_color=pre_color,
            pre_palette=pre_palette,
            pre_color_norm=pre_color_norm,
            post_anno=post_anno,
            post_color=post_color,
            post_palette=post_palette,
            post_color_norm=post_color_norm,
            ax=ax,
            **syn_kwargs,
        )
    return axes


def single_panel_figure(
    data_bounds_min: np.ndarray,
    data_bounds_max: np.ndarray,
    units_per_inch: float,
    despine: bool = True,
    dpi: Optional[float] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """Create a single panel figure with precise unit-based sizing.

    Parameters
    ----------
    data_bounds_min : np.ndarray
        2-element array [x_min, y_min] of data bounds
    data_bounds_max : np.ndarray
        2-element array [x_max, y_max] of data bounds
    units_per_inch : float
        Number of data units per inch for scaling
    despine : bool, default True
        Whether to remove axis spines and ticks for clean appearance
    dpi : float, optional
        Dots per inch for figure resolution. If None, uses matplotlib default.

    Returns
    -------
    tuple of (plt.Figure, plt.Axes)
        Figure and axes objects with correct unit scaling

    Examples
    --------
    >>> bounds_min = np.array([0, 0])
    >>> bounds_max = np.array([100, 50])
    >>> fig, ax = create_single_panel_figure(bounds_min, bounds_max, 10)
    >>> # Creates 10" x 5" figure with 10 units per inch
    """
    data_bounds_min = np.asarray(data_bounds_min)
    data_bounds_max = np.asarray(data_bounds_max)

    # Calculate data extents
    data_width = data_bounds_max[0] - data_bounds_min[0]
    data_height = data_bounds_max[1] - data_bounds_min[1]

    # Convert to figure size in inches
    fig_width = data_width / units_per_inch
    fig_height = data_height / units_per_inch

    # Create figure and axis
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])  # Fill entire figure

    # Set data limits and aspect ratio
    ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
    ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
    ax.set_aspect("equal")

    if despine:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.xaxis.set_ticks([])
        ax.yaxis.set_ticks([])
    return fig, ax


def multi_panel_figure(
    data_bounds_min: np.ndarray,
    data_bounds_max: np.ndarray,
    units_per_inch: float,
    layout: Literal["side_by_side", "stacked", "three_panel"],
    gap_inches: float = 0.5,
    despine: bool = True,
    dpi: Optional[float] = None,
) -> Tuple[plt.Figure, Dict[str, plt.Axes]]:
    """Create multi-panel figure with precise unit-based sizing and alignment.

    Parameters
    ----------
    data_bounds_min : np.ndarray
        3-element array [x_min, y_min, z_min] of data bounds
    data_bounds_max : np.ndarray
        3-element array [x_max, y_max, z_max] of data bounds
    units_per_inch : float
        Number of data units per inch for scaling
    layout : {"side_by_side", "stacked", "three_panel"}
        Layout configuration:
        - "side_by_side": xy | zy (horizontal)
        - "stacked": xz over xy (vertical)
        - "three_panel": L-shaped (xy bottom-left, xz top-left, zy bottom-right)
    gap_inches : float, default 0.5
        Gap between panels in inches
    despine : bool, default True
        Whether to remove axis spines and ticks for clean appearance
    dpi : float, optional
        Dots per inch for figure resolution. If None, uses matplotlib default.

    Returns
    -------
    tuple of (plt.Figure, dict of plt.Axes)
        Figure and dictionary of axes keyed by projection.
        - "side_by_side": {"xy": xy_ax, "zy": zy_ax}
        - "stacked": {"xz": xz_ax, "xy": xy_ax}
        - "three_panel": {"xy": xy_ax, "xz": xz_ax, "zy": zy_ax}

    Examples
    --------
    >>> bounds_min = np.array([0, 0, 0])
    >>> bounds_max = np.array([100, 50, 75])
    >>> fig, axes_dict = create_multi_panel_figure(bounds_min, bounds_max, 10, "side_by_side")
    >>> xy_ax, zy_ax = axes_dict["xy"], axes_dict["zy"]
    """
    data_bounds_min = np.asarray(data_bounds_min)
    data_bounds_max = np.asarray(data_bounds_max)

    # Calculate data extents for each dimension
    x_extent = data_bounds_max[0] - data_bounds_min[0]
    y_extent = data_bounds_max[1] - data_bounds_min[1]
    z_extent = data_bounds_max[2] - data_bounds_min[2]

    # Convert to sizes in inches
    x_inches = x_extent / units_per_inch
    y_inches = y_extent / units_per_inch
    z_inches = z_extent / units_per_inch

    if layout == "side_by_side":
        # xy | zy layout
        xy_width, xy_height = x_inches, y_inches
        zy_width, zy_height = z_inches, y_inches

        fig_width = xy_width + gap_inches + zy_width
        fig_height = max(xy_height, zy_height)

        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)

        # xy panel (left)
        xy_left = 0
        xy_bottom = (fig_height - xy_height) / 2  # Center vertically
        xy_ax = fig.add_axes(
            [
                xy_left / fig_width,
                xy_bottom / fig_height,
                xy_width / fig_width,
                xy_height / fig_height,
            ]
        )
        xy_ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
        xy_ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
        xy_ax.set_aspect("equal")

        # zy panel (right)
        zy_left = xy_width + gap_inches
        zy_bottom = (fig_height - zy_height) / 2  # Center vertically
        zy_ax = fig.add_axes(
            [
                zy_left / fig_width,
                zy_bottom / fig_height,
                zy_width / fig_width,
                zy_height / fig_height,
            ]
        )
        zy_ax.set_xlim(data_bounds_min[2], data_bounds_max[2])
        zy_ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
        zy_ax.set_aspect("equal")
        if despine:
            for ax in [xy_ax, zy_ax]:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.spines["bottom"].set_visible(False)
                ax.xaxis.set_ticks([])
                ax.yaxis.set_ticks([])

        return fig, {"xy": xy_ax, "zy": zy_ax}

    elif layout == "stacked":
        # xz over xy layout
        xy_width, xy_height = x_inches, y_inches
        xz_width, xz_height = x_inches, z_inches

        fig_width = max(xy_width, xz_width)
        fig_height = xy_height + gap_inches + xz_height

        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)

        # xz panel (top)
        xz_left = (fig_width - xz_width) / 2  # Center horizontally
        xz_bottom = xy_height + gap_inches
        xz_ax = fig.add_axes(
            [
                xz_left / fig_width,
                xz_bottom / fig_height,
                xz_width / fig_width,
                xz_height / fig_height,
            ]
        )
        xz_ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
        xz_ax.set_ylim(data_bounds_min[2], data_bounds_max[2])
        xz_ax.set_aspect("equal")

        # xy panel (bottom)
        xy_left = (fig_width - xy_width) / 2  # Center horizontally
        xy_bottom = 0
        xy_ax = fig.add_axes(
            [
                xy_left / fig_width,
                xy_bottom / fig_height,
                xy_width / fig_width,
                xy_height / fig_height,
            ]
        )
        xy_ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
        xy_ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
        xy_ax.set_aspect("equal")
        if despine:
            for ax in [xy_ax, xz_ax]:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.spines["bottom"].set_visible(False)
                ax.xaxis.set_ticks([])
                ax.yaxis.set_ticks([])

        return fig, {"xz": xz_ax, "xy": xy_ax}

    elif layout == "three_panel":
        # L-shaped: xy (bottom-left), xz (top-left), zy (bottom-right)
        xy_width, xy_height = x_inches, y_inches
        xz_width, xz_height = x_inches, z_inches
        zy_width, zy_height = z_inches, y_inches

        # Calculate figure dimensions
        left_width = max(xy_width, xz_width)
        fig_width = left_width + gap_inches + zy_width
        fig_height = xy_height + gap_inches + xz_height

        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)

        # xy panel (bottom-left)
        xy_left = (left_width - xy_width) / 2  # Center in left column
        xy_bottom = 0
        xy_ax = fig.add_axes(
            [
                xy_left / fig_width,
                xy_bottom / fig_height,
                xy_width / fig_width,
                xy_height / fig_height,
            ]
        )
        xy_ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
        xy_ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
        xy_ax.set_aspect("equal")

        # xz panel (top-left)
        xz_left = (left_width - xz_width) / 2  # Center in left column
        xz_bottom = xy_height + gap_inches
        xz_ax = fig.add_axes(
            [
                xz_left / fig_width,
                xz_bottom / fig_height,
                xz_width / fig_width,
                xz_height / fig_height,
            ]
        )
        xz_ax.set_xlim(data_bounds_min[0], data_bounds_max[0])
        xz_ax.set_ylim(data_bounds_min[2], data_bounds_max[2])
        xz_ax.set_aspect("equal")

        # zy panel (bottom-right, aligned with xy panel)
        zy_left = left_width + gap_inches
        zy_bottom = 0  # Align with xy panel bottom
        zy_ax = fig.add_axes(
            [
                zy_left / fig_width,
                zy_bottom / fig_height,
                zy_width / fig_width,
                zy_height / fig_height,
            ]
        )
        zy_ax.set_xlim(data_bounds_min[2], data_bounds_max[2])
        zy_ax.set_ylim(data_bounds_min[1], data_bounds_max[1])
        zy_ax.set_aspect("equal")
        if despine:
            for ax in [xy_ax, xz_ax, zy_ax]:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.spines["bottom"].set_visible(False)
                ax.xaxis.set_ticks([])
                ax.yaxis.set_ticks([])
        return fig, {"xy": xy_ax, "xz": xz_ax, "zy": zy_ax}

    else:
        raise ValueError(
            f"Unknown layout '{layout}'. Choose from 'side_by_side', 'stacked', or 'three_panel'."
        )


def add_scale_bar(
    ax: plt.Axes,
    length: float,
    position: Tuple[float, float] = (0.05, 0.05),
    color: str = "black",
    linewidth: float = 10.0,
    orientation: Literal["h", "v", "horizontal", "vertical"] = "h",
    feature: Optional[str] = None,
    feature_offset: float = 0.01,
    fontsize: float = 10,
) -> None:
    """Add a scale bar to an axis with precise positioning.

    Parameters
    ----------
    ax : plt.Axes
        Matplotlib axes to add scale bar to
    length : float
        Length of scale bar in data units
    position : tuple of float, default (0.05, 0.05)
        Starting position as fraction of axis dimensions (x_frac, y_frac).
        (0, 0) is bottom-left, (1, 1) is top-right.
    color : str, default "black"
        Color of the scale bar line
    linewidth : float, default 3.0
        Width of the scale bar line in points
    feature : str, optional
        Text feature for the scale bar (e.g., "100 μm")
    feature_offset : float, default 0.01
        Vertical offset for feature as fraction of axis height
    fontsize : float, default 10
        Font size for scale bar feature

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.plot([0, 100], [0, 50])
    >>> add_scale_bar(ax, length=20, position=(0.1, 0.1), feature="20 units")

    >>> # Add scale bar to morphology plot
    >>> fig, ax = single_panel_figure(bounds_min, bounds_max, 10)
    >>> plot_skeleton(skeleton, ax=ax)
    >>> add_scale_bar(ax, length=50, position=(0.8, 0.05), feature="50 μm")
    """
    # Get axis data limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Calculate axis data ranges
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]

    # Convert fractional position to data coordinates
    x_start = xlim[0] + position[0] * x_range
    y_start = ylim[0] + position[1] * y_range

    # Calculate end position (scale bar extends to the right)
    match orientation:
        case "h" | "horizontal":
            x_end = x_start + length
            y_end = y_start
        case "v" | "vertical":
            x_end = x_start
            if ax.yaxis_inverted():
                y_end = y_start - length
            else:
                y_end = y_start + length

    # Draw the scale bar line
    ax.plot(
        [x_start, x_end],
        [y_start, y_end],
        color=color,
        linewidth=linewidth,
        solid_capstyle="butt",
    )

    # Add feature if provided
    if feature is not None:
        # Position feature above the center of the scale bar
        match orientation:
            case "h" | "horizontal":
                feature_x = x_start + length / 2
                feature_y = y_start + feature_offset * y_range
            case "v" | "vertical":
                if ax.yaxis_inverted():
                    feature_x = x_start + feature_offset * x_range
                    feature_y = y_start - length / 2
                else:
                    feature_x = x_start + feature_offset * x_range
                    feature_y = y_start + length / 2

        ax.text(
            feature_x,
            feature_y,
            feature,
            ha="center",
            va="bottom",
            color=color,
            fontsize=fontsize,
        )
