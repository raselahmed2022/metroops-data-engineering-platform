from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
FILE = RAW_DIR / "maintenance_events.csv"

df = pd.read_csv(FILE)

print("\n--- MAINTENANCE EVENTS PROFILE ---")

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

print("\nUnique maintenance IDs:")
print(df["maintenance_id"].nunique())

print("\nUnique work order IDs:")
print(df["work_order_id"].nunique())

print("\nMaintenance types:")
print(df["maintenance_type"].value_counts())

print("\nMaintenance cost statistics:")
print(df["maintenance_cost_eur"].describe())

print("\nDowntime statistics:")
print(df["downtime_minutes"].describe())

print("\nTechnicians:")
print(df["technician_id"].value_counts())