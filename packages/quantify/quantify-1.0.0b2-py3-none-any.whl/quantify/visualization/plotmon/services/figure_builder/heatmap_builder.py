"""
2D Heatmap figure builder for Plotmon: provides configuration and
rendering of 2D heatmaps using Bokeh.
"""

import logging

import numpy as np
from bokeh.models import (
    ColorBar,
    ColumnDataSource,
    DataRange1d,
    GlyphRenderer,
    HoverTool,
    LinearColorMapper,
    Title,
)
from bokeh.plotting import figure
from pydantic import BaseModel

from quantify.visualization.plotmon.services.figure_builder.base_figure_builder import (
    BaseFigureBuilder,
)
from quantify.visualization.plotmon.services.plotmon_service import TuidData


class HeatmapConfig(BaseModel):
    """Configuration parameters for a 2D heatmap figure."""

    image_key: str = "image"
    x_key: str = "x"
    y_key: str = "y"
    dw_key: str = "dw"
    dh_key: str = "dh"
    plot_name: str = "generic_heatmap"
    x_label: str = "X"
    y_label: str = "Y"
    z_label: str = "Z"
    x_units: str = ""
    y_units: str = ""
    z_units: str = ""
    title: str = "2D Heatmap"
    width: int = 750
    height: int = 600
    palette: str = "Viridis256"


class HeatmapFigureBuilder(BaseFigureBuilder):
    """
    Builds a 2D image placeholder, the given source is linked to the image data.
    If no TUID is selected or active, a placeholder image with NaN values is shown.
    """

    def build_figure(
        self,
        config: dict,
        sources: dict[str, ColumnDataSource],
        tuid_data: TuidData,
        ranges: dict[str, DataRange1d],
        fig: figure | None = None,
    ) -> figure:
        """
        Build a 2D heatmap figure for finished experiments.
        Returns a Bokeh figure object.
        """
        cfg = self._extract_config(config)  # returns HeatmapConfig instance
        source_tuid = self._select_source_tuid(tuid_data)
        source = self._get_source(source_tuid, cfg, sources)
        ranges.clear()  # heatmaps do not share ranges
        if fig is None:
            fig = figure(
                title=cfg.title + (f" - TUID: {source_tuid}" if source_tuid else ""),
                x_axis_label=f"{cfg.x_label} ({cfg.x_units})",
                y_axis_label=f"{cfg.y_label} ({cfg.y_units})",
                min_width=cfg.width,
                min_height=cfg.height,
                output_backend="webgl",
                background_fill_color="#ffffff",
                border_fill_color="#ffffff",
                outline_line_color="#e1e5e9",
                sizing_mode="stretch_width",
                match_aspect=True,
            )
        else:
            if fig.title is not None:
                if isinstance(fig.title, Title):
                    fig.title.text = cfg.title + (
                        f" - TUID: {source_tuid}" if source_tuid else ""
                    )
                else:
                    fig.title = cfg.title + (
                        f" - TUID: {source_tuid}" if source_tuid else ""
                    )
            fig.xaxis.axis_label = f"{cfg.x_label} ({cfg.x_units})"
            fig.yaxis.axis_label = f"{cfg.y_label} ({cfg.y_units})"
            if isinstance(fig.renderers[0], GlyphRenderer):
                fig.renderers[0].data_source = source
            return fig

        color_mapper = LinearColorMapper(palette=cfg.palette)
        image_renderer = fig.image(
            image=cfg.image_key,
            x=cfg.x_key,
            y=cfg.y_key,
            dw=cfg.dw_key,
            dh=cfg.dh_key,
            source=source,
        )
        image_renderer.glyph.color_mapper = color_mapper

        color_bar = ColorBar(color_mapper=color_mapper, padding=3)
        color_bar.title = f"{cfg.z_label} ({cfg.z_units})"
        color_bar.title_text_font_style = "normal"
        color_bar.title_standoff = 5
        color_bar.title_text_font_size = "15px"
        color_bar.title_text_baseline = "middle"
        fig.add_layout(color_bar, "right")

        hover = HoverTool(
            renderers=[image_renderer],
            tooltips=[
                ("TUID", "@tuid"),
                (f"{cfg.x_label} ({cfg.x_units})", "$x"),
                (f"{cfg.y_label} ({cfg.y_units})", "$y"),
                (f"{cfg.z_label} ({cfg.z_units})", f"@{cfg.image_key}"),
            ],
        )
        fig.add_tools(hover)
        return fig

    @staticmethod
    def _select_source_tuid(tuid_data: TuidData) -> str | None:
        """Select the TUID to use for the heatmap source."""
        selected_tuid = tuid_data.selected_tuid.get(
            tuid_data.session_id, tuid_data.selected_tuid.get(-1, "")
        )

        if selected_tuid != "":
            return selected_tuid
        if tuid_data.active_tuid != "":
            return tuid_data.active_tuid
        return None

    @staticmethod
    def _extract_config(config: dict) -> HeatmapConfig:
        """Extract and group config values with defaults using Pydantic BaseModel."""
        return HeatmapConfig(**config)

    @staticmethod
    def _get_source(
        source_tuid: str | None,
        cfg: HeatmapConfig,
        sources: dict[str, ColumnDataSource],
    ) -> ColumnDataSource:
        """Get the ColumnDataSource for the heatmap, or a placeholder if not found."""
        if source_tuid:
            source_name = f"{source_tuid}_{cfg.plot_name}"
            source = sources.get(source_name)
            if source is None:
                logging.warning(
                    "ColumnDataSource for '%s' not found in sources. "
                    "Available sources: %s",
                    source_name,
                    list(sources.keys()),
                )
                source = sources.get(cfg.plot_name)  # fallback to base source

            if source is not None:
                return source

        # Return placeholder source if no TUID selected or source missing
        placeholder_image = np.full((1, 1), np.nan)
        return ColumnDataSource(
            data={
                cfg.image_key: [placeholder_image],
                cfg.x_key: [0],
                cfg.y_key: [0],
                cfg.dw_key: [1],
                cfg.dh_key: [1],
                "tuid": [""],
            }
        )
