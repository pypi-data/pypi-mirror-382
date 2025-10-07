# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""Module containing the pyqtgraph based plotting monitor."""

import time
import warnings
from threading import Event, Lock, Thread

import pyqtgraph as pg
import pyqtgraph.multiprocess as pgmp
from pyqtgraph.multiprocess.remoteproxy import ClosedError
from qcodes import Instrument, ManualParameter, Parameter  # type: ignore
from qcodes.utils import validators as vals
from qcodes.utils.helpers import strip_attrs  # type: ignore

from quantify.data.handling import snapshot
from quantify.utilities.general import traverse_dict
from quantify.visualization.ins_mon_widget import qc_snapshot_widget


class InstrumentMonitor(Instrument):
    """
    Creates a `pyqtgraph` widget that displays the instrument monitor window.

    .. seealso:: :ref:`howto-measurement-control-insmon`

    Parameters
    ----------
    name
        name of the :class:`.InstrumentMonitor` object.
    window_size
        The size of the :class:`.InstrumentMonitor`
        window in px.
    remote
        Switch to use a remote instance of the pyqtgraph class.
    update_interval
        Interval in seconds between two updates

    """

    proc = None
    rpg = None

    def __init__(  # noqa: D107
        self,
        name: str,
        window_size: tuple = (600, 600),
        remote: bool = True,
        update_interval: int = 5,
    ) -> None:
        super().__init__(name=name)

        self._update_lock = Lock()
        self._update_thread = RepeatTimer(
            interval=update_interval, function=self._update
        )

        self.update_interval = Parameter(
            get_cmd=self._get_update_interval,
            set_cmd=self._set_update_interval,
            unit="s",
            initial_value=update_interval,
            vals=vals.Numbers(min_value=0.001),
            name="update_interval",
            instrument=self,
        )
        """Only update the window if this amount of time has passed since the last
        update."""

        self.update_snapshot = ManualParameter(
            initial_value=False,
            vals=vals.Bool(),
            name="update_snapshot",
            instrument=self,
        )
        """Set to True in order to query the instruments about each parameter before
        updating the window. Can be slow due to communication overhead."""
        if remote:
            if not self.__class__.proc:
                self._init_qt()
        else:
            # overrule the remote modules
            self.rpg = pg
            self.rwidget = qc_snapshot_widget

        for i in range(10):
            try:
                self.create_widget(window_size=window_size)
            except (ClosedError, ConnectionResetError) as e:
                # the remote process might crash
                if i >= 9:
                    raise e
                time.sleep(0.2)
                self._init_qt()
            else:
                break

        self._update_thread.start()  # Only start updating after widget is created

    def _get_update_interval(self):  # noqa: ANN202
        return self._update_thread.interval

    def _set_update_interval(self, value) -> None:  # noqa: ANN001
        self._update_thread.interval = value

    def _update(self) -> None:
        """Updates the Qc widget with the current snapshot of the instruments."""
        if (
            not self._update_lock.locked()
        ):  # skip if already updating instead of waiting for lock to be released
            with self._update_lock:
                # Take an updated, clean snapshot
                snap = snapshot(update=self.update_snapshot(), clean=True)
                try:
                    self.widget.setData(snap["instruments"])
                except AttributeError as e:
                    # This is to catch any potential pickling problems with the
                    # snapshot. We do so by converting all lowest elements of
                    # the napshot to string.
                    snap_collated = traverse_dict(snap["instruments"])
                    self.widget.setData(snap_collated)
                    warnings.warn(f"Encountered: {e}", Warning)

    def _init_qt(self, timeout: int = 60) -> None:
        # starting the process for the pyqtgraph plotting
        # You do not want a new process to be created every time you start a
        # run, so this only starts once and stores the process in the class
        self.__class__.proc = pgmp.QtProcess(
            processRequests=False
        )  # pyqtgraph multiprocessing
        if not isinstance(self.proc, pgmp.QtProcess):
            raise TypeError(
                f"self.proc must be of type pgmp.QtProcess but is {type(self.proc)}"
            )
        self.__class__.rpg = self.proc._import("pyqtgraph", timeout=timeout)
        qc_widget = "quantify.visualization.ins_mon_widget.qc_snapshot_widget"
        self.__class__.rwidget = self.proc._import(qc_widget, timeout=timeout)  # type: ignore

    def create_widget(self, window_size: tuple = (1000, 600)) -> None:
        """
        Saves an instance of the
        :class:`!quantify.visualization.ins_mon_widget.qc_snapshot_widget.QcSnapshotWidget`
        class during startup. Creates the
        :class:`~quantify.data.handling.snapshot` tree to display within the
        remote widget window.

        Parameters
        ----------
        window_size
            The size of the :class:`.InstrumentMonitor`
            window in px.

        """  # pylint: disable=line-too-long
        self.widget = self.rwidget.QcSnapshotWidget()
        self._update()
        self.widget.show()
        self.widget.setWindowTitle(self.name)
        self.widget.resize(*window_size)

    def setGeometry(self, x: int, y: int, w: int, h: int) -> None:  # noqa N802
        """Set the geometry of the main widget window.

        Parameters
        ----------
        x
            Horizontal position of the top-left corner of the window.
        y
            Vertical position of the top-left corner of the window.
        w
            Width of the window.
        h
            Height of the window.

        """
        self.widget.setGeometry(x, y, w, h)

    def close(self) -> None:
        """
        Irreversibly stop this instrument and free its resources.

        Subclasses should override this if they have other specific
        resources to close.

        (Modified from Instrument class)
        """
        self._update_thread.cancel()
        self._update_thread.join()

        if hasattr(self, "connection") and hasattr(self.connection, "close"):
            self.connection.close()

        # Essential!!!
        # Close the process
        # Although _update_thread is cancelled, _update may still be running; wait
        # for it to finish
        with self._update_lock:
            if not hasattr(self.proc, "join"):
                raise AttributeError("self.proc doesn't have the method 'join'")
            self.proc.join()  # type: ignore

            strip_attrs(self, whitelist=["_name"])
            self.remove_instance(self)


class RepeatTimer(Thread):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        interval,  # noqa: ANN001
        function,  # noqa: ANN001
        args=None,  # noqa: ANN001
        kwargs=None,  # noqa: ANN001
    ) -> None:
        super().__init__()
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()
        self._paused = Event()
        self._interval_lock = Lock()
        self.interval = interval

    def run(self) -> None:
        """Function called in separate thread after calling .start() on the instance."""
        while not self.finished.wait(self.interval):
            if not self._paused.is_set():
                self.function(*self.args, **self.kwargs)

    def cancel(self) -> None:
        """Stop the timer (and exit the loop/thread)."""
        self.finished.set()

    def pause(self) -> None:
        """
        Pause the timer.

        i.e. do not execute the function, but stay in the loop/thread.
        """
        self._paused.set()

    def unpause(self) -> None:
        """Unpause the timer, i.e. execute the function in the loop again."""
        self._paused.clear()

    @property
    def interval(self):  # noqa: ANN201, D102
        with (
            self._interval_lock
        ):  # not completely sure if an instance attribute is atomic, so let's be sure
            return self._interval

    @interval.setter
    def interval(self, value) -> None:  # noqa: ANN001
        with (
            self._interval_lock
        ):  # not completely sure if an instance attribute is atomic, so let's be sure
            self._interval = value
