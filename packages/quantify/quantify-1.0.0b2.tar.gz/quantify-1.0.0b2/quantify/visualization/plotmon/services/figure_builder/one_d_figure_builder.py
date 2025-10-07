"""
One-dimensional figure builder for Plotmon: provides configuration and
rendering of 1D experiment plots using Bokeh.
"""

from bokeh.models import ColumnDataSource, DataRange1d, HoverTool
from bokeh.plotting import figure
from pydantic import BaseModel

from quantify.visualization.plotmon.services.figure_builder.base_figure_builder import (
    BaseFigureBuilder,
)
from quantify.visualization.plotmon.services.plotmon_service import TuidData
from quantify.visualization.plotmon.utils.colors import Colors


class OneDFigureConfig(BaseModel):
    """Configuration parameters for a 1D figure."""

    x_label: str = "X-axis"
    y_label: str = "Y-axis"
    x_units: str = "units"
    y_units: str = "units"
    title: str = "1D Plot"
    width: int = 300
    height: int = 300
    plot_name: str = "generic_plot"
    inactive_alpha: float = 0.3
    active_alpha: float = 1.0
    color: str = Colors.BLUE.value
    selection_color: str = Colors.BLUE.value
    nonselection_color: str = Colors.ORANGE.value
    nonselection_alpha: float = 0.08
    hover_color: str = Colors.ORANGE.value
    hover_alpha: float = 1.0
    x_key: str = "x"
    y_key: str = "y"
    legend_title: str = "Experiments"
    legend_location: tuple[float, float] | str = "top_right"
    legend_click_policy: str = "hide"


class OneDFigureBuilder(BaseFigureBuilder):
    """Builds a 1D figure using Bokeh, highlighting active and selected TUIDs."""

    def build_figure(
        self,
        config: dict,
        sources: dict[str, ColumnDataSource],
        tuid_data: TuidData,
        ranges: dict[str, DataRange1d],
        fig: figure | None = None,
    ) -> figure:
        """
        Build a 1D figure for experiments, highlighting active and selected TUIDs.
        Returns a Bokeh figure object.
        """
        cfg = self._extract_config(config)
        if fig is None:
            p = figure(
                title=cfg.title,
                x_axis_label=f"{cfg.x_label} ({cfg.x_units})",
                y_axis_label=f"{cfg.y_label} ({cfg.y_units})",
                min_width=cfg.width,
                min_height=cfg.height,
                x_range=ranges["x_range"],
                y_range=ranges["y_range"],
                output_backend="webgl",
                sizing_mode="stretch_width",
                background_fill_color="#ffffff",
                border_fill_color="#ffffff",
                outline_line_color="#e1e5e9",
            )
        else:
            p = fig
            # Remove all renderers (lines, scatters, etc.)
            p.renderers = []
            # Optionally, remove tools if you want to reset them:
            p.tools = []

        selected_tuid = tuid_data.selected_tuid.get(
            tuid_data.session_id, tuid_data.selected_tuid.get(-1, "")
        )
        active_tuid = tuid_data.active_tuid

        # Prepare data for multi_line
        xs, ys, tuid_labels = [], [], []
        for tuid in tuid_data.tuids:
            source_name = f"{tuid}_{cfg.plot_name}"
            source = sources.get(source_name)
            if source is None:
                raise ValueError(
                    f"""Data source '{source_name}' not found in provided sources.
                    Available: {list(sources.keys())}"""
                )
            xs.append(list(source.data[cfg.x_key]))
            ys.append(list(source.data[cfg.y_key]))
            tuid_labels.append(tuid)

        # Multi-line for all tuids (inactive alpha)
        multi_source = ColumnDataSource(data=dict(xs=xs, ys=ys, tuid=tuid_labels))
        glyph = p.multi_line(
            xs="xs",
            ys="ys",
            source=multi_source,
            line_width=2,
            alpha=cfg.inactive_alpha,
            color=cfg.color,
            legend_label="All TUIDs",
            nonselection_alpha=cfg.nonselection_alpha,
            nonselection_color=cfg.nonselection_color,
            hover_alpha=cfg.hover_alpha,
            hover_color=cfg.hover_color,
        )

        # Highlighted line for selected/active tuid
        highlight_tuid = active_tuid if active_tuid else selected_tuid
        if highlight_tuid:
            source_name = f"{highlight_tuid}_{cfg.plot_name}"
            source = sources.get(source_name)
            if source is None:
                raise ValueError(
                    f"""Data source '{source_name}' not found in provided sources.
                    Available: {list(sources.keys())}"""
                )
            p.line(
                x=cfg.x_key,
                y=cfg.y_key,
                source=source,
                legend_label=highlight_tuid,
                line_width=2,
                alpha=cfg.active_alpha,
                color=cfg.selection_color,
                selection_color=cfg.selection_color,
                nonselection_color=cfg.nonselection_color,
                nonselection_alpha=cfg.nonselection_alpha,
                hover_color=cfg.hover_color,
                hover_alpha=cfg.hover_alpha,
            )
            p.scatter(
                x=cfg.x_key,
                y=cfg.y_key,
                source=source,
                marker="circle",
                color=cfg.selection_color,
                size=8,
                fill_alpha=cfg.active_alpha,
                line_alpha=cfg.active_alpha,
                selection_alpha=1.0,
                selection_color=cfg.selection_color,
                nonselection_alpha=cfg.nonselection_alpha,
                nonselection_color=cfg.nonselection_color,
                hover_alpha=cfg.hover_alpha,
                hover_color=cfg.hover_color,
            )

        hover = HoverTool(
            renderers=[glyph],
            tooltips=[("TUID", "@tuid")],
        )
        p.add_tools(hover)

        return p

    @staticmethod
    def _extract_config(config: dict) -> OneDFigureConfig:
        """Extract and group config values with defaults using dataclass."""
        return OneDFigureConfig(**config)
