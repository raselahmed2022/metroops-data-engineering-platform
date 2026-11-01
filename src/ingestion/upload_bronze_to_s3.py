from pathlib import Path
import boto3


# =========================================================
# AWS CONFIGURATION
# =========================================================

AWS_PROFILE = "metroops-admin"
AWS_REGION = "eu-central-1"

BUCKET_NAME = "metroops-data-rasal-2026"

BRONZE_DIR = Path("data/bronze")


# =========================================================
# CREATE AWS SESSION
# =========================================================

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION
)

s3 = session.client("s3")


# =========================================================
# SMALL BRONZE TABLES
# =========================================================

small_tables = [
    "compressors",
    "facilities",
    "fault_events",
    "work_orders",
    "maintenance_events",
    "technicians",
    "spare_parts",
    "work_order_parts",
    "operating_targets",
    "daily_operating_kpis",
]


print("\n==========================================")
print("UPLOADING SMALL BRONZE TABLES TO S3")
print("==========================================")


uploaded_files = 0


for table in small_tables:

    local_file = BRONZE_DIR / f"{table}.parquet"

    s3_key = (
        f"bronze/{table}/{table}.parquet"
    )

    if not local_file.exists():
        print(f"SKIPPED - file not found: {local_file}")
        continue

    print(f"\nUploading: {local_file}")

    s3.upload_file(
        str(local_file),
        BUCKET_NAME,
        s3_key
    )

    uploaded_files += 1

    print(
        f"Uploaded to: "
        f"s3://{BUCKET_NAME}/{s3_key}"
    )


# =========================================================
# SENSOR READINGS
# =========================================================

print("\n==========================================")
print("UPLOADING SENSOR BRONZE FILES")
print("==========================================")


SENSOR_DIR = BRONZE_DIR / "sensor_readings"

sensor_files = sorted(
    SENSOR_DIR.glob("part_*.parquet")
)

print("Sensor files found:", len(sensor_files))


for local_file in sensor_files:

    s3_key = (
        f"bronze/sensor_readings/"
        f"{local_file.name}"
    )

    print(f"\nUploading: {local_file.name}")

    s3.upload_file(
        str(local_file),
        BUCKET_NAME,
        s3_key
    )

    uploaded_files += 1

    print(
        f"Uploaded to: "
        f"s3://{BUCKET_NAME}/{s3_key}"
    )


# =========================================================
# SUMMARY
# =========================================================

print("\n==========================================")
print("BRONZE S3 UPLOAD COMPLETE")
print("==========================================")

print("Small tables expected:", len(small_tables))
print("Sensor files found:", len(sensor_files))
print("Total files uploaded:", uploaded_files)

print(
    f"S3 location: "
    f"s3://{BUCKET_NAME}/bronze/"
)