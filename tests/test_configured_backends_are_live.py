import pytest

from src.config import cfg


@pytest.mark.requires_ibm
def test_configured_backends_are_live():
    """Fail if any backend named in `config.yaml` is no longer operational.

    This test should be scheduled (not run on every commit) because it
    queries live IBM hardware information and may consume quota.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    live = {b.name for b in service.backends(operational=True, simulator=False)}
    dead = [b for b in cfg.backends if b not in live]
    assert not dead, f"Configured backends no longer exist: {dead}"
