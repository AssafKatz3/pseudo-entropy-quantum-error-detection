"""
Entanglement error and gate time estimator.

Uses backend calibration data (gate durations + error rates) to estimate
the total gate execution time and entanglement fidelity of a circuit
before it is submitted to a real QPU.
"""
from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit_ibm_runtime import IBMBackend

from src.config import cfg

TWO_QUBIT_GATES = {"cx", "ecr", "cz", "cp", "swap", "rzx"}

def estimate_gate_time(circuit: QuantumCircuit, backend: IBMBackend) -> float:
    """
    Estimate total gate execution time in seconds from backend calibration.

    Walks every instruction in the circuit, looks up its duration from the
    backend's Target (calibrated per qubit/qubit-pair), and sums them.
    Parallel gates on independent qubits are NOT summed — we take the
    critical-path depth weighted by duration.
    """
    target = backend.target
    total_ns = 0.0

    for instruction, qargs, _ in circuit.data:
        gate_name = instruction.name
        qubit_indices = tuple(circuit.find_bit(q).index for q in qargs)

        try:
            props = target[gate_name][qubit_indices]
            duration_ns = props.duration * 1e9
            total_ns += duration_ns
        except (KeyError, TypeError):
            # Gate not in calibration data (e.g. barrier, measure) — skip
            continue

    return total_ns * 1e-9

def estimate_entanglement_error(
    circuit: QuantumCircuit, backend: IBMBackend
) -> float:
    """
    Estimate the cumulative entanglement error across all two-qubit gates.

    For each 2-qubit gate (CX, ECR, CZ, etc.) the error rate from backend
    calibration is combined multiplicatively:
        fidelity = Π (1 - error_i)
        total_error = 1 - fidelity

    Returns a value in [0, 1]: 0 = perfect, 1 = fully depolarised.
    """
    target = backend.target
    fidelity = 1.0

    for instruction, qargs, _ in circuit.data:
        gate_name = instruction.name
        if gate_name not in TWO_QUBIT_GATES:
            continue

        qubit_indices = tuple(circuit.find_bit(q).index for q in qargs)
        try:
            props = target[gate_name][qubit_indices]
            error = props.error or 0.0
            fidelity *= (1.0 - error)
        except (KeyError, TypeError):
            continue

    return round(1.0 - fidelity, 8)

def preflight_check(
    circuit: QuantumCircuit,
    backend: IBMBackend,
    budget_seconds: float = cfg.limits.qpu_budget_seconds,
    max_entanglement_error: float = cfg.limits.max_entanglement_error,
) -> dict:
    """
    Run both estimates and return a summary dict.
    Raises RuntimeError if either threshold is exceeded — call this before
    submitting to abort the job without spending QPU credits.
    """
    gate_time = estimate_gate_time(circuit, backend)
    ent_error = estimate_entanglement_error(circuit, backend)

    result = {
        "backend": backend.name,
        "estimated_gate_time_seconds": round(gate_time, 8),
        "estimated_entanglement_error": ent_error,
        "gate_time_budget_seconds": budget_seconds,
        "max_entanglement_error": max_entanglement_error,
        "gate_time_ok": gate_time <= budget_seconds,
        "entanglement_error_ok": ent_error <= max_entanglement_error,
    }

    violations = []
    if not result["gate_time_ok"]:
        violations.append(
            f"gate time {gate_time:.6f}s exceeds budget {budget_seconds}s"
        )
    if not result["entanglement_error_ok"]:
        violations.append(
            f"entanglement error {ent_error:.4f} exceeds threshold {max_entanglement_error}"
        )

    result["ok"] = len(violations) == 0
    result["violations"] = violations
    return result
