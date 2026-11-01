from pathlib import Path
import pandas as pd

BRONZE_DIR = Path("data/bronze")
SILVER_DIR = Path("data/silver")

SILVER_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# 1. Read Bronze compressor data
# -----------------------------

input_file = BRONZE_DIR / "compressors.parquet"

df = pd.read_parquet(input_file)

print("\n--- COMPRESSORS SILVER TRANSFORMATION ---")
print("Rows read:", len(df))


# -----------------------------
# 2. Convert date columns
# -----------------------------

df["commissioned_date"] = pd.to_datetime(
    df["commissioned_date"],
    errors="coerce"
)

df["planned_replacement_date"] = pd.to_datetime(
    df["planned_replacement_date"],
    errors="coerce"
)


# -----------------------------
# 3. Remove duplicate compressor IDs
# -----------------------------

df = df.drop_duplicates(
    subset=["compressor_id"],
    keep="first"
)


# -----------------------------
# 4. Validate important fields
# -----------------------------

df = df.dropna(
    subset=[
        "compressor_id",
        "facility_id"
    ]
)


# -----------------------------
# 5. Validate numeric values
# -----------------------------

df = df[
    (df["max_pressure_bar"] >= 0)
    & (df["max_oil_temp_c"] >= 0)
    & (df["max_motor_current_a"] >= 0)
]


# -----------------------------
# 6. Clean text columns
# -----------------------------

text_columns = [
    "compressor_id",
    "facility_id",
    "asset_name",
    "asset_type",
    "asset_status",
    "criticality",
    "manufacturer"
]

for column in text_columns:
    df[column] = df[column].str.strip()


# -----------------------------
# 7. Write Silver Parquet
# -----------------------------

output_file = SILVER_DIR / "compressors.parquet"

df.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(df))
print("Silver file:", output_file)
print("TRANSFORMATION COMPLETE")


# =========================================================
# FAULT EVENTS
# =========================================================

print("\n--- FAULT EVENTS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "fault_events.parquet"

faults = pd.read_parquet(input_file)

print("Rows read:", len(faults))

# 1. Convert timestamps
faults["fault_start"] = pd.to_datetime(
    faults["fault_start"],
    errors="coerce"
)

faults["fault_end"] = pd.to_datetime(
    faults["fault_end"],
    errors="coerce"
)

# 2. Remove duplicate fault IDs
faults = faults.drop_duplicates(
    subset=["fault_id"],
    keep="first"
)

# 3. Required fields
faults = faults.dropna(
    subset=[
        "fault_id",
        "compressor_id",
        "fault_start"
    ]
)

# 4. Clean text columns
fault_text_columns = [
    "fault_id",
    "compressor_id",
    "fault_type",
    "severity",
    "detected_by",
    "fault_status"
]

for column in fault_text_columns:
    faults[column] = faults[column].str.strip()

# 5. Validate timestamps
invalid_dates = faults[
    faults["fault_end"] < faults["fault_start"]
]

print("Invalid fault date ranges:", len(invalid_dates))

# Keep only valid date ranges
faults = faults[
    faults["fault_end"] >= faults["fault_start"]
]

# 6. Write Silver
output_file = SILVER_DIR / "fault_events.parquet"

faults.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(faults))
print("Silver file:", output_file)


# =========================================================
# WORK ORDERS
# =========================================================

