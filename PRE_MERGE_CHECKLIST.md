# Pre-Merge Checklist — Production Readiness

Last updated: 2026-07-05 — checklist added to branch; hardware validation pending.

This checklist must be completed **before merging** the
`draft/production-readiness-docs` branch into `main`.

The branch has passed lint and simulator tests, but has **not yet been
validated on real IBM Quantum hardware**. Do not merge until the
hardware suite has been run and the budget report is green.

---

## 1. Credentials & Environment

- [ ] `QISKIT_IBM_TOKEN` available (from IBM Quantum Platform → API key)
- [ ] `ORG_ID` (CRN) set if using a paid service instance
- [ ] `IBM_CLOUD_SETUP.md` steps 1–5 completed
- [ ] Token verified:
      ```bash
      python -c "from qiskit_ibm_runtime import QiskitRuntimeService; \
                 QiskitRuntimeService().backends()"
      ```

## 2. Static Checks (already green in CI, re-verify locally)

- [ ] `flake8 src tests --max-line-length=100 --extend-ignore=E203,W503`
- [ ] `black --check src tests`
- [ ] `pytest tests/ -m "not requires_ibm" -v` — all simulator tests pass

## 3. Hardware Test Run ⚠️ (spends QPU credits)

Run against real backends defined in `config.yaml` (ibm_kingston,
ibm_fez, ibm_marrakesh).

- [ ] Run locally first (faster feedback, controlled cost):
      ```bash
      pytest tests/ -m "requires_ibm" \
          --html=pytest_hardware_report.html --self-contained-html -v
      ```
- [ ] All `test_hardware_data.py` cases pass (backend data extraction + CSV export)
- [ ] All `test_pseudo_entropy.py` hardware cases pass:
      - clean circuit (`beta=0.5, delta=0.0`) → not detected
      - coherent error (`beta=0.5, delta=0.3`) → detected
- [ ] `hardware/*.csv` artifacts generated and inspected
- [ ] If running via Jenkins, set `RUN_HARDWARE_TESTS=true` on a non-main
      branch and confirm `pytest_hardware_report.html` is archived

## 4. Gate-Time Budget

- [ ] `python scripts/quantum_usage.py --output quantum_usage.json` runs clean
- [ ] `job_count`, `total_gate_time_seconds` recorded
- [ ] `budget_exceeded == false`
- [ ] No `first_violation` entry in the JSON
- [ ] Jenkins "Quantum Gate Time Budget" stage prints `✅ OK`

## 5. Preflight Estimator

- [ ] `src/qpu/entanglement_error.py` validates test circuits before
      submission (no aborts due to `max_entanglement_error` exceeded)

## 6. PR Hygiene

- [ ] PR #8 description reflects the final state
- [ ] Diff reviewed — no stray notebook files, no hardcoded tokens
- [ ] `LICENSE` is the dual-license (non-commercial / commercial)
- [ ] `README.md` links to `IBM_CLOUD_SETUP.md` and `LICENSE`
- [ ] Branch is up to date with `main` (no merge conflicts)

---

## Merge Criteria

Merge only when **every box above is checked** and the hardware report
is archived. If any hardware test fails or the budget is exceeded, do
not merge — file findings on PR #8 and keep the branch in draft.

## Emergency Rollback

If a regression is found after merge:
1. Revert the merge commit on `main`.
2. Re-open PR #8 with the fix.
3. Re-run this checklist before merging again.
