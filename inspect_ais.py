import pandas as pd
import pyarrow.parquet as pq

FILE_PATH = "data/ais-2024-01-01.parquet"


print("=" * 60)
print("AIS DATASET INSPECTION")
print("=" * 60)


# --------------------------------------------------
# 1. Open Parquet file metadata
# --------------------------------------------------

print("\nReading file metadata...")

parquet_file = pq.ParquetFile(FILE_PATH)

print("Number of rows:", parquet_file.metadata.num_rows)
print("Number of columns:", parquet_file.metadata.num_columns)


# --------------------------------------------------
# 2. Show column names
# --------------------------------------------------

print("\n" + "=" * 60)
print("COLUMN NAMES")
print("=" * 60)

columns = parquet_file.schema_arrow.names

for i, column in enumerate(columns, start=1):
    print(f"{i}. {column}")


# --------------------------------------------------
# 3. Read only first 10 rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("FIRST 10 ROWS")
print("=" * 60)

df = pd.read_parquet(
    FILE_PATH,
    engine="pyarrow"
)

print(df.head(10).to_string())


# --------------------------------------------------
# 4. Data types
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)


# --------------------------------------------------
# 5. Dataset size
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nMemory usage:")
print(
    f"{df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB"
)


print("\nInspection complete.")