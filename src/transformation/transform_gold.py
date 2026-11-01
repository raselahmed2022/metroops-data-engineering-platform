from pathlib import Path
import pandas as pd


# =========================================================
# PATHS
# =========================================================

SILVER_DIR = Path("data/silver")
GOLD_DIR = Path("data/gold")

GOLD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# LOAD SILVER TABLES
# =========================================================

work_orders_df = pd.read_parquet(
    SILVER_DIR / "work_orders.parquet"
)

maintenance_df = pd.read_parquet(
    SILVER_DIR / "maintenance_events.parquet"
)

technicians_df = pd.read_parquet(
    SILVER_DIR / "technicians.parquet"
)

faults_df = pd.read_parquet(
    SILVER_DIR / "fault_events.parquet"
)

# =========================================================
# INSPECT INPUT TABLES
# =========================================================

print("Work orders:", work_orders_df.shape)
print("Maintenance:", maintenance_df.shape)
print("Technicians:", technicians_df.shape)

print("\nWork order columns:")
print(work_orders_df.columns.tolist())

print("\nMaintenance columns:")
print(maintenance_df.columns.tolist())

print("\nTechnician columns:")
print(technicians_df.columns.tolist())


# =========================================================
# GOLD TABLE 1: MAINTENANCE PERFORMANCE
# Grain: one row per work order / maintenance event
# =========================================================

print("\n--- BUILDING MAINTENANCE PERFORMANCE GOLD TABLE ---")


# ---------------------------------------------------------
# 1. Select useful work-order columns
# ---------------------------------------------------------

work_orders_gold = work_orders_df[
    [
        "work_order_id",
        "compressor_id",
        "fault_id",
        "technician_id",
        "maintenance_type",
        "priority",
        "opened_at",
        "closed_at",
        "status",
        "external_cost_eur"
    ]
].copy()


# ---------------------------------------------------------
# 2. Select useful maintenance columns
# ---------------------------------------------------------

maintenance_gold = maintenance_df[
    [
        "maintenance_id",
        "work_order_id",
        "maintenance_date",
        "labor_hours",
        "downtime_minutes",
        "maintenance_cost_eur",
        "resolution"
    ]
].copy()


# ---------------------------------------------------------
# 3. Merge work orders with maintenance
# ---------------------------------------------------------

maintenance_performance = work_orders_gold.merge(
    maintenance_gold,
    on="work_order_id",
    how="left",
    validate="one_to_one"
)


print(
    "Rows after work-order + maintenance merge:",
    len(maintenance_performance)
)

print(
    "Missing maintenance records:",
    maintenance_performance["maintenance_id"]
    .isna()
    .sum()
)



# ---------------------------------------------------------
# 4. Select useful technician columns
# ---------------------------------------------------------

technicians_gold = technicians_df[
    [
        "technician_id",
        "technician_name",
        "specialization",
        "skill_level",
        "home_facility_id",
        "hourly_cost_eur"
    ]
].copy()


# ---------------------------------------------------------
# 5. Merge technician information
# ---------------------------------------------------------

maintenance_performance = maintenance_performance.merge(
    technicians_gold,
    on="technician_id",
    how="left",
    validate="many_to_one"
)

print(
    "Rows after technician merge:",
    len(maintenance_performance)
)

print(
    "Missing technician matches:",
    maintenance_performance["technician_name"]
    .isna()
    .sum()
)


# ---------------------------------------------------------
# 6. Create business-ready calculated fields
# ---------------------------------------------------------

# Work order duration in hours
maintenance_performance["work_order_duration_hours"] = (
    maintenance_performance["closed_at"]
    - maintenance_performance["opened_at"]
).dt.total_seconds() / 3600


# Downtime in hours
maintenance_performance["downtime_hours"] = (
    maintenance_performance["downtime_minutes"] / 60
)


# Total maintenance cost
# maintenance_cost_eur + external_cost_eur
maintenance_performance["total_maintenance_cost_eur"] = (
    maintenance_performance["maintenance_cost_eur"]
    + maintenance_performance["external_cost_eur"]
)


# Technician labor cost
maintenance_performance["technician_labor_cost_eur"] = (
    maintenance_performance["labor_hours"]
    * maintenance_performance["hourly_cost_eur"]
)


print("\nGold table preview:")

