from pathlib import Path
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BRONZE_SENSOR_DIR = Path("data/bronze/sensor_readings")
SILVER_SENSOR_DIR = Path("data/silver/sensor_readings")

SILVER_SENSOR_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# SENSOR COLUMNS
# =========================================================

numeric_sensor_columns = [
    "TP2",
    "TP3",
    "H1",
    "DV_pressure",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current",
    "COMP",
    "DV_eletric",
    "Towers",
    "MPG",
    "LPS",
    "Pressure_switch",
    "Oil_level",
    "Caudal_impulses",
]


# =========================================================
# CLEAN OLD SILVER PART FILES
# =========================================================

for old_file in SILVER_SENSOR_DIR.glob("part_*.parquet"):
    old_file.unlink()


# =========================================================
# GET BRONZE FILES
# =========================================================

bronze_files = sorted(
    BRONZE_SENSOR_DIR.glob("part_*.parquet")
)

print("Bronze sensor files found:", len(bronze_files))


total_rows_read = 0
total_rows_written = 0
total_missing_required = 0
total_missing_sensor_values = 0


# =========================================================
# TRANSFORM EACH PARQUET PART
# =========================================================

for index, input_file in enumerate(bronze_files):

    print(f"\nProcessing: {input_file.name}")

    sensor = pd.read_parquet(input_file)

    rows_read = len(sensor)
    total_rows_read += rows_read

    print("Rows read:", rows_read)


    # -----------------------------------------------------
    # 1. Standardize timestamp
    # -----------------------------------------------------

    sensor["timestamp"] = pd.to_datetime(
        sensor["timestamp"],
        errors="coerce"
    )


    # -----------------------------------------------------
    # 2. Clean compressor ID
    # -----------------------------------------------------

    sensor["compressor_id"] = (
        sensor["compressor_id"]
        .astype("string")
        .str.strip()
    )


    # -----------------------------------------------------
    # 3. Enforce numeric sensor columns
    # -----------------------------------------------------

    for column in numeric_sensor_columns:

        sensor[column] = pd.to_numeric(
            sensor[column],
            errors="coerce"
        )


    # -----------------------------------------------------
    # 4. Check required fields
    # -----------------------------------------------------

    missing_required = sensor[
        sensor[
            [
                "reading_id",
                "compressor_id",
                "timestamp"
            ]
        ].isna().any(axis=1)
    ]

    print(
        "Rows missing required fields:",
        len(missing_required)
    )

    total_missing_required += len(missing_required)


    # -----------------------------------------------------
    # 5. Remove rows missing required identifiers
    # -----------------------------------------------------

    sensor = sensor.dropna(
        subset=[
            "reading_id",
            "compressor_id",
            "timestamp"
        ]
    )


    # -----------------------------------------------------
    # 6. Remove duplicate reading IDs inside this part
    # -----------------------------------------------------

    duplicate_readings = sensor.duplicated(
        subset=["reading_id"]
    ).sum()

    print(
        "Duplicate reading IDs in part:",
        duplicate_readings
    )

    sensor = sensor.drop_duplicates(
        subset=["reading_id"],
        keep="first"
    )


    # -----------------------------------------------------
    # 7. Check missing sensor measurements
    # -----------------------------------------------------

    missing_sensor_values = sensor[
        sensor[numeric_sensor_columns]
        .isna()
        .any(axis=1)
    ]

    print(
        "Rows with missing sensor values:",
        len(missing_sensor_values)
    )

    total_missing_sensor_values += len(
        missing_sensor_values
    )


    # -----------------------------------------------------
    # 8. Add useful date field
    # -----------------------------------------------------

    sensor["reading_date"] = (
        sensor["timestamp"]
        .dt.normalize()
    )


    # -----------------------------------------------------
    # 9. Write Silver part
    # -----------------------------------------------------

    output_file = (
        SILVER_SENSOR_DIR
        / f"part_{index:03d}.parquet"
    )

    sensor.to_parquet(
        output_file,
        engine="pyarrow",
        index=False
    )

    rows_written = len(sensor)

    total_rows_written += rows_written

    print("Rows written:", rows_written)


# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n==========================================")
print("SENSOR SILVER TRANSFORMATION COMPLETE")
print("==========================================")

print("Files processed:", len(bronze_files))
print("Total rows read:", total_rows_read)
print("Total rows written:", total_rows_written)
print(
    "Rows missing required fields:",
    total_missing_required
)
print(
    "Rows with missing sensor values:",
    total_missing_sensor_values
)

print(
    "Silver directory:",
    SILVER_SENSOR_DIR
)