"""
plotmon_service module: Contains configuration and
service containers for Plotmon applications.
Provides dataclasses for managing graph building and caching services.
"""

from dataclasses import dataclass

from bokeh.core.types import ID

from quantify.visualization.plotmon.caching.base_cache import BaseCache


@dataclass
class TuidData:
    """
    A container for TUID related data in the Plotmon application.

    Attributes
    ----------
    tuids : set[str]
        A set of all TUIDs currently known to the application.
    active_tuids : set[str]
        A set of TUIDs that are currently active (e.g., experiments in progress).
    selected_tuid : str
        A set of TUIDs that are currently selected by the user for detailed viewing.

    """

    tuids: set[str]
    active_tuid: str
    selected_tuid: dict[ID | int, str]
    session_id: ID | int = -1  # Default session ID for non-session-specific data


@dataclass
class PlotmonConfig:
    """
    graph_configs: A two-dimensional list representing the configuration of
    graphs to be displayed.
    Each inner list corresponds to a row of graphs,
    and each dictionary within the inner list contains
    the configuration for an individual graph in that row.
    The outer list represents the columns of the graph layout.

    Example:
    [
        [ {graph1_config}, {graph2_config} ],  # Row 1
        [ {graph3_config} ]                    # Row 2
    ]

    """

    data_source_name: str
    graph_configs: list[list[dict]]
    title: str = "Plotmon App"


@dataclass
class PlotmonServices:
    """
    Service container for Plotmon,
    providing graph building and caching functionality.
    """

    cache: BaseCache
