"""Heatmap data processor for Plotmon: processes heatmap data for visualization."""

import logging
from collections.abc import Sequence
from typing import Any

import numpy as np
from pydantic import BaseModel

from quantify.visualization.plot_interpolation import interpolate_heatmap


class HeatmapKeys(BaseModel):
    """
    A container class for constant keys used in heatmap data processing.

    Attributes:
        image_key (str): Key for the heatmap image data.
        x_key (str): Key for the x-axis values.
        y_key (str): Key for the y-axis values.
        dw_key (str): Key for the width delta.
        dh_key (str): Key for the height delta.
        tuid_key (str): Key for the unique identifier.
        tuid (str): Value for the unique identifier (default is an empty string).

    """

    image_key: str = "image"
    x_key: str = "x"
    y_key: str = "y"
    dw_key: str = "dw"
    dh_key: str = "dh"
    tuid_key: str = "tuid"
    tuid: Sequence[Any] = ""


def process_heatmap_data(
    data: dict[str, Sequence[Any]], config: dict
) -> dict[str, Sequence[Any]]:
    """
    Process heatmap data based on its structure and configuration.
    Handles uniform grids, uniform settables, and interpolated heatmaps.

    Parameters
    ----------
    data : dict[str, Sequence[Any]]
        Input data containing heatmap information.
    config : dict
        Configuration dictionary with keys for data extraction.

    Returns
    -------
    dict[str, Sequence[Any]]
        Processed heatmap data ready for visualization.

    """
    keys = HeatmapKeys(
        image_key=config.get("image_key", "image"),
        x_key=config.get("x_key", "x"),
        y_key=config.get("y_key", "y"),
        dw_key=config.get("dw_key", "dw"),
        dh_key=config.get("dh_key", "dh"),
        tuid_key=config.get("tuid_key", "tuid"),
        tuid=data.get("tuid", ""),  # type: ignore
    )

    def extract_array(key: str) -> np.ndarray:
        return np.array(data.get(key, [np.nan]))

    x = extract_array(keys.x_key)
    y = extract_array(keys.y_key)
    z = extract_array(keys.image_key)

    xlen, ylen = x.shape[0], y.shape[0]
    uniform_grid = data.get("uniform_grid", False)
    uniform_settables = data.get("uniform_settables", False)

    if uniform_grid and xlen and ylen:
        return _process_uniform_grid_heatmap(x, y, z, xlen, ylen, keys)
    if uniform_settables:
        return _process_uniform_settables_heatmap(x, y, z, keys)

    has_data = len(x) > 0 and len(y) > 0 and len(z) > 0
    is_uniform = np.all(x == x[0]) or np.all(y == y[0])
    is_small = len(x) < 8 or len(y) < 8
    if has_data and not (is_uniform or is_small):
        return _process_interpolated_heatmap(x, y, z, keys)

    logging.warning(
        "Heatmap data is insufficient or unsuitable for interpolation. "
        "Returning a placeholder image. Data lengths - x: %d, y: %d, z: %d",
        len(x),
        len(z),
        len(y),
    )
    placeholder_image = np.full((1, 1), np.nan)
    return _build_result(placeholder_image, x, y, keys)


def _build_result(
    image: np.ndarray, x: np.ndarray, y: np.ndarray, keys: HeatmapKeys
) -> dict[str, Sequence[Any]]:
    return {
        keys.image_key: [image],
        keys.x_key: [np.min(x)],
        keys.y_key: [np.min(y)],
        keys.dw_key: [np.max(x) - np.min(x)],
        keys.dh_key: [np.max(y) - np.min(y)],
        keys.tuid_key: [
            keys.tuid
            if isinstance(keys.tuid, str)
            else keys.tuid[0]
            if keys.tuid
            else ""
        ],
    }


def _process_uniform_grid_heatmap(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, xlen: int, ylen: int, keys: HeatmapKeys
) -> dict[str, Sequence[Any]]:
    length = xlen * ylen
    z_vals = np.full((length,), np.nan)
    z_vals[: len(z)] = z
    z_matrix = np.reshape(z_vals, (xlen, ylen), order="F").T
    return _build_result(z_matrix, x, y, keys)


def _process_uniform_settables_heatmap(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, keys: HeatmapKeys
) -> dict[str, Sequence[Any]]:
    shape = (len(x), len(y))
    z_matrix = np.full(shape, np.nan)
    np.fill_diagonal(z_matrix, z)
    z_matrix = np.reshape(z_matrix, shape, order="F").T
    return _build_result(z_matrix, x, y, keys)


def _process_interpolated_heatmap(
    x: np.ndarray, y: np.ndarray, z: np.ndarray, keys: HeatmapKeys
) -> dict[str, Sequence[Any]]:
    x_grid, y_grid, z_grid = interpolate_heatmap(x=x, y=y, z=z, interp_method="linear")
    return _build_result(z_grid, x_grid, y_grid, keys)
