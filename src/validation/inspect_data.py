from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/metro_company_dataset_csv")

file_path = RAW_DIR / "sensor_readings.csv"

df = pd.read_csv(
    file_path,
    nrows=10
)

print("Columns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df)

print("\nData types:")
print(df.dtypes)