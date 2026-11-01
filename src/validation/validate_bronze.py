from pathlib import Path
import pandas as pd

BRONZE_DIR = Path("data/bronze/sensor_readings")

EXPECTED_ROWS = 1_516_948

parquet_files = list(BRONZE_DIR.glob("*.parquet"))

total_bronze_rows = 0

for file in parquet_files:
    df = pd.read_parquet(file)
    total_bronze_rows += len(df)

print("Parquet files:", len(parquet_files))
print("Bronze rows:", total_bronze_rows)
print("Expected source rows:", EXPECTED_ROWS)

if total_bronze_rows == EXPECTED_ROWS:
    print("VALIDATION PASSED")
else:
    print("VALIDATION FAILED")