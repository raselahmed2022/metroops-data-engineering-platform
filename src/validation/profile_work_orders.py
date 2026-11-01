from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")
FILE = RAW_DIR / "work_orders.csv"

df = pd.read_csv(FILE)

print("\n--- WORK ORDERS PROFILE ---")

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


# Convert timestamps for analysis
df["opened_at"] = pd.to_datetime(df["opened_at"])
df["closed_at"] = pd.to_datetime(df["closed_at"])

print("\nUnique work order IDs:")
print(df["work_order_id"].nunique())

print("\nTotal work orders:")
print(len(df))

print("\nMaintenance types:")
print(df["maintenance_type"].value_counts())

print("\nPriority:")
print(df["priority"].value_counts())

print("\nStatus:")
print(df["status"].value_counts())

print("\nTechnicians:")
print(df["technician_id"].value_counts())

print("\nWork orders by compressor:")
print(df["compressor_id"].value_counts())

print("\nWork orders with missing fault_id:")
print(df[df["fault_id"].isnull()][
    ["work_order_id", "maintenance_type", "priority", "status"]
])

print("\nLabor hour statistics:")
print(df["labor_hours"].describe())

print("\nExternal cost statistics:")
print(df["external_cost_eur"].describe())

df["work_order_duration_hours"] = (
    df["closed_at"] - df["opened_at"]
).dt.total_seconds() / 3600

print("\nWork order duration statistics:")
print(df["work_order_duration_hours"].describe())