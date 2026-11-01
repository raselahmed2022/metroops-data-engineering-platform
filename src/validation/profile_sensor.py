from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
FILE = RAW_DIR / "sensor_readings.csv"

CHUNK_SIZE = 100_000

total_rows = 0
compressors = set()
min_timestamp = None
max_timestamp = None
null_counts = None
seen_ids = set()
duplicate_ids = 0

for chunk in pd.read_csv(
    FILE,
    chunksize=CHUNK_SIZE,
    parse_dates=["timestamp"]
):

    # 1. Count rows
    total_rows += len(chunk)

    # 2. Find compressors
    compressors.update(chunk["compressor_id"].dropna().unique())

    # 3. Find time range
    chunk_min = chunk["timestamp"].min()
    chunk_max = chunk["timestamp"].max()

    if min_timestamp is None or chunk_min < min_timestamp:
        min_timestamp = chunk_min

    if max_timestamp is None or chunk_max > max_timestamp:
        max_timestamp = chunk_max

    # 4. Count null values
    if null_counts is None:
        null_counts = chunk.isnull().sum()
    else:
        null_counts += chunk.isnull().sum()

    # 5. Check whether reading_id is unique
    for reading_id in chunk["reading_id"]:
        if reading_id in seen_ids:
            duplicate_ids += 1
        else:
            seen_ids.add(reading_id)


print("\n--- SENSOR DATA PROFILE ---")

print("\nTotal rows:")
print(total_rows)

print("\nCompressors:")
print(compressors)

print("\nNumber of compressors:")
print(len(compressors))

print("\nEarliest timestamp:")
print(min_timestamp)

print("\nLatest timestamp:")
print(max_timestamp)

print("\nNull values:")
print(null_counts)

print("\nDuplicate reading IDs:")
print(duplicate_ids)