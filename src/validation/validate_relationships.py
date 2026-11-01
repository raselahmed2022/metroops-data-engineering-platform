from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")

faults = pd.read_csv(RAW_DIR / "fault_events.csv")
work_orders = pd.read_csv(RAW_DIR / "work_orders.csv")
maintenance = pd.read_csv(RAW_DIR / "maintenance_events.csv")

# ---------------------------------
# 1. Work Orders -> Maintenance
# ---------------------------------

work_order_ids = set(work_orders["work_order_id"])
maintenance_work_order_ids = set(maintenance["work_order_id"])

missing_maintenance = (
    work_order_ids - maintenance_work_order_ids
)

orphan_maintenance = (
    maintenance_work_order_ids - work_order_ids
)

print("\nWork orders without maintenance:")
print(missing_maintenance)

print("\nMaintenance records without a valid work order:")
print(orphan_maintenance)


# ---------------------------------
# 2. Faults -> Corrective Work Orders
# ---------------------------------

corrective_orders = work_orders[
    work_orders["maintenance_type"] == "Corrective"
]

fault_ids = set(faults["fault_id"])

corrective_fault_ids = set(
    corrective_orders["fault_id"].dropna()
)

faults_without_work_orders = (
    fault_ids - corrective_fault_ids
)

invalid_fault_references = (
    corrective_fault_ids - fault_ids
)

print("\nFaults without corrective work orders:")
print(faults_without_work_orders)

print("\nWork orders referencing invalid fault IDs:")
print(invalid_fault_references)