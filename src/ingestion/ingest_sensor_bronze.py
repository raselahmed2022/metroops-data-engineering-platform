from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
BRONZE_DIR = Path("data/bronze/sensor_readings")

SOURCE_FILE = RAW_DIR / "sensor_readings.csv"

CHUNK_SIZE = 100_000

BRONZE_DIR.mkdir(parents=True, exist_ok=True)

total_rows = 0

for chunk_number, chunk in enumerate(
    pd.read_csv(
        SOURCE_FILE,
        chunksize=CHUNK_SIZE
    )
):

    # Add ingestion metadata
    chunk["_source_file"] = "sensor_readings.csv"
    chunk["_ingested_at"] = pd.Timestamp.now(tz="UTC")

    output_file = (
        BRONZE_DIR /
        f"part_{chunk_number:03d}.parquet"
    )

    chunk.to_parquet(
        output_file,
        engine="pyarrow",
        index=False
    )

    total_rows += len(chunk)

    print(
        f"Chunk {chunk_number:03d} | "
        f"{len(chunk):,} rows | "
        f"Written to {output_file}"
    )

print("\n--- SENSOR INGESTION COMPLETE ---")
print(f"Total rows ingested: {total_rows:,}")