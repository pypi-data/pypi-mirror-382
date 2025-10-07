from unittest import mock

import pytest
from bokeh.models import ColumnDataSource

from quantify.visualization.plotmon.plotmon_app import PlotmonApp
from quantify.visualization.plotmon.services.figure_builder.base_figure_builder import (
    PlotType,
)
from quantify.visualization.plotmon.utils.commands import CommandType


@pytest.fixture
def mock_config():
    return mock.Mock(
        graph_configs=[[{"plot_name": "test_plot", "plot_type": "1d", "x_key": "x"}]],
        data_source_name="ds",
        title="Test Title",
    )


@pytest.fixture
def mock_services():
    cache = mock.Mock()
    cache.get.return_value = {}
    cache.get_all.return_value = {}
    cache.set.return_value = None
    return mock.Mock(cache=cache)


@pytest.fixture
def app(mock_config, mock_services):
    return PlotmonApp(config=mock_config, services=mock_services)


def test_initialization_sets_base_sources(mock_config, mock_services):
    with mock.patch(
        "quantify.visualization.plotmon.services.session_manager.SessionManager.add_base_source"
    ) as add_base_source_mock:
        PlotmonApp(config=mock_config, services=mock_services)
        assert add_base_source_mock.called


def test_modify_document_sets_layout_and_callbacks(app):
    doc = mock.Mock()
    app.session_manager.get_doc_and_sources = mock.Mock(return_value=(doc, {}, None))
    app.session_manager.get_current_session_id = mock.Mock(return_value=1)
    app.session_manager.get_layout = mock.Mock(return_value=mock.Mock())
    app.session_manager.set_layout = mock.Mock(return_value=None)
    app.serve = mock.Mock()
    app.initialize_sources_from_cache = mock.Mock()
    app._check_for_base_sources = mock.Mock()
    app.modify_document(doc)
    app.serve.assert_called()
    app.initialize_sources_from_cache.assert_called()


def test_enqueue_data_puts_to_queue(app):
    app.data_queue = mock.Mock()
    app.enqueue_data("plot", "tuid", {"x": [1]})
    app.data_queue.put.assert_called_with(("plot", "tuid", {"x": [1]}))


def test_start_experiment_updates_tuid_and_cache(app, mock_services):
    app._tuid_data.tuids = set()
    app._tuid_data.selected_tuid = {}
    app.session_manager.update_sources = mock.Mock()
    app._re_render = mock.Mock()
    mock_services.cache.get.return_value = {}
    mock_services.cache.set.return_value = None
    app.start_experiment("tuid1", "2024-01-01")
    assert "tuid1" in app._tuid_data.tuids
    assert app._tuid_data.active_tuid == "tuid1"
    app.session_manager.update_sources.assert_called()
    app._re_render.assert_called()
    mock_services.cache.set.assert_called()


def test_end_experiment_updates_selected_and_cache(app, mock_services):
    app._tuid_data.selected_tuid = {}
    app.session_manager.get_all_session_ids = mock.Mock(return_value=[1, 2])
    app._re_render = mock.Mock()
    mock_services.cache.get.return_value = {}
    mock_services.cache.set.return_value = None
    app.end_experiment("tuid2", "2024-01-02")
    assert app._tuid_data.selected_tuid[-1] == "tuid2"
    assert app._tuid_data.active_tuid == ""
    assert app._tuid_data.selected_tuid[1] == "tuid2"
    assert app._tuid_data.selected_tuid[2] == "tuid2"
    app._re_render.assert_called()
    mock_services.cache.set.assert_called()


def test_get_plot_names_returns_names(app):
    names = app._get_plot_names()
    assert names == ["test_plot"]


def test_get_source_returns_source_and_name(app):
    sources = {"tuid_test_plot": "source_obj"}
    source, name = app._get_source(sources, "test_plot", "tuid")
    assert source == "source_obj"
    assert name == "tuid_test_plot"


def test_make_cache_key_and_source_name(app):
    assert app._make_cache_key("plot", "tuid") == "ds_tuid_plot"
    assert app._make_source_name("tuid", "plot") == "tuid_plot"


def test_get_plot_type_returns_type_and_config(app):
    plot_type, config = app._get_plot_type("test_plot")
    assert plot_type.name.lower() == "one_d"
    assert config["plot_name"] == "test_plot"


def test_get_plot_type_raises_for_unknown(app):
    with pytest.raises(ValueError):
        app._get_plot_type("unknown_plot")


