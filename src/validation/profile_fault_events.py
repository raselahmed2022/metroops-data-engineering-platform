from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
FILE = RAW_DIR / "fault_events.csv"

df = pd.read_csv(FILE)

print("\n--- FAULT EVENTS PROFILE ---")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nNull values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

# Convert dates for analysis
df["fault_start"] = pd.to_datetime(df["fault_start"])
df["fault_end"] = pd.to_datetime(df["fault_end"])

print("\nUnique fault IDs:")
print(df["fault_id"].nunique())

print("\nTotal fault rows:")
print(len(df))

print("\nFaults by compressor:")
print(df["compressor_id"].value_counts())

print("\nFault types:")
print(df["fault_type"].value_counts())

print("\nSeverity:")
print(df["severity"].value_counts())

print("\nDetected by:")
print(df["detected_by"].value_counts())

print("\nFault status:")
print(df["fault_status"].value_counts())

print("\nEarliest fault:")
print(df["fault_start"].min())

print("\nLatest fault:")
print(df["fault_start"].max())

df["fault_duration_minutes"] = (
    df["fault_end"] - df["fault_start"]
).dt.total_seconds() / 60

print("\nFault duration statistics (minutes):")
print(df["fault_duration_minutes"].describe())