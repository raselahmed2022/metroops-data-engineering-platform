from pathlib import Path
import pandas as pd


SILVER_DIR = Path("data/silver")
SENSOR_DIR = SILVER_DIR / "sensor_readings"


print("\n===================================")
print("SILVER DATA VALIDATION")
print("===================================")


# =========================================================
# 1. SENSOR ROW COUNT VALIDATION
# =========================================================

sensor_files = sorted(
    SENSOR_DIR.glob("part_*.parquet")
)

print("\nSensor files found:", len(sensor_files))

total_sensor_rows = 0

for file in sensor_files:
    df = pd.read_parquet(file)

    total_sensor_rows += len(df)

print("Total Silver sensor rows:", total_sensor_rows)


expected_sensor_rows = 1_516_948

if total_sensor_rows == expected_sensor_rows:
    print("Sensor row count: PASSED")
else:
    print("Sensor row count: FAILED")


    # =========================================================
# 2. REQUIRED FIELD VALIDATION
# =========================================================

missing_required_total = 0

for file in sensor_files:

    df = pd.read_parquet(file)

    missing_required = df[
        df[
            [
                "reading_id",
                "compressor_id",
                "timestamp"
            ]
        ].isna().any(axis=1)
    ]

    missing_required_total += len(missing_required)


print(
    "Rows missing required fields:",
    missing_required_total
)

if missing_required_total == 0:
    print("Required fields: PASSED")
else:
    print("Required fields: FAILED")


    # =========================================================
# 3. DUPLICATE READING ID VALIDATION
# =========================================================

reading_ids = []

for file in sensor_files:

    df = pd.read_parquet(
        file,
        columns=["reading_id"]
    )

    reading_ids.append(df)


all_reading_ids = pd.concat(
    reading_ids,
    ignore_index=True
)

duplicate_reading_ids = (
    all_reading_ids["reading_id"]
    .duplicated()
    .sum()
)

print(
    "Duplicate reading IDs:",
    duplicate_reading_ids
)

if duplicate_reading_ids == 0:
    print("Reading ID uniqueness: PASSED")
else:
    print("Reading ID uniqueness: FAILED")


    # =========================================================
# 4. TIMESTAMP VALIDATION
# =========================================================

timestamp_errors = 0

for file in sensor_files:

    df = pd.read_parquet(
        file,
        columns=["timestamp"]
    )

    if not pd.api.types.is_datetime64_any_dtype(
        df["timestamp"]
    ):
        timestamp_errors += 1


print(
    "Files with invalid timestamp datatype:",
    timestamp_errors
)

if timestamp_errors == 0:
    print("Timestamp datatype: PASSED")
else:
    print("Timestamp datatype: FAILED")


    # =========================================================
# 5. WORK ORDER VALIDATION
# =========================================================

work_orders = pd.read_parquet(
    SILVER_DIR / "work_orders.parquet"
)

print("\nWork order rows:", len(work_orders))


duplicate_work_orders = (
    work_orders["work_order_id"]
    .duplicated()
    .sum()
)

print(
    "Duplicate work order IDs:",
    duplicate_work_orders
)


invalid_dates = work_orders[
    work_orders["closed_at"]
    < work_orders["opened_at"]
]

print(
    "Invalid work order date ranges:",
    len(invalid_dates)
)


invalid_corrective = work_orders[
    (work_orders["maintenance_type"] == "Corrective")
    & (work_orders["fault_id"].isna())
]

print(
    "Corrective work orders missing fault ID:",
    len(invalid_corrective)
)