print("\n--- WORK ORDERS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "work_orders.parquet"

work_orders = pd.read_parquet(input_file)

print("Rows read:", len(work_orders))


# 1. Convert timestamps
work_orders["opened_at"] = pd.to_datetime(
    work_orders["opened_at"],
    errors="coerce"
)

work_orders["closed_at"] = pd.to_datetime(
    work_orders["closed_at"],
    errors="coerce"
)


# 2. Remove duplicate work order IDs
work_orders = work_orders.drop_duplicates(
    subset=["work_order_id"],
    keep="first"
)


# 3. Required fields
work_orders = work_orders.dropna(
    subset=[
        "work_order_id",
        "compressor_id",
        "technician_id",
        "maintenance_type",
        "opened_at",
        "closed_at"
    ]
)


# 4. Clean text columns
work_order_text_columns = [
    "work_order_id",
    "compressor_id",
    "fault_id",
    "technician_id",
    "maintenance_type",
    "priority",
    "status",
    "resolution"
]

for column in work_order_text_columns:
    work_orders[column] = work_orders[column].str.strip()


# 5. Validate date logic
invalid_dates = work_orders[
    work_orders["closed_at"] < work_orders["opened_at"]
]

print("Invalid work order date ranges:", len(invalid_dates))

work_orders = work_orders[
    work_orders["closed_at"] >= work_orders["opened_at"]
]


# 6. Validate numeric values
invalid_numeric = work_orders[
    (work_orders["labor_hours"] < 0)
    | (work_orders["external_cost_eur"] < 0)
]

print("Invalid numeric rows:", len(invalid_numeric))

work_orders = work_orders[
    (work_orders["labor_hours"] >= 0)
    & (work_orders["external_cost_eur"] >= 0)
]


# 7. Validate fault_id business rule
invalid_fault_rule = work_orders[
    (work_orders["maintenance_type"] == "Corrective")
    & (work_orders["fault_id"].isna())
]

print(
    "Corrective work orders missing fault_id:",
    len(invalid_fault_rule)
)


# Remove only invalid corrective rows
work_orders = work_orders[
    ~(
        (work_orders["maintenance_type"] == "Corrective")
        & (work_orders["fault_id"].isna())
    )
]


# 8. Write Silver
output_file = SILVER_DIR / "work_orders.parquet"

work_orders.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(work_orders))
print("Silver file:", output_file)



# =========================================================
# MAINTENANCE EVENTS
# =========================================================

print("\n--- MAINTENANCE EVENTS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "maintenance_events.parquet"

maintenance = pd.read_parquet(input_file)

print("Rows read:", len(maintenance))


# 1. Convert maintenance date
maintenance["maintenance_date"] = pd.to_datetime(
    maintenance["maintenance_date"],
    errors="coerce"
)


# 2. Remove duplicate maintenance IDs
maintenance = maintenance.drop_duplicates(
    subset=["maintenance_id"],
    keep="first"
)


# 3. Required fields
maintenance = maintenance.dropna(
    subset=[
        "maintenance_id",
        "work_order_id",
        "compressor_id",
        "technician_id",
        "maintenance_date",
        "maintenance_type"
    ]
)


# 4. Clean text columns
maintenance_text_columns = [
    "maintenance_id",
    "work_order_id",
    "compressor_id",
    "technician_id",
    "maintenance_type",
    "resolution"
]

for column in maintenance_text_columns:
    maintenance[column] = maintenance[column].str.strip()


# 5. Validate numeric values
invalid_numeric = maintenance[
    (maintenance["labor_hours"] < 0)
    | (maintenance["downtime_minutes"] < 0)
    | (maintenance["maintenance_cost_eur"] < 0)
]

print("Invalid numeric rows:", len(invalid_numeric))

maintenance = maintenance[
    (maintenance["labor_hours"] >= 0)
    & (maintenance["downtime_minutes"] >= 0)
    & (maintenance["maintenance_cost_eur"] >= 0)
]


# 6. Write Silver
output_file = SILVER_DIR / "maintenance_events.parquet"

maintenance.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(maintenance))
print("Silver file:", output_file)


# =========================================================
# FACILITIES
# =========================================================

print("\n--- FACILITIES SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "facilities.parquet"

facilities = pd.read_parquet(input_file)

print("Rows read:", len(facilities))


# 1. Convert opened_date to datetime
facilities["opened_date"] = pd.to_datetime(
    facilities["opened_date"],
    errors="coerce"
)


# 2. Remove duplicate facility IDs
facilities = facilities.drop_duplicates(
    subset=["facility_id"],
    keep="first"
)


# 3. Required fields
facilities = facilities.dropna(
    subset=[
        "facility_id",
        "facility_name",
        "city",
        "country",
        "opened_date"
    ]
)


# 4. Clean text columns
facility_text_columns = [
    "facility_id",
    "facility_name",
    "city",
    "country",
    "facility_type",
    "operating_hours"
]

for column in facility_text_columns:
    facilities[column] = facilities[column].str.strip()


# 5. Write Silver
output_file = SILVER_DIR / "facilities.parquet"

facilities.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(facilities))
print("Silver file:", output_file)