def test_get_current_timestamp_format(app):
    ts = app.get_current_timestamp()
    assert isinstance(ts, str)
    assert "_" in ts


def test_add_event_next_tick_calls_next_tick(app):
    doc = mock.Mock()
    app.session_manager.all_sessions = mock.Mock(return_value=[(1, doc)])
    app._process_event = mock.Mock()
    app.add_event_next_tick("event", "data")
    doc.add_next_tick_callback.assert_called()


def test_process_event_calls_start_and_stop(app):
    app.start_experiment = mock.Mock()
    app.end_experiment = mock.Mock()
    app.get_current_timestamp = mock.Mock(return_value="ts")
    app._process_event(CommandType.START, "data")
    app.start_experiment.assert_called_with("data", "ts")
    app._process_event(CommandType.STOP, "data")
    app.end_experiment.assert_called_with("data", "ts")


def test_check_for_base_sources_creates_sources(app):
    app.services.cache.get.return_value = {"now": ("tuid", mock.Mock(name="STARTED"))}
    app._tuid_data.tuids = set()
    app.session_manager.update_sources = mock.Mock()
    app._check_for_base_sources()
    app.session_manager.update_sources.assert_called()


def test_initialize_sources_from_cache_sets_source_data(app):
    # Prepare mock sources and tuids
    tuid = "tuid1"
    plot_name = "test_plot"
    app._tuid_data.tuids = {tuid}
    sources = {f"{tuid}_{plot_name}": mock.Mock(spec=["data"])}

    # Prepare mock cache and configs
    app._make_cache_key(plot_name, tuid)
    cached_data = {"x": [1, 2, 3], "y": [4, 5, 6]}
    app.services.cache.get = mock.Mock(return_value=cached_data)
    app._get_plot_names = mock.Mock(return_value=[plot_name])
    app._get_source = mock.Mock(
        return_value=(sources[f"{tuid}_{plot_name}"], f"{tuid}_{plot_name}")
    )
    app._get_plot_type = mock.Mock(
        return_value=(
            PlotType.ONE_D,
            {"plot_name": plot_name, "plot_type": "1d", "x_key": "x"},
        )
    )

    # Patch data_processor methods
    with (
        mock.patch(
            "quantify.visualization.plotmon.services.data_processor.extract_data",
            return_value=cached_data,
        ) as extract_data_mock,
        mock.patch(
            "quantify.visualization.plotmon.services.data_processor.process",
            return_value=cached_data,
        ) as process_mock,
    ):
        app.initialize_sources_from_cache(sources)
        # Check that source.data was set
        assert sources[f"{tuid}_{plot_name}"].data == cached_data
        extract_data_mock.assert_called_once()
        process_mock.assert_called_once()


def test_check_for_update_updates_column_data_source(app):
    # Setup: create a real ColumnDataSource and add it to sources

    tuid = "tuid1"
    plot_name = "test_plot"
    identifier = 42
    sources = {f"{tuid}_{plot_name}": ColumnDataSource(data={"x": [], "y": []})}
    app._tuid_data.tuids = {tuid}
    app._get_plot_names = mock.Mock(return_value=[plot_name])
    app._get_source = mock.Mock(
        return_value=(sources[f"{tuid}_{plot_name}"], f"{tuid}_{plot_name}")
    )
    app._get_plot_type = mock.Mock(
        return_value=(
            PlotType.ONE_D,
            {"plot_name": plot_name, "plot_type": "1d", "x_key": "x"},
        )
    )

    # Patch session_manager to return our sources and a fake doc
    doc = mock.Mock()
    app.session_manager.all_sessions = mock.Mock(return_value=[(identifier, doc)])

    # Patch doc.add_next_tick_callback to immediately call the callback
    def immediate_callback(cb):
        cb()

    doc.add_next_tick_callback = immediate_callback

    # Patch data_processor to return processed data
    processed_data = {"x": [1, 2, 3], "y": [4, 5, 6]}
    with (
        mock.patch(
            "quantify.visualization.plotmon.services.data_processor.extract_data",
            return_value=processed_data,
        ),
        mock.patch(
            "quantify.visualization.plotmon.services.data_processor.process",
            return_value=processed_data,
        ),
    ):
        # Enqueue data
        app.enqueue_data(plot_name, tuid, processed_data)
        # Call check_for_update, which will call _update_plots
        app.check_for_update()
        # Assert ColumnDataSource was updated
        assert sources[f"{tuid}_{plot_name}"].data == processed_data