print(
    maintenance_performance[
        [
            "work_order_id",
            "maintenance_type",
            "priority",
            "technician_name",
            "labor_hours",
            "downtime_hours",
            "work_order_duration_hours",
            "maintenance_cost_eur",
            "external_cost_eur",
            "total_maintenance_cost_eur",
            "technician_labor_cost_eur"
        ]
    ].head()
)


# ---------------------------------------------------------
# 7. Write Gold table
# ---------------------------------------------------------

output_file = GOLD_DIR / "maintenance_performance.parquet"

maintenance_performance.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("\nRows written:", len(maintenance_performance))
print("Gold file:", output_file)



# =========================================================
# GOLD TABLE 2: FAULT SUMMARY
# Grain: one row per fault event
# =========================================================

print("\n--- BUILDING FAULT SUMMARY GOLD TABLE ---")


# ---------------------------------------------------------
# 1. Select useful fault columns
# ---------------------------------------------------------

fault_summary = faults_df[
    [
        "fault_id",
        "compressor_id",
        "fault_start",
        "fault_end",
        "fault_type",
        "severity",
        "oil_temperature_c",
        "motor_current_a",
        "tp3_pressure_bar",
        "detected_by",
        "fault_status"
    ]
].copy()


# ---------------------------------------------------------
# 2. Calculate fault duration
# ---------------------------------------------------------

fault_summary["fault_duration_minutes"] = (
    fault_summary["fault_end"]
    - fault_summary["fault_start"]
).dt.total_seconds() / 60


# ---------------------------------------------------------
# 3. Get corrective work orders only
# ---------------------------------------------------------

corrective_work_orders = work_orders_df[
    work_orders_df["maintenance_type"] == "Corrective"
][
    [
        "work_order_id",
        "fault_id",
        "priority",
        "opened_at",
        "closed_at"
    ]
].copy()


print(
    "Corrective work orders:",
    len(corrective_work_orders)
)


# Check whether one fault has multiple corrective work orders
duplicate_fault_links = (
    corrective_work_orders["fault_id"]
    .duplicated()
    .sum()
)

print(
    "Duplicate fault IDs in corrective work orders:",
    duplicate_fault_links
)


# ---------------------------------------------------------
# 4. Merge corrective work order information into faults
# ---------------------------------------------------------

fault_summary = fault_summary.merge(
    corrective_work_orders,
    on="fault_id",
    how="left",
    validate="one_to_one"
)

print(
    "Rows after fault + corrective work order merge:",
    len(fault_summary)
)

print(
    "Faults without corrective work order:",
    fault_summary["work_order_id"]
    .isna()
    .sum()
)


# ---------------------------------------------------------
# 5. Create business-ready fault indicators
# ---------------------------------------------------------

fault_summary["has_corrective_work_order"] = (
    fault_summary["work_order_id"].notna()
)



# ---------------------------------------------------------
# 6. Write Gold table
# ---------------------------------------------------------

output_file = GOLD_DIR / "fault_summary.parquet"

fault_summary.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("\nRows written:", len(fault_summary))
print("Gold file:", output_file)


# =========================================================
# GOLD TABLE 3: COMPRESSOR DAILY HEALTH
# Grain: one row per compressor per day
# =========================================================

print("\n--- BUILDING COMPRESSOR DAILY HEALTH GOLD TABLE ---")

SILVER_SENSOR_DIR = SILVER_DIR / "sensor_readings"

sensor_files = sorted(
    SILVER_SENSOR_DIR.glob("part_*.parquet")
)

print("Sensor Silver files:", len(sensor_files))


daily_parts = []


# ---------------------------------------------------------
# 1. Aggregate each Silver sensor file
# ---------------------------------------------------------

for file in sensor_files:

    sensor_df = pd.read_parquet(file)

    daily_part = (
        sensor_df
        .groupby(
            ["compressor_id", "reading_date"],
            as_index=False
        )
        .agg(
            reading_count=("reading_id", "count"),

            avg_tp3_bar=("TP3", "mean"),

            min_tp3_bar=("TP3", "min"),

            max_tp3_bar=("TP3", "max"),

            avg_oil_temperature_c=(
                "Oil_temperature",
                "mean"
            ),

            max_oil_temperature_c=(
                "Oil_temperature",
                "max"
            ),

            avg_motor_current_a=(
                "Motor_current",
                "mean"
            ),

            max_motor_current_a=(
                "Motor_current",
                "max"
            ),

            avg_dv_pressure_bar=(
                "DV_pressure",
                "mean"
            ),

            avg_reservoir_pressure_bar=(
                "Reservoirs",
                "mean"
            )
        )
    )

    daily_parts.append(daily_part)


