"""
CI replacement for hardware-data.ipynb.
Collects real hardware data, validates qubit group selection,
and writes CSVs as pipeline artifacts.
"""
import pytest

from src.hardware_data import (
    extract_hardware_data,
    find_optimal_qubit_groups,
    save_hardware_data_csv,
    save_optimal_groups_csv,
)

@pytest.mark.requires_ibm
def test_extract_hardware_data(ibm_service):
    data = extract_hardware_data(ibm_service)
    assert len(data) > 0, "No hardware data returned"

    for row in data:
        assert row["Backend"], "Missing backend name"
        assert row["Num_Qubits"] >= 2
        assert (
            row["Readout_Error_Percent"] is None
            or 0.0 <= row["Readout_Error_Percent"] <= 100.0
        )

    save_hardware_data_csv(data, "hardware/hardware.csv")
    print(
        f"  Collected {len(data)} qubit records across "
        f"{len(set(r['Backend'] for r in data))} backends"
    )

@pytest.mark.requires_ibm
def test_optimal_qubit_groups(ibm_service):
    data = extract_hardware_data(ibm_service)
    groups = find_optimal_qubit_groups(data)

    assert len(groups) > 0, "No optimal groups found"

    for backend, group in groups.items():
        assert group["size"] >= 2
        assert group["max_error"] <= 100.0
        assert group["avg_error"] <= group["max_error"]

    save_optimal_groups_csv(groups, "hardware/optimal_qubit_groups.csv")
    print(f"  Optimal groups found for {len(groups)} backends")
