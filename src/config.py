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