# =========================================================
# TECHNICIANS
# =========================================================

print("\n--- TECHNICIANS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "technicians.parquet"

technicians = pd.read_parquet(input_file)

print("Rows read:", len(technicians))


# 1. Remove duplicate technician IDs
technicians = technicians.drop_duplicates(
    subset=["technician_id"],
    keep="first"
)


# 2. Required fields
technicians = technicians.dropna(
    subset=[
        "technician_id",
        "technician_name",
        "specialization",
        "skill_level",
        "home_facility_id"
    ]
)


# 3. Clean text columns
technician_text_columns = [
    "technician_id",
    "technician_name",
    "specialization",
    "skill_level",
    "home_facility_id"
]

for column in technician_text_columns:
    technicians[column] = technicians[column].str.strip()


# 4. Validate hourly cost
invalid_cost = technicians[
    technicians["hourly_cost_eur"] < 0
]

print("Invalid hourly cost rows:", len(invalid_cost))

technicians = technicians[
    technicians["hourly_cost_eur"] >= 0
]


# 5. Write Silver
output_file = SILVER_DIR / "technicians.parquet"

technicians.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(technicians))
print("Silver file:", output_file)


# =========================================================
# SPARE PARTS
# =========================================================

print("\n--- SPARE PARTS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "spare_parts.parquet"

spare_parts = pd.read_parquet(input_file)

print("Rows read:", len(spare_parts))


# 1. Remove duplicate part IDs
spare_parts = spare_parts.drop_duplicates(
    subset=["part_id"],
    keep="first"
)


# 2. Required fields
spare_parts = spare_parts.dropna(
    subset=[
        "part_id",
        "part_name",
        "part_category",
        "unit_cost_eur",
        "stock_qty",
        "reorder_level"
    ]
)


# 3. Clean text columns
spare_part_text_columns = [
    "part_id",
    "part_name",
    "part_category"
]

for column in spare_part_text_columns:
    spare_parts[column] = spare_parts[column].str.strip()


# 4. Validate numeric values
invalid_numeric = spare_parts[
    (spare_parts["unit_cost_eur"] < 0)
    | (spare_parts["stock_qty"] < 0)
    | (spare_parts["reorder_level"] < 0)
]

print("Invalid numeric rows:", len(invalid_numeric))

spare_parts = spare_parts[
    (spare_parts["unit_cost_eur"] >= 0)
    & (spare_parts["stock_qty"] >= 0)
    & (spare_parts["reorder_level"] >= 0)
]


# 5. Write Silver
output_file = SILVER_DIR / "spare_parts.parquet"

spare_parts.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(spare_parts))
print("Silver file:", output_file)


# =========================================================
# WORK ORDER PARTS
# =========================================================

print("\n--- WORK ORDER PARTS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "work_order_parts.parquet"

work_order_parts = pd.read_parquet(input_file)

print("Rows read:", len(work_order_parts))


# 1. Required fields
work_order_parts = work_order_parts.dropna(
    subset=[
        "work_order_id",
        "part_id",
        "quantity_used",
        "unit_cost_eur",
        "line_cost_eur"
    ]
)


# 2. Clean text columns
work_order_part_text_columns = [
    "work_order_id",
    "part_id"
]

for column in work_order_part_text_columns:
    work_order_parts[column] = (
        work_order_parts[column]
        .str.strip()
    )


# 3. Remove exact duplicate rows
work_order_parts = work_order_parts.drop_duplicates()


# 4. Validate numeric values
invalid_numeric = work_order_parts[
    (work_order_parts["quantity_used"] <= 0)
    | (work_order_parts["unit_cost_eur"] < 0)
    | (work_order_parts["line_cost_eur"] < 0)
]

print("Invalid numeric rows:", len(invalid_numeric))

work_order_parts = work_order_parts[
    (work_order_parts["quantity_used"] > 0)
    & (work_order_parts["unit_cost_eur"] >= 0)
    & (work_order_parts["line_cost_eur"] >= 0)
]


# 5. Write Silver
output_file = SILVER_DIR / "work_order_parts.parquet"

work_order_parts.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(work_order_parts))
print("Silver file:", output_file)




