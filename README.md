# Pseudo-Entropy Quantum Error Detection — CI/CD Edition

A CI/CD adaptation of [pseudo-entropy-quantum-error-detection](https://github.com/AssafKatz3/pseudo-entropy-quantum-error-detection).
Instead of Jupyter notebooks with visualization, this project runs **pseudo-entropy coherent error estimation**
as automated tests on real IBM Quantum hardware, with strict per-job gate-time budgeting.

## Project Structure

```
.
├── config.yaml                  # All tunable parameters (sweep ranges, budgets, QPU list)
├── requirements.txt
├── Jenkinsfile                  # Pipeline: lint → simulator tests → hardware tests → budget check
├── k8s/
│   ├── secretstore-ibm-cloud.yaml       # ESO SecretStore (IBM Cloud Secrets Manager)
│   └── externalsecret-quantum.yaml      # Syncs QISKIT_IBM_TOKEN + ORG_ID into K8s Secret
├── src/
│   ├── config.py                # Loads config.yaml as typed dataclasses
│   ├── hardware_data.py         # Replaces hardware-data.ipynb — real backend qubit data
│   ├── pseudo_entropy.py        # Replaces pseudo_entropy.ipynb — core math, no plotting
│   └── qpu/
│       └── entanglement_error.py  # Pre-submission gate time + entanglement error estimator
├── scripts/
│   └── quantum_usage.py         # Post-run per-job gate time budget enforcement
└── tests/
    ├── conftest.py
    ├── test_hardware_data.py    # CI replacement for hardware-data.ipynb
    └── test_pseudo_entropy.py   # CI replacement for pseudo_entropy.ipynb
```

## Reference and test origins

The core protocol is based on the companion article and reference notebook for
pseudo-entropy-based coherent-error detection:
https://github.com/AssafKatz3/pseudo-entropy-quantum-error-detection

The implementation and tests are grounded in the article's sections on:
- the circuit construction sequence ("3. Quantum Circuit Visualizations and Sources"),
- the β/δ sensitivity analysis ("1. Pseudo-Entropy Derivative and Sensitivity Maps"), and
- the threshold/phase-region interpretation ("2. Phase Diagrams, Model Comparisons, and Segment Analysis").

The simulator tests use simple no-error, sub-threshold, and strong-error cases to
check that the detector behaves as expected. The hardware tests use the configured
(β, δ, expect_detected) triples from config.yaml so they mirror the article's
protocol scenarios on real IBM Quantum backends.

## Configuration

All parameters live in `config.yaml`:

| Section | Key | Description |
|---|---|---|
| `sweep` | `beta_points`, `beta_range` | β grid (interaction strength) |
| `sweep` | `delta_points`, `delta_range` | δ grid (coherent error angle) |
| `backends` | — | List of IBM QPU names to test |
| `limits` | `qpu_budget_seconds` | Per-job gate time limit (CI fails if exceeded) |
| `limits` | `max_entanglement_error` | Preflight entanglement error threshold |
| `limits` | `job_timeout_seconds` | Max wait for a single IBM job |
| `limits` | `pipeline_timeout_minutes` | Jenkins pipeline timeout |
| `detection` | `safety_factor` | threshold = factor × mean(readout_errors) |
| `hardware_test_cases` | — | (β, δ, expect_detected) triples run on real QPUs |

## Running Locally

```bash
pip install -r requirements.txt
export QISKIT_IBM_TOKEN=your_token
export ORG_ID=your_crn

# Simulator tests (no QPU credits)
pytest tests/ -m "not requires_ibm" -v

# Hardware tests (spends QPU credits)
pytest tests/ -m "requires_ibm" -v

# Gate time budget check
python scripts/quantum_usage.py --output quantum_usage.json
```

## Other QPU Architectures

This CI/CD edition currently targets **IBM Quantum** backends via Qiskit Runtime.
Versions supporting other QPU architectures (e.g. AWS Braket / IonQ / Rigetti,
Google Cirq / Quantum AI, Quantinuum, Azure Quantum) are available on payment
under the Commercial License — see [LICENSE](./LICENSE) or contact the copyright
holder for details.

## Pipeline Stages

1. **Checkout** — pull source
2. **Install Dependencies** — `pip install -r requirements.txt`
3. **Lint** — flake8 + black
4. **Test (Simulator)** — always runs, no QPU credits
5. **Test (IBM Quantum Hardware)** — runs on `main` branch or tags only
6. **Quantum Gate Time Budget** — fails build if any job exceeds `qpu_budget_seconds`
