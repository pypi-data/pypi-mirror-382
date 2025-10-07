# Repository: https://gitlab.com/quantify-os/quantify
# Licensed according to the LICENSE file on the main branch
"""
Data acquisition framework focused on Quantum Computing and solid-state physics
experiments.

.. list-table::
    :header-rows: 1
    :widths: auto

    * - Import alias
      - Target
    * - :class:`.QuantumDevice`
      - :class:`!quantify.QuantumDevice`
    * - :class:`.Schedule`
      - :class:`!quantify.Schedule`
    * - :class:`.Resource`
      - :class:`!quantify.Resource`
    * - :class:`.ClockResource`
      - :class:`!quantify.ClockResource`
    * - :class:`.BasebandClockResource`
      - :class:`!quantify.BasebandClockResource`
    * - :class:`.DigitalClockResource`
      - :class:`!quantify.DigitalClockResource`
    * - :class:`.Operation`
      - :class:`!quantify.Operation`
    * - :obj:`.structure`
      - :obj:`!quantify.structure`
    * - :class:`.BasicTransmonElement`
      - :class:`!quantify.BasicTransmonElement`
    * - :class:`.CompositeSquareEdge`
      - :class:`!quantify.CompositeSquareEdge`
    * - :class:`.InstrumentCoordinator`
      - :class:`!quantify.InstrumentCoordinator`
    * - :class:`.GenericInstrumentCoordinatorComponent`
      - :class:`!quantify.GenericInstrumentCoordinatorComponent`
    * - :class:`.SerialCompiler`
      - :class:`!quantify.SerialCompiler`
    * - :class:`.MockLocalOscillator`
      - :class:`!quantify.MockLocalOscillator`
"""

# Core modules
from quantify import structure, waveforms

# Version handling
try:
    from importlib.metadata import version

    __version__ = version("quantify")
except Exception:
    __version__ = "unknown"

# Expose measurement and analysis submodules for Sphinx
from quantify import analysis, measurement
from quantify.analysis.base_analysis import BaseAnalysis
from quantify.backends import SerialCompiler
from quantify.device_under_test import BasicTransmonElement, QuantumDevice
from quantify.instrument_coordinator.components.generic import (
    GenericInstrumentCoordinatorComponent,
)
from quantify.instrument_coordinator.instrument_coordinator import InstrumentCoordinator
from quantify.measurement.control import MeasurementControl
from quantify.measurement.types import Settable
from quantify.operations import Operation
from quantify.resources import (
    BasebandClockResource,
    ClockResource,
    DigitalClockResource,
    Resource,
)
from quantify.schedules import Schedule

__all__ = [
    # Core modules
    "structure",
    "waveforms",
    "__version__",
    "SerialCompiler",
    "BasicTransmonElement",
    "QuantumDevice",
    "InstrumentCoordinator",
    "GenericInstrumentCoordinatorComponent",
    "Operation",
    "BasebandClockResource",
    "ClockResource",
    "DigitalClockResource",
    "Resource",
    "Schedule",
    # Measurement & analysis
    "measurement",
    "analysis",
    "MeasurementControl",
    "Settable",
    "BaseAnalysis",
]
