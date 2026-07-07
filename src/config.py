"""
config.py  —  Load and expose config.yaml as a typed dataclass.
Import: from src.config import cfg
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_PATH = Path(
    os.environ.get(
        "CONFIG_PATH",
        Path(__file__).resolve().parent.parent / "config.yaml",
    )
)

@dataclass
class SweepConfig:
    beta_points: int
    beta_range: float
    delta_points: int
    delta_range: float

@dataclass
class LimitsConfig:
    qpu_budget_seconds: float
    max_entanglement_error: float
    job_timeout_seconds: int
    pipeline_timeout_minutes: int

@dataclass
class DetectionConfig:
    safety_factor: float

@dataclass
class HardwareTestCase:
    beta: float
    delta: float
    expect_detected: bool

@dataclass
class AppConfig:
    sweep: SweepConfig
    backends: list[str]
    limits: LimitsConfig
    detection: DetectionConfig
    hardware_test_cases: list[HardwareTestCase]

def _load() -> AppConfig:
    with open(CONFIG_PATH) as f:
        raw = yaml.safe_load(f)
    return AppConfig(
        sweep=SweepConfig(**raw["sweep"]),
        backends=raw["backends"],
        limits=LimitsConfig(**raw["limits"]),
        detection=DetectionConfig(**raw["detection"]),
        hardware_test_cases=[
            HardwareTestCase(**tc) for tc in raw["hardware_test_cases"]
        ],
    )

cfg: AppConfig = _load()


def get_active_backends(candidates: list[str], min_qubits: int = 5) -> list[str]:
    """Filter a list of candidate backend names down to those actually live right now.

    This performs a live query against the IBM Quantum service. It will raise a
    RuntimeError if the Qiskit IBM Runtime SDK is not available, if credentials
    are missing, or if none of the configured backends are currently operational.
    """
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except Exception as exc:  # ImportError or other runtime problems
        raise RuntimeError(
            "qiskit_ibm_runtime is required to resolve live backends: "
            + str(exc)
        )

    service = QiskitRuntimeService()
    live = {
        b.name
        for b in service.backends(operational=True, simulator=False, min_num_qubits=min_qubits)
    }
    active = [name for name in candidates if name in live]
    if not active:
        raise RuntimeError(
            f"None of the configured backends {candidates} are currently active. "
            f"Live options: {sorted(live)}"
        )
    return active


def resolve_cfg_backends(min_qubits: int = 5) -> list[str]:
    """Resolve the backends listed in the loaded config to the currently active set.

    Callers (for example the Jenkins hardware-test stage) should call this
    early and fail fast if no configured backend is live.
    """
    return get_active_backends(cfg.backends, min_qubits=min_qubits)