# =========================================================
# OPERATING TARGETS
# =========================================================

print("\n--- OPERATING TARGETS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "operating_targets.parquet"

operating_targets = pd.read_parquet(input_file)

print("Rows read:", len(operating_targets))


# 1. Remove duplicate target IDs
operating_targets = operating_targets.drop_duplicates(
    subset=["target_id"],
    keep="first"
)


# 2. Required fields
operating_targets = operating_targets.dropna(
    subset=[
        "target_id",
        "compressor_id",
        "metric_name",
        "unit",
        "lower_limit",
        "upper_limit"
    ]
)


# 3. Clean text columns
target_text_columns = [
    "target_id",
    "compressor_id",
    "metric_name",
    "unit",
    "description"
]

for column in target_text_columns:
    operating_targets[column] = (
        operating_targets[column]
        .str.strip()
    )


# 4. Validate operating limits
invalid_limits = operating_targets[
    operating_targets["lower_limit"]
    > operating_targets["upper_limit"]
]

print("Invalid operating limit rows:", len(invalid_limits))


# Keep only logical ranges
operating_targets = operating_targets[
    operating_targets["lower_limit"]
    <= operating_targets["upper_limit"]
]


# 5. Write Silver
output_file = SILVER_DIR / "operating_targets.parquet"

operating_targets.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(operating_targets))
print("Silver file:", output_file)



# =========================================================
# DAILY OPERATING KPIS
# =========================================================

print("\n--- DAILY OPERATING KPIS SILVER TRANSFORMATION ---")

input_file = BRONZE_DIR / "daily_operating_kpis.parquet"

daily_kpis = pd.read_parquet(input_file)

print("Rows read:", len(daily_kpis))


# 1. Convert timestamp
daily_kpis["timestamp"] = pd.to_datetime(
    daily_kpis["timestamp"],
    errors="coerce"
)


# 2. Check duplicates
duplicate_count = daily_kpis.duplicated(
    subset=["compressor_id", "timestamp"]
).sum()

print("Duplicate compressor-timestamp rows:", duplicate_count)


# 3. Check missing required identifiers
missing_required = daily_kpis[
    daily_kpis[
        ["compressor_id", "timestamp"]
    ].isna().any(axis=1)
]

print("Rows missing compressor/timestamp:", len(missing_required))


# 4. Remove duplicate rows
daily_kpis = daily_kpis.drop_duplicates(
    subset=["compressor_id", "timestamp"],
    keep="first"
)


# 5. Remove rows missing identifiers
daily_kpis = daily_kpis.dropna(
    subset=["compressor_id", "timestamp"]
)


# 6. Clean compressor ID
daily_kpis["compressor_id"] = (
    daily_kpis["compressor_id"]
    .str.strip()
)


# 7. Check availability values that are missing
missing_availability = daily_kpis[
    daily_kpis["availability_pct"].isna()
]

print("Rows with missing availability:", len(missing_availability))


# 8. Check whether missing availability is explainable by zero samples
valid_missing_availability = daily_kpis[
    daily_kpis["availability_pct"].isna()
    & (daily_kpis["total_samples"] == 0)
]

print(
    "Valid missing availability due to zero samples:",
    len(valid_missing_availability)
)


# 9. Invalid rows:
# negative samples/hours OR
# availability outside 0-100 when availability exists
invalid_kpis = daily_kpis[
    (daily_kpis["operating_samples"] < 0)
    | (daily_kpis["total_samples"] < 0)
    | (daily_kpis["estimated_operating_hours"] < 0)
    | (
        daily_kpis["availability_pct"].notna()
        & (
            (daily_kpis["availability_pct"] < 0)
            | (daily_kpis["availability_pct"] > 100)
        )
    )
]

print("Invalid KPI rows:", len(invalid_kpis))


# 10. Remove truly invalid rows only
daily_kpis = daily_kpis.drop(
    index=invalid_kpis.index
)


# 11. Write Silver
output_file = SILVER_DIR / "daily_operating_kpis.parquet"

daily_kpis.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("Rows written:", len(daily_kpis))
print("Silver file:", output_file)