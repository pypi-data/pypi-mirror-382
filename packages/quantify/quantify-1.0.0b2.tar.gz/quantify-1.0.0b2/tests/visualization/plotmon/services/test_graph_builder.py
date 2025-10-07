# File: /home/kiki/quantify/tests/visualization/plotmon/services/test_graph_builder.py

from unittest import mock

import pytest
from bokeh.models import Column, ColumnDataSource, DataRange1d, Row
from bokeh.models.widgets import DataTable
from bokeh.plotting import figure

from quantify.visualization.plotmon.services import graph_builder
from quantify.visualization.plotmon.services.plotmon_service import TuidData


class DummyFigureBuilder:
    def build_figure(self, config, *_):
        f = mock.Mock(spec=figure)
        f.id = f"{config.get('plot_name', 'dummy')}_id"
        return f


@pytest.fixture
def patch_figure_builder(monkeypatch):
    monkeypatch.setattr(
        graph_builder.FigureBuilderFactory,
        "get_builder",
        lambda _: DummyFigureBuilder(),
    )


def test_make_source_name_empty_tuid():
    assert graph_builder._make_source_name("", "plot1") == "plot1"


def test_make_source_name_with_tuid():
    assert graph_builder._make_source_name("TUID123", "plot1") == "TUID123_plot1"


def test_create_shared_ranges_basic():
    configs = [[{"x_key": "x", "y_key": "y"}], [{"x_key": "x2", "y_key": "y2"}]]
    ranges = graph_builder._create_shared_ranges(configs)
    assert isinstance(ranges["x"], DataRange1d)
    assert isinstance(ranges["y"], DataRange1d)
    assert isinstance(ranges["x2"], DataRange1d)
    assert isinstance(ranges["y2"], DataRange1d)


def test_create_rows_creates_rows():
    configs = [
        [{"plot_type": "1d", "plot_name": "plot1", "x_key": "x", "y_key": "y"}],
        [{"plot_type": "1d", "plot_name": "plot2", "x_key": "x2", "y_key": "y2"}],
    ]
    sources = {
        "tuid_1_plot1": ColumnDataSource(data={"x": [], "y": [], "tuid": []}),
        "tuid_2_plot1": ColumnDataSource(data={"x": [], "y": [], "tuid": []}),
        "tuid_1_plot2": ColumnDataSource(data={"x2": [], "y2": [], "tuid": []}),
        "tuid_2_plot2": ColumnDataSource(data={"x2": [], "y2": [], "tuid": []}),
    }
    tuid_data = TuidData(
        tuids=["tuid_1", "tuid_2"],
        selected_tuid={-1: "tuid_1"},
        active_tuid="",
        session_id=-1,
    )
    rows = graph_builder._create_rows(configs, sources, tuid_data)
    assert isinstance(rows, list)
    assert all(isinstance(row, Row) for row in rows)
    assert len(rows) == 2


def test_build_figure_calls_builder(monkeypatch):
    monkeypatch.setattr(
        graph_builder.FigureBuilderFactory,
        "get_builder",
        lambda _: DummyFigureBuilder(),
    )
    config = {"plot_type": "1d", "plot_name": "plot1"}
    sources = {"plot1_plot1": ColumnDataSource(data={"x": [], "y": [], "tuid": []})}
    tuid_data = TuidData(
        tuids=["plot1"], selected_tuid={-1: "plot1"}, active_tuid="", session_id=-1
    )
    ranges = {"x_range": DataRange1d(), "y_range": DataRange1d()}
    fig = None
    result = graph_builder._build_figure(config, sources, tuid_data, ranges, fig)
    assert hasattr(result, "id")
    assert result.id == "plot1_id"


def test_build_layout_returns_column(monkeypatch):
    dummy_table = DataTable()
    monkeypatch.setattr(
        graph_builder.table_builder, "create_table", lambda *_, **__: dummy_table
    )
    configs = [[{"plot_type": "1d", "plot_name": "plot1", "x_key": "x", "y_key": "y"}]]
    # The key should be "plot1_plot1" to match what build_layout expects
    sources = {"plot1_plot1": ColumnDataSource(data={"x": [], "y": [], "tuid": []})}
    tuid_data = TuidData(
        tuids=["plot1"],
        selected_tuid={-1: "plot1"},
        active_tuid="",
        session_id=-1,
    )
    meta_data = {"plot1": {}}

    def on_select():
        pass

    layout = graph_builder.build_layout(
        configs, sources, tuid_data, meta_data, on_select
    )
    assert isinstance(layout, Column)
    assert any(isinstance(child, Column) for child in layout.children)
    assert any(isinstance(child, Row) for child in layout.children[1:])


def test_create_sources_1d_and_heatmap():
    configs = [
        [
            {"plot_type": "1d", "plot_name": "plot1", "x_key": "x", "y_key": "y"},
            {
                "plot_type": "heatmap",
                "plot_name": "heatmap1",
                "image_key": "image",
                "x_key": "x",
                "y_key": "y",
                "dw_key": "dw",
                "dh_key": "dh",
            },
        ]
    ]
    sources = graph_builder.create_sources(configs, tuid="TUID")
    assert "TUID_plot1" in sources
    assert "TUID_heatmap1" in sources
    assert "table_source" in sources
    assert isinstance(sources["TUID_plot1"], ColumnDataSource)
    assert isinstance(sources["TUID_heatmap1"], ColumnDataSource)
    assert isinstance(sources["table_source"], ColumnDataSource)


def test_create_sources_raises_on_invalid_plot_type():
    configs = [[{"plot_type": "unknown", "plot_name": "plot1"}]]
    with pytest.raises(ValueError):
        graph_builder.create_sources(configs, tuid="TUID")