# ---------------------------------------------------------
# 2. Combine partial daily aggregations
# ---------------------------------------------------------

daily_combined = pd.concat(
    daily_parts,
    ignore_index=True
)

print(
    "Intermediate daily rows:",
    len(daily_combined)
)





# ---------------------------------------------------------
# 3. Prepare weighted sums for correct final averages
# ---------------------------------------------------------

daily_combined["tp3_sum"] = (
    daily_combined["avg_tp3_bar"]
    * daily_combined["reading_count"]
)

daily_combined["oil_temp_sum"] = (
    daily_combined["avg_oil_temperature_c"]
    * daily_combined["reading_count"]
)

daily_combined["motor_current_sum"] = (
    daily_combined["avg_motor_current_a"]
    * daily_combined["reading_count"]
)

daily_combined["dv_pressure_sum"] = (
    daily_combined["avg_dv_pressure_bar"]
    * daily_combined["reading_count"]
)

daily_combined["reservoir_pressure_sum"] = (
    daily_combined["avg_reservoir_pressure_bar"]
    * daily_combined["reading_count"]
)


# ---------------------------------------------------------
# 4. Combine partial days
# ---------------------------------------------------------

compressor_daily_health = (
    daily_combined
    .groupby(
        ["compressor_id", "reading_date"],
        as_index=False
    )
    .agg(
        reading_count=("reading_count", "sum"),

        tp3_sum=("tp3_sum", "sum"),
        oil_temp_sum=("oil_temp_sum", "sum"),
        motor_current_sum=("motor_current_sum", "sum"),
        dv_pressure_sum=("dv_pressure_sum", "sum"),
        reservoir_pressure_sum=("reservoir_pressure_sum", "sum"),

        min_tp3_bar=("min_tp3_bar", "min"),
        max_tp3_bar=("max_tp3_bar", "max"),

        max_oil_temperature_c=(
            "max_oil_temperature_c",
            "max"
        ),

        max_motor_current_a=(
            "max_motor_current_a",
            "max"
        )
    )
)


# ---------------------------------------------------------
# 5. Recalculate final weighted averages
# ---------------------------------------------------------

compressor_daily_health["avg_tp3_bar"] = (
    compressor_daily_health["tp3_sum"]
    / compressor_daily_health["reading_count"]
)

compressor_daily_health["avg_oil_temperature_c"] = (
    compressor_daily_health["oil_temp_sum"]
    / compressor_daily_health["reading_count"]
)

compressor_daily_health["avg_motor_current_a"] = (
    compressor_daily_health["motor_current_sum"]
    / compressor_daily_health["reading_count"]
)

compressor_daily_health["avg_dv_pressure_bar"] = (
    compressor_daily_health["dv_pressure_sum"]
    / compressor_daily_health["reading_count"]
)

compressor_daily_health["avg_reservoir_pressure_bar"] = (
    compressor_daily_health["reservoir_pressure_sum"]
    / compressor_daily_health["reading_count"]
)


# ---------------------------------------------------------
# 6. Remove temporary calculation columns
# ---------------------------------------------------------

compressor_daily_health = compressor_daily_health.drop(
    columns=[
        "tp3_sum",
        "oil_temp_sum",
        "motor_current_sum",
        "dv_pressure_sum",
        "reservoir_pressure_sum"
    ]
)


print(
    "Final compressor-day rows:",
    len(compressor_daily_health)
)

print("\nDaily health preview:")
print(compressor_daily_health.head())


# ---------------------------------------------------------
# 7. Write Gold table
# ---------------------------------------------------------

output_file = (
    GOLD_DIR
    / "compressor_daily_health.parquet"
)

compressor_daily_health.to_parquet(
    output_file,
    engine="pyarrow",
    index=False
)

print("\nRows written:", len(compressor_daily_health))
print("Gold file:", output_file)




# =========================================================
# VALIDATE SENSOR DATE COVERAGE
# =========================================================

daily_kpis_df = pd.read_parquet(
    SILVER_DIR / "daily_operating_kpis.parquet"
)

kpi_dates = set(
    daily_kpis_df["timestamp"].dt.normalize()
)

sensor_dates = set(
    compressor_daily_health["reading_date"]
)

missing_sensor_dates = (
    kpi_dates - sensor_dates
)

print(
    "\nKPI dates without sensor readings:",
    sorted(missing_sensor_dates)
)