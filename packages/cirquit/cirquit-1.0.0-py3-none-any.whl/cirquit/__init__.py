"""
Cirquit - Quantum circuits, simplified
"""

__version__ = "1.0.0"
__author__ = "Cirquit Team"
__email__ = "hello@cirquit.io"

from .circuit import QuantumCircuit
from .gates import GateType
from .results import CircuitResult

__all__ = [
    "QuantumCircuit",
    "GateType",
    "CircuitResult",
]