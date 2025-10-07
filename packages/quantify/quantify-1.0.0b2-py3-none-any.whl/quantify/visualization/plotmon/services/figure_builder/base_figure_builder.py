"""Abstract base class for figure builders."""

from abc import ABC, abstractmethod
from enum import Enum

from bokeh.models import ColumnDataSource, DataRange1d
from bokeh.plotting import figure

from quantify.visualization.plotmon.services.plotmon_service import TuidData


class PlotType(Enum):
    """Enumeration of supported plot types."""

    ONE_D = "1d"
    HEATMAP = "heatmap"
    ONE_D_MULTILINE = "1d_multiline"

    @staticmethod
    def from_str(label: str) -> "PlotType":
        """Convert a string to a PlotType enum member."""
        match label.lower():
            case "1d":
                return PlotType.ONE_D
            case "heatmap":
                return PlotType.HEATMAP
            case "1d_multiline":
                return PlotType.ONE_D_MULTILINE
            case _:
                raise ValueError(f"Unknown plot type: {label}")


class BaseFigureBuilder(ABC):
    """Abstract base class for building different types of figures."""

    @abstractmethod
    def build_figure(
        self,
        config: dict,
        sources: dict[str, ColumnDataSource],
        tuid_data: TuidData,
        ranges: dict[str, DataRange1d],
        fig: figure | None,
    ) -> figure:
        """
        Build a figure based on the provided configuration and
        plot data from the sources.

        Parameters
        ----------
        config : dict
            Configuration dictionary for the figure.
        sources : dict[str, ColumnDataSource]
            Dictionary of data sources to be used in the figure.
        tuid_data : TuidData
            TUID related data for the application.
        ranges : dict[str, Range]
            Shared x and y ranges for the figure.
        fig : figure | None
            Existing figure to update, or None to create a new one.

        Returns
        -------
        A Bokeh Figure object.

        """
