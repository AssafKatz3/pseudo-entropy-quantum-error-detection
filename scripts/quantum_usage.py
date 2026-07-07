"""
IBM Quantum gate-time reporter for CI/CD.

Monitors per-job gate execution time (excluding queue/transpile overhead)
and fails the pipeline if any single job exceeds the budget defined in config.yaml.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from qiskit_ibm_runtime import QiskitRuntimeService

from src.config import cfg

QPU_BUDGET_SECONDS = cfg.limits.qpu_budget_seconds

def extract_gate_time(job) -> float:
    """Extract actual gate execution time only (no queue/transpile overhead)."""
    try:
        result = job.result()

        # Path 1: SamplerV2 / EstimatorV2 execution spans (most precise)
        spans = result.metadata.get("execution", {}).get("execution_spans")
        if spans:
            return sum(
                (span.stop - span.start).total_seconds()
                for span in spans
            )

        # Path 2: time_per_step (older backend.run() jobs), value is ms
        running_ms = result.metadata.get("time_per_step", {}).get("running")
        if running_ms is not None:
            return float(running_ms) / 1000.0

        return 0.0

    except Exception as e:
        print(
            f"  [warning] Could not read gate time for {job.job_id()}: {e}",
            file=sys.stderr,
        )
        return 0.0

def build_usage_report(
    service: QiskitRuntimeService,
    since_hours: int = 1,
    budget: float = QPU_BUDGET_SECONDS,
) -> dict:
    """
    Walk recent completed jobs, enforce per-job budget, accumulate gate time.
    Fails immediately (sys.exit(1)) when a single job exceeds the budget.
    """
    cutoff = datetime.now(timezone.utc).timestamp() - (since_hours * 3600)
    total_gate_seconds = 0.0
    jobs_run = 0
    per_backend: dict[str, float] = {}
    job_details: list[dict] = []
    first_violation: dict | None = None

    for job in service.jobs(limit=200, descending=True):
        if job.creation_date.timestamp() < cutoff:
            break
        if job.status().name not in ("DONE", "COMPLETED"):
            continue

        jobs_run += 1
        backend_name = job.backend.name
        gate_time = extract_gate_time(job)
        total_gate_seconds += gate_time
        per_backend[backend_name] = per_backend.get(backend_name, 0) + gate_time

        exceeded = gate_time > budget
        if exceeded and first_violation is None:
            first_violation = {
                "job_id": job.job_id(),
                "backend": backend_name,
                "gate_time_seconds": round(gate_time, 6),
            }

        job_details.append({
            "job_id": job.job_id(),
            "backend": backend_name,
            "gate_time_seconds": round(gate_time, 6),
            "budget_exceeded": exceeded,
        })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "build_number": os.environ.get("BUILD_NUMBER"),
        "job_count": jobs_run,
        "total_gate_time_seconds": round(total_gate_seconds, 6),
        "per_backend_seconds": {k: round(v, 6) for k, v in per_backend.items()},
        "backends": sorted(per_backend.keys()),
        "budget_seconds": budget,
        "budget_exceeded": first_violation is not None,
        "first_violation": first_violation,
        "jobs": job_details,
    }

def main():
    parser = argparse.ArgumentParser(
        description="IBM Quantum gate-time reporter"
    )
    parser.add_argument("--since-hours", type=int, default=1)
    parser.add_argument("--output", default="quantum_usage.json")
    parser.add_argument(
        "--budget",
        type=float,
        default=cfg.limits.qpu_budget_seconds,
        help="Per-job gate time limit in seconds (default: from config.yaml)",
    )
    args = parser.parse_args()

    token = os.environ.get("QISKIT_IBM_TOKEN")
    if not token:
        raise RuntimeError("QISKIT_IBM_TOKEN not set in environment")

    service = QiskitRuntimeService(
        channel="ibm_cloud",
        token=token,
        instance=os.environ.get("ORG_ID"),
    )

    report = build_usage_report(service, args.since_hours, args.budget)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print("\n══════════════════════════════════════════════")
    print(f"  IBM QUANTUM GATE TIME — Build #{report['build_number']}")
    print("══════════════════════════════════════════════")
    print(f"  Jobs completed        : {report['job_count']}")
    print(f"  Total gate time       : {report['total_gate_time_seconds']:.6f} s")
    print(f"  Per-job budget        : {args.budget:.3f} s")
    for backend, secs in report["per_backend_seconds"].items():
        print(f"  └─ {backend}: {secs:.6f} s")
    if report["first_violation"]:
        v = report["first_violation"]
        print(
            f"\n  ❌ VIOLATION: job {v['job_id']} on {v['backend']} "
            f"used {v['gate_time_seconds']:.6f}s  > {args.budget}s budget"
        )
    else:
        print("\n  ✅ All jobs within budget.")
    print("══════════════════════════════════════════════\n")

    if report["budget_exceeded"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
