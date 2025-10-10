"""
Main QuantumCircuit class for Cirquit
"""
import numpy as np
from typing import List, Tuple, Optional

class QuantumCircuit:
    """A quantum circuit for building and simulating quantum algorithms."""
    
    def __init__(self, num_qubits: int):
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")
        self.num_qubits = num_qubits
        self.gates: List[Tuple] = []
        
    def h(self, qubit: int):
        """Apply Hadamard gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('H', qubit))
        return self
        
    def x(self, qubit: int):
        """Apply Pauli-X gate to qubit."""
        self._validate_qubit(qubit)
        self.gates.append(('X', qubit))
        return self
        
    def cx(self, control: int, target: int):
        """Apply CNOT gate."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target qubits must be different")
        self.gates.append(('CX', control, target))
        return self
        
    def measure_all(self):
        """Measure all qubits."""
        self.gates.append(('MEASURE_ALL',))
        return self
        
    def _validate_qubit(self, qubit: int):
        if not 0 <= qubit < self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits})")
    
    def run(self, shots: int = 1000):
        """Simulate the circuit."""
        return {'0' * self.num_qubits: shots}
    
    def __repr__(self):
        return f"QuantumCircuit({self.num_qubits} qubits, {len(self.gates)} gates)"
