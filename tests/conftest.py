import os

import pytest
from qiskit_ibm_runtime import QiskitRuntimeService

from src.config import cfg

@pytest.fixture(scope="session")
def ibm_service():
    """Shared IBM Quantum session for the entire test run."""
    token = os.environ.get("QISKIT_IBM_TOKEN")
    if not token:
        pytest.skip("QISKIT_IBM_TOKEN not set — skipping hardware tests")
    return QiskitRuntimeService(
        channel="ibm_cloud",
        token=token,
        instance=os.environ.get("ORG_ID"),
    )

@pytest.fixture(scope="session")
def real_backends(ibm_service):
    """All operational real QPU backends for this account."""
    return ibm_service.backends(simulator=False, operational=True)

@pytest.fixture(scope="session")
def qpu_budget_seconds() -> float:
    return float(
        os.environ.get("QPU_BUDGET_SECONDS", cfg.limits.qpu_budget_seconds)
    )
