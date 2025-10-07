"""
Module for processing and transforming data for heatmap and other plot types
in the quantify plotting monitor service.

Provides functions to reshape, interpolate, and prepare data for visualization,
including support for uniform grids, uniform settables, and interpolation.
"""

import logging
from collections.abc import Sequence
from typing import Any

from quantify.visualization.plotmon.services.data_processors.heatmap_processor import (
    process_heatmap_data,
)
from quantify.visualization.plotmon.services.graph_builder import PlotType


def process(
    plot_type: PlotType, data: dict[str, Sequence[Any]], config: dict
) -> dict[str, Sequence[Any]]:
    """
    Process incoming data based on plot type and configuration.
    Currently, only heatmap requires special processing.
    """
    if plot_type == PlotType.HEATMAP:
        return process_heatmap_data(data, config)
    # Add more plot types as needed
    return data


def extract_data(
    old_data: dict[int, dict[str, Sequence[Any]]], plot_type: PlotType, config: dict
) -> dict[str, Sequence[Any]]:
    """
    Extract and combine data from old and new data dictionaries.
    This is particularly useful for heatmaps where we want to accumulate data over time.
    """
    data = {}

    prev_index = None
    for index, value in sorted(old_data.items()):
        if prev_index is None:
            prev_index = index - 1
        elif index != prev_index + 1:
            # Log a warning if indices are not sequential
            logging.warning(
                "Non-sequential indices in cached data for %s: %s followed by %s",
                old_data,
                prev_index,
                index,
            )

        prev_index = index
        for k, v in value.items():
            if plot_type == PlotType.ONE_D:
                data.setdefault(k, []).append(v)
                continue
            if plot_type == PlotType.HEATMAP:
                if k == config.get("image_key", "z"):
                    # For heatmap images, we want to keep them as a list of 2D arrays
                    data.setdefault(k, []).extend(v)
                else:
                    data[k] = v
    return data
