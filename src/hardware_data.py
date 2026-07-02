"""
hardware_data.py
Replaces hardware-data.ipynb for CI use.
Collects readout error + noise model data from REAL IBM backends via Qiskit Runtime.
Outputs CSV files matching the notebook's schema.
"""
import csv
import os
from itertools import combinations

from qiskit_ibm_runtime import QiskitRuntimeService

def extract_hardware_data(service: QiskitRuntimeService) -> list[dict]:
    """
    Pull qubit-level readout error + noise metadata from all available real backends.
    Matches the schema of hardware-data.ipynb's extract_hardware_data().
    """
    all_data = []

    for backend in service.backends(simulator=False, operational=True):
        try:
            props = backend.properties()
            n_qubits = backend.num_qubits
        except Exception:
            continue

        for qubit in range(n_qubits):
            try:
                readout_error = props.readout_error(qubit)
            except Exception:
                readout_error = None

            all_data.append({
                "Backend": backend.name,
                "Num_Qubits": n_qubits,
                "Qubit": qubit,
                "Readout_Error_Percent": (
                    round(readout_error * 100, 2)
                    if readout_error is not None
                    else None
                ),
            })

    return all_data

def find_optimal_qubit_groups(
    data: list[dict], max_group_size: int = 5, min_group_size: int = 2
) -> dict:
    """
    Port of find_optimal_qubit_groups() from hardware-data.ipynb.
    Selects qubit groups with lowest average readout error per backend.
    """
    backend_data: dict[str, list] = {}
    for row in data:
        if row["Readout_Error_Percent"] is None:
            continue
        backend_data.setdefault(row["Backend"], []).append({
            "qubit": row["Qubit"],
            "error": row["Readout_Error_Percent"],
        })

    optimal_groups = {}

    for backend, qubits in backend_data.items():
        qubits_sorted = sorted(qubits, key=lambda x: x["error"])
        best_groups = []

        for group_size in range(max_group_size, min_group_size - 1, -1):
            if len(qubits_sorted) < group_size:
                continue
            for combo in combinations(qubits_sorted[:10], group_size):
                errors = [q["error"] for q in combo]
                best_groups.append({
                    "qubits": [q["qubit"] for q in combo],
                    "errors": errors,
                    "avg_error": round(sum(errors) / len(errors), 3),
                    "min_error": round(min(errors), 3),
                    "max_error": round(max(errors), 3),
                    "size": group_size,
                })

        best_groups.sort(key=lambda x: (-x["size"], x["max_error"]))
        if best_groups:
            optimal_groups[backend] = best_groups[0]

    return optimal_groups

def save_hardware_data_csv(data: list[dict], path: str = "hardware/hardware.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = ["Backend", "Num_Qubits", "Qubit", "Readout_Error_Percent"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

def save_optimal_groups_csv(groups: dict, path: str = "hardware/optimal_qubit_groups.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "Backend", "Group Size", "Qubits", "Individual Errors",
        "Min Error", "Max Error", "Average Error",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for backend, g in groups.items():
            writer.writerow({
                "Backend": backend,
                "Group Size": g["size"],
                "Qubits": ";".join(map(str, g["qubits"])),
                "Individual Errors": ";".join(map(str, g["errors"])),
                "Min Error": g["min_error"],
                "Max Error": g["max_error"],
                "Average Error": g["avg_error"],
            })
