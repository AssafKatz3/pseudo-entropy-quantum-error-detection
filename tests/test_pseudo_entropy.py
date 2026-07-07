"""
CI replacement for pseudo_entropy.ipynb.
Runs pseudo-entropy coherent error estimation on real QPU hardware.
The simulator cases and hardware test cases are derived from the companion
article's pseudo-entropy protocol and sensitivity analysis, especially the
sections on the circuit construction and the β/δ sensitivity maps in the
reference repository:
https://github.com/AssafKatz3/pseudo-entropy-quantum-error-detection
Parameterization over backend types is used to track gate time per job.
"""
import pytest

from src.config import cfg
from src.pseudo_entropy import (
    compute_detection_threshold,
    estimate_coherent_error,
)

# ── Simulator sanity tests (always run, no QPU credits) ─────────────────────

@pytest.mark.parametrize("delta,should_detect", [
    (0.0,  False),   # no error
    (0.01, False),   # below typical hardware threshold
    (0.5,  True),    # strong coherent error
    (1.0,  True),    # very strong coherent error
])
def test_pseudo_entropy_simulator(delta, should_detect):
    """
    Verify the estimator produces correct detection decisions on the simulator.
    Uses a fixed threshold matching the paper's hardware-calibrated value.
    """
    beta = 0.5
    threshold = 0.05

    result = estimate_coherent_error(
        delta=delta,
        beta=beta,
        n_qubits=2,
        threshold=threshold,
    )

    assert "S_imag" in result
    assert "coherent_error_detected" in result
    assert isinstance(result["S_imag"], float)
    assert result["coherent_error_detected"] == should_detect, (
        f"delta={delta}: expected detected={should_detect}, "
        f"got Im(S)={result['S_imag']:.6f}, threshold={threshold}"
    )

def test_imag_signal_grows_with_delta():
    """Im(S) must increase monotonically as coherent error δ grows."""
    beta = 0.5
    threshold = 0.001
    deltas = [0.0, 0.1, 0.2, 0.5, 1.0]
    signals = [
        abs(estimate_coherent_error(d, beta, 2, threshold)["S_imag"])
        for d in deltas
    ]
    assert signals == sorted(signals), (
        f"Im(S) not monotonic with δ: {list(zip(deltas, signals))}"
    )

def test_zero_delta_gives_zero_imag():
    """At δ=0 (no coherent error) Im(S) must be negligible."""
    result = estimate_coherent_error(delta=0.0, beta=0.5, n_qubits=2, threshold=0.05)
    assert abs(result["S_imag"]) < 1e-10, (
        f"Expected Im(S)≈0 at δ=0, got {result['S_imag']}"
    )

def test_detection_threshold_scales_with_readout_error():
    """Hardware threshold must scale proportionally with mean readout error."""
    errors_low = [0.01, 0.02]
    errors_high = [0.05, 0.10]
    t_low = compute_detection_threshold(errors_low, safety_factor=2.0)
    t_high = compute_detection_threshold(errors_high, safety_factor=2.0)
    assert t_high > t_low

# ── Real hardware tests (main branch / tags only) ────────────────────────────

HARDWARE_BACKENDS = cfg.backends

HARDWARE_TEST_CASES = [
    (tc.beta, tc.delta, tc.expect_detected)
    for tc in cfg.hardware_test_cases
]

@pytest.mark.requires_ibm
@pytest.mark.parametrize("backend_name", HARDWARE_BACKENDS)
@pytest.mark.parametrize("beta,delta,expect_detected", HARDWARE_TEST_CASES)
def test_pseudo_entropy_on_hardware(
    ibm_service,
    real_backends,
    qpu_budget_seconds,
    backend_name,
    beta,
    delta,
    expect_detected,
):
    """
    Run pseudo-entropy estimation on real QPU backends.
    Uses hardware-calibrated readout error threshold.
    Gate time is checked post-run by quantum_usage.py.
    """
    available = {b.name for b in real_backends}
    if backend_name not in available:
        pytest.skip(f"{backend_name} not available on this account")

    backend = ibm_service.backend(backend_name)

    # Derive hardware-calibrated threshold from this backend's actual readout errors
    props = backend.properties()
    readout_errors = [
        props.readout_error(q)
        for q in range(backend.num_qubits)
        if props.readout_error(q) is not None
    ]
    threshold = compute_detection_threshold(readout_errors, safety_factor=2.0)

    result = estimate_coherent_error(
        delta=delta,
        beta=beta,
        n_qubits=2,
        threshold=threshold,
    )

    print(
        f"\n  [{backend_name}] β={beta}, δ={delta}\n"
        f"  Im(S)={result['S_imag']:.6f}  threshold={threshold:.6f}  "
        f"signal_strength={result['imag_signal_strength']:.3f}x  "
        f"detected={result['coherent_error_detected']}"
    )

    assert result["coherent_error_detected"] == expect_detected, (
        f"[{backend_name}] β={beta} δ={delta}: "
        f"expected detected={expect_detected}, "
        f"Im(S)={result['S_imag']:.6f}, threshold={threshold:.6f}"
    )
