from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
BRONZE_DIR = Path("data/bronze")

BRONZE_DIR.mkdir(parents=True, exist_ok=True)

files = [
    "compressors.csv",
    "facilities.csv",
    "fault_events.csv",
    "work_orders.csv",
    "maintenance_events.csv",
    "technicians.csv",
    "spare_parts.csv",
    "work_order_parts.csv",
    "operating_targets.csv",
    "daily_operating_kpis.csv",
]

for file_name in files:

    file_path = RAW_DIR / file_name

    print(f"\nReading: {file_name}")

    # Read CSV
    df = pd.read_csv(file_path)

    # Add technical ingestion metadata
    df["_source_file"] = file_name
    df["_ingested_at"] = pd.Timestamp.now(tz="UTC")

    # Create output file name
    output_path = (
        BRONZE_DIR /
        f"{Path(file_name).stem}.parquet"
    )

    # Write as Parquet
    df.to_parquet(
        output_path,
        engine="pyarrow",
        index=False
    )

    print(f"Rows ingested: {len(df):,}")
    print(f"Written to: {output_path}")