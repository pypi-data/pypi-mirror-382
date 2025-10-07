"""
plotmon_app module: Bokeh application handler for Plotmon,
managing documents and data sources.
"""

import datetime
import logging
import queue
from collections.abc import Sequence
from functools import partial
from typing import Any

from bokeh.application.application import SessionContext
from bokeh.application.handlers.handler import Handler
from bokeh.core.types import ID
from bokeh.document import Document
from bokeh.models import Column, ColumnDataSource

from quantify.visualization.plotmon.services import data_processor, graph_builder
from quantify.visualization.plotmon.services.figure_builder.base_figure_builder import (
    PlotType,
)
from quantify.visualization.plotmon.services.plotmon_service import (
    PlotmonConfig,
    PlotmonServices,
    TuidData,
)
from quantify.visualization.plotmon.services.session_manager import SessionManager
from quantify.visualization.plotmon.utils.commands import CommandType, ExperimentState


class PlotmonApp(Handler):
    """
    Bokeh application handler for Plotmon.
    Manages multiple documents and their data sources, ensuring thread-safe updates.
    """

    UPDATE_RATE_MS: int = 1000 // 60

    def __init__(
        self,
        config: PlotmonConfig,
        services: PlotmonServices,
    ) -> None:
        """
        Initialize the Plotmon application handler.

        Parameters
        ----------
        config : PlotmonConfig
            Configuration for the Plotmon application.
        services : PlotmonServices
            Services for data caching and retrieval.

        """
        super().__init__()
        self.config = config
        self.services = services
        self.session_manager = SessionManager()
        self.data_queue = queue.Queue()
        self._tuid_data = TuidData(tuids=set(), active_tuid="", selected_tuid={-1: ""})

        base_sources = graph_builder.create_sources(self.config.graph_configs)
        for name, source in base_sources.items():
            self.session_manager.add_base_source(name, source)

    def modify_document(self, doc: Document) -> None:
        """
        Modify the given Bokeh document to
        set up the application layout and callbacks.

        Parameters
        ----------
        doc : Document
            The Bokeh document to modify.

        """
        self._check_for_base_sources()
        doc, sources, layout = self.session_manager.get_doc_and_sources(doc)
        self._tuid_data.selected_tuid[
            self.session_manager.get_current_session_id(doc)
        ] = self._tuid_data.selected_tuid.get(-1, "")
        # Set up the document with layout and
        # callbacks using the sources for this session.
        self.initialize_sources_from_cache(sources)
        logging.warning(
            "Document modified for session %s",
            self.session_manager.get_current_session_id(doc),
        )
        self.serve(doc, sources, layout)

    def enqueue_data(self, plot_name: str, tuid: str, data: dict[str, list]) -> None:
        """
        Enqueue new data for a specific plot to be processed in the Bokeh event loop.

        Parameters
        ----------
        plot_name : str
            The name of the plot to update.
        tuid : str
            The TUID associated with the plot.
        data : dict[str, list]
            The new data to append to the plot.

        """
        self.data_queue.put((plot_name, tuid, data))

    def serve(
        self, doc: Document, sources: dict[str, ColumnDataSource], layout: None | Column
    ) -> None:
        """Set up the Bokeh document with the application layout and periodic callbacks.

        Parameters
        ----------
        doc : Document
            The Bokeh document to modify.
        sources : dict[str, ColumnDataSource]
            The data sources to be used in the document.
        layout : Column | None
            The existing layout to update, or None to create a new one.

        """
        self._tuid_data.session_id = self.session_manager.get_current_session_id(doc)
        new_layout = graph_builder.build_layout(
            self.config.graph_configs,
            sources,
            self._tuid_data,
            self.services.cache.get_all(
                prefix=self.config.data_source_name, suffix="_meta"
            ),
            partial(self._on_select, doc=doc),
            layout,
        )

        if layout is None:
            self.session_manager.set_layout(doc, new_layout)
            doc.add_root(new_layout)
            doc.add_periodic_callback(self.check_for_update, PlotmonApp.UPDATE_RATE_MS)
            doc.title = self.config.title
            logging.warning("Document root replaced")
        else:
            logging.warning("Document layout updated")

    def initialize_sources_from_cache(
        self, sources: dict[str, ColumnDataSource]
    ) -> None:
        """Initialize data sources from cached data if available."""
        for plot_name in self._get_plot_names():
            for tuid in self._tuid_data.tuids:
                cache_key = self._make_cache_key(plot_name, tuid)
                cached_data = self.services.cache.get(cache_key) or {}

                source, source_name = self._get_source(sources, plot_name, tuid)
                if cached_data and source and source_name:
                    plot_type, config = self._get_plot_type(plot_name)
                    data = data_processor.extract_data(cached_data, plot_type, config)
                    data = data_processor.process(plot_type, data, config)
                    source.data = data  # type: ignore[assignment]

    def check_for_update(self) -> None:
        """
        Check the data queue for new data and update plots accordingly.
        This method is called periodically in the Bokeh event loop.
        """
        while not self.data_queue.empty():
            plot_name, tuid, data = self.data_queue.get()
            # Schedule plot updates for each document/session using Bokeh's
            # next_tick_callback for thread safety.
            for identifier, doc in self.session_manager.all_sessions():
                doc.add_next_tick_callback(
                    lambda pn=plot_name,
                    d=data,
                    i=identifier,
                    t=tuid: self._update_plots(pn, d, i, t)
                )

    def start_experiment(self, tuid: str, timestamp: str) -> None:
        """
        Start tracking a new experiment by its TUID and create associated data sources.

        Parameters
        ----------
        tuid : str
            The TUID of the experiment to start.
        timestamp : str
            The timestamp when the experiment started.

        """
        self._tuid_data.tuids.add(tuid)
        self._tuid_data.active_tuid = tuid
        self._tuid_data.selected_tuid = {}
        tuid_sources = graph_builder.create_sources(self.config.graph_configs, tuid)
        self.session_manager.update_sources(tuid_sources)

        cache_key = f"{self.config.data_source_name}_{tuid}_meta"
        meta = self.services.cache.get(cache_key) or {}
        self.services.cache.set(
            cache_key,
            {
                **meta,
                "start_date": timestamp,
            },
        )
        logging.warning("New experiment started with TUID: %s", tuid)
        self._re_render()

    def end_experiment(self, tuid: str, timestamp: str) -> None:
        """Mark an experiment as finished by removing it from the active TUIDs set."""
        self._tuid_data.selected_tuid[-1] = tuid
        session_ids = self.session_manager.get_all_session_ids()
        self._tuid_data.active_tuid = ""
        # Display the ended experiment as selected in all sessions
        for session_id in session_ids:
            self._tuid_data.selected_tuid[session_id] = tuid

        cache_key = f"{self.config.data_source_name}_{tuid}_meta"
        meta = self.services.cache.get(cache_key) or {}
        meta["end_date"] = timestamp
        self.services.cache.set(cache_key, meta)
        logging.warning("Experiment ended with TUID: %s", tuid)
        self._re_render()

    #### PRIVATE METHODS ####

    def _re_render(self) -> None:
        for identifier, doc in self.session_manager.all_sessions():
            sources = self.session_manager.get_sources(identifier)
            layout = self.session_manager.get_layout(doc)
            if layout is None:
                continue
            logging.warning("Re-rendering layout for session %s", identifier)
            doc.add_next_tick_callback(
                lambda d=doc, s=sources, l=layout: self.serve(d, s, l)
            )

    def _update_plots(
        self,
        plot_name: str,
        data: dict[str, Sequence[Any]],
        identifier: int | ID,
        tuid: str,
    ) -> None:
        """
        Update the plots with new data and save the updated data to cache.

        Parameters
        ----------
        plot_name : str
            The name of the plot to update.
        data : dict[str, list]
            The new data to append to the plot.
        identifier : int | ID
            The session identifier for which to update the plot.
        tuid : str
            The TUID associated with the plot.

        """
        # get the plot source by name and append the new data,
        # then save the data to cache
        source, _ = self._get_source(
            self.session_manager.get_sources(identifier), plot_name, tuid
        )

        plot_type, config = self._get_plot_type(plot_name)
        if plot_type == PlotType.HEATMAP:
            # For heatmaps we get cache data and then process it
            cache_data = (
                self.services.cache.get(self._make_cache_key(plot_name, tuid)) or {}
            )
            data = data_processor.extract_data(cache_data, plot_type, config)

        processed_data = data_processor.process(plot_type, data, config)

        # Use Bokeh's stream method to efficiently
        # append new data to the plot's data source.
        # Validate data agains the source columns, they must have the same keys
        xkey = config.get("x_key", "x")
        if not source:
            logging.warning(
                "Data source for plot %s and TUID %s not found.", plot_name, tuid
            )
            return

        source_data = source.data
        if not isinstance(source_data, dict):
            logging.warning("Data for plot %s is not a valid DataDict.", plot_name)
            return
        if not set(processed_data.keys()).issubset(set(source_data.keys())):
            logging.warning("Data for plot %s missing x_key %s", plot_name, xkey)
            return

        # if source data already contains data for the xkey ignore update
        if (
            processed_data[xkey][0] not in source.data[xkey]
            and plot_type == PlotType.ONE_D
        ):
            source.stream(new_data=processed_data, rollover=None)  # type: ignore[arg-type]
        elif plot_type == PlotType.HEATMAP:
            source.update(data=processed_data)
            # source.data = data

    async def on_session_destroyed(self, session_context: SessionContext) -> None:
        """
        Callback when a session is destroyed. Cleans up associated resources.

        Parameters
        ----------
        session_context : SessionContext
            The session context that was destroyed.

        """
        # Delete doc and sources associated with the destroyed session
        session_id = session_context.id if session_context else None
        self.session_manager.delete_session(session_id)

    def _get_plot_names(self) -> list[str]:
        """Retrieve all plot names from the graph configurations."""
        return [
            config.get("plot_name", "")
            for row_config in self.config.graph_configs
            for config in row_config
            if config.get("plot_name")
        ]

    def _get_source(
        self, sources: dict[str, ColumnDataSource], plot_name: str, tuid: str
    ) -> tuple[ColumnDataSource | None, str | None]:
        """
        Retrieve the data source and its name associated with a given plot name.

        Parameters
        ----------
        sources : dict[str, ColumnDataSource]
            The dictionary of available data sources.
        plot_name : str
            The name of the plot to look up.
        tuid : str
            The TUID associated with the plot.

        Returns
        -------
        Tuple[ColumnDataSource | None, str | None]
            A tuple containing the data source and its name,
            or (None, None) if not found.

        """
        source_name = self._make_source_name(tuid, plot_name)
        return sources.get(source_name), source_name

    def _make_cache_key(self, plot_name: str, tuid: str) -> str:
        """Helper to construct a cache key for a given plot name."""
        return f"{self.config.data_source_name}_{tuid}_{plot_name}"

    def _make_source_name(self, tuid: str, plot_name: str) -> str:
        """Helper to construct a source name for a given TUID and plot name."""
        return f"{tuid}_{plot_name}"

    def _on_select(self, selected_tuids: set[str], doc: Document) -> None:
        """
        Callback for when TUIDs are selected in the DataTable.
        Only updates the plot for the current session/document.
        """
        session_id = self.session_manager.get_current_session_id(doc)
        if set(self._tuid_data.selected_tuid.get(session_id, "")) == selected_tuids:
            return  # No change in selection
        for tuid in selected_tuids:
            if tuid != self._tuid_data.selected_tuid[session_id]:
                self._tuid_data.selected_tuid[session_id] = tuid
                break

        sources = self.session_manager.get_sources(session_id)
        layout = self.session_manager.get_layout(doc)
        if layout is None:
            return
        logging.warning(
            "TUID selection changed to %s in session %s",
            self._tuid_data.selected_tuid[session_id],
            session_id,
        )
        doc.add_next_tick_callback(
            lambda d=doc, s=sources, l=layout: self.serve(d, s, l)
        )

    def _get_plot_type(self, plot_name: str) -> tuple[PlotType, dict]:
        """
        Retrieve the plot type for a given plot name from the graph configurations.

        Parameters
        ----------
        plot_name : str
            The name of the plot to look up.

        Returns
        -------
        PlotType
            The PlotType if found.

        """
        for row_config in self.config.graph_configs:
            for config in row_config:
                if config.get("plot_name") == plot_name:
                    plot_type_str = config.get("plot_type", "")
                    return PlotType.from_str(plot_type_str), config

        raise ValueError(f"Plot name '{plot_name}' not found in configurations.")

    def get_current_timestamp(self) -> str:
        """Get the current timestamp in ISO format."""
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d_%H-%M-%S_%Z"
        )

    def add_event_next_tick(self, event: CommandType, data: str) -> None:
        """Add an event to be processed in the next tick of the Bokeh event loop."""
        for _, doc in self.session_manager.all_sessions():
            doc.add_next_tick_callback(
                lambda e=event, d=data: self._process_event(e, d)
            )
            return

    def _process_event(self, event: CommandType, data: str) -> None:
        """
        Process an event. Currently supports 'start_experiment' and 'end_experiment'.

        Parameters
        ----------
        event : CommandType
            The type of event to process.
        data : Any
            The data associated with the event.

        """
        timestamp = self.get_current_timestamp()
        logging.info("Processing event %s at %s", event, timestamp)
        if event == CommandType.START:
            self.start_experiment(data, timestamp)
        elif event == CommandType.STOP:
            self.end_experiment(data, timestamp)
        else:
            logging.warning("Unknown event %s received.", event)

    def _check_for_base_sources(self) -> None:
        """Retrieve tuids from cache and ensure that they have base sources created."""
        experiment_state: dict[str, tuple[str, ExperimentState]] = (
            self.services.cache.get(f"{self.config.data_source_name}_experiments") or {}
        )
        for now, (tuid, status) in experiment_state.items():
            created = True
            if tuid in self._tuid_data.tuids:
                created = False
            self._tuid_data.tuids.add(tuid)
            if status == ExperimentState.STARTED:
                self._tuid_data.active_tuid = tuid
                self._tuid_data.selected_tuid[-1] = tuid
                cache_key = f"{self.config.data_source_name}_{tuid}_meta"
                meta = self.services.cache.get(cache_key) or {}
                meta["start_date"] = meta.get("start_date", now)
                self.services.cache.set(cache_key, meta)

            if status == ExperimentState.FINISHED:
                cache_key = f"{self.config.data_source_name}_{tuid}_meta"
                meta = self.services.cache.get(cache_key) or {}
                meta["end_date"] = meta.get("end_date", now)
                self.services.cache.set(cache_key, meta)
                if self._tuid_data.active_tuid == tuid:
                    self._tuid_data.active_tuid = ""

            if created:
                tuid_sources = graph_builder.create_sources(
                    self.config.graph_configs, tuid
                )
                self.session_manager.update_sources(tuid_sources)
            logging.info(
                "New TUID detected, that hasnt been initialized from cache: %s", tuid
            )
