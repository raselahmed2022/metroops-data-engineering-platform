from pathlib import Path
import pandas as pd


# =========================================================
# PATHS
# =========================================================

GOLD_DIR = Path("data/gold")


print("\n===================================")
print("GOLD DATA VALIDATION")
print("===================================")


# =========================================================
# 1. MAINTENANCE PERFORMANCE
# Grain: one row per work order
# =========================================================

maintenance = pd.read_parquet(
    GOLD_DIR / "maintenance_performance.parquet"
)

print("\n--- MAINTENANCE PERFORMANCE ---")
print("Rows:", len(maintenance))

duplicate_work_orders = (
    maintenance["work_order_id"]
    .duplicated()
    .sum()
)

print("Duplicate work_order_id:", duplicate_work_orders)

missing_work_order_id = (
    maintenance["work_order_id"]
    .isna()
    .sum()
)

print("Missing work_order_id:", missing_work_order_id)

invalid_costs = maintenance[
    maintenance["total_maintenance_cost_eur"] < 0
]

print("Negative maintenance costs:", len(invalid_costs))

if (
    len(maintenance) == 49
    and duplicate_work_orders == 0
    and missing_work_order_id == 0
    and len(invalid_costs) == 0
):
    print("Maintenance performance: PASSED")
else:
    print("Maintenance performance: FAILED")


# =========================================================
# 2. FAULT SUMMARY
# Grain: one row per fault
# =========================================================

faults = pd.read_parquet(
    GOLD_DIR / "fault_summary.parquet"
)

print("\n--- FAULT SUMMARY ---")
print("Rows:", len(faults))

duplicate_faults = (
    faults["fault_id"]
    .duplicated()
    .sum()
)

print("Duplicate fault_id:", duplicate_faults)

missing_fault_id = (
    faults["fault_id"]
    .isna()
    .sum()
)

print("Missing fault_id:", missing_fault_id)

invalid_duration = faults[
    faults["fault_duration_minutes"] < 0
]

print("Negative fault durations:", len(invalid_duration))

if (
    len(faults) == 55
    and duplicate_faults == 0
    and missing_fault_id == 0
    and len(invalid_duration) == 0
):
    print("Fault summary: PASSED")
else:
    print("Fault summary: FAILED")


# =========================================================
# 3. COMPRESSOR DAILY HEALTH
# Grain: one row per compressor per day
# =========================================================

daily_health = pd.read_parquet(
    GOLD_DIR / "compressor_daily_health.parquet"
)

print("\n--- COMPRESSOR DAILY HEALTH ---")
print("Rows:", len(daily_health))

duplicate_days = daily_health.duplicated(
    subset=[
        "compressor_id",
        "reading_date"
    ]
).sum()

print(
    "Duplicate compressor-date rows:",
    duplicate_days
)

missing_required = daily_health[
    daily_health[
        [
            "compressor_id",
            "reading_date",
            "reading_count"
        ]
    ].isna().any(axis=1)
]

print(
    "Rows missing required fields:",
    len(missing_required)
)

invalid_reading_count = daily_health[
    daily_health["reading_count"] <= 0
]

print(
    "Invalid reading counts:",
    len(invalid_reading_count)
)

if (
    len(daily_health) == 212
    and duplicate_days == 0
    and len(missing_required) == 0
    and len(invalid_reading_count) == 0
):
    print("Compressor daily health: PASSED")
else:
    print("Compressor daily health: FAILED")


# =========================================================
# FINAL RESULT
# =========================================================

print("\n===================================")
print("GOLD VALIDATION COMPLETE")
print("===================================")