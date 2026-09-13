import pyarrow.parquet as pq
import pandas as pd
import geopandas as gpd
import os


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "data/ais-2024-01-01.parquet"
OUTPUT_FILE = "data/ais_processed_sample.csv"

SAMPLE_ROWS = 100000


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"File not found: {INPUT_FILE}"
    )


print("=" * 60)
print("AIS PREPROCESSING")
print("=" * 60)


# ============================================================
# READ SAMPLE
# ============================================================

print("\nReading first", SAMPLE_ROWS, "rows...")

parquet_file = pq.ParquetFile(INPUT_FILE)

batch = next(
    parquet_file.iter_batches(
        batch_size=SAMPLE_ROWS
    )
)

df = batch.to_pandas()

print("Rows loaded:", len(df))


# ============================================================
# CONVERT WKB → GEOMETRY
# ============================================================

print("\nConverting WKB geometry...")

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.GeoSeries.from_wkb(
        df["geometry"]
    )
)


# ============================================================
# EXTRACT COORDINATES
# ============================================================

print("Extracting latitude and longitude...")

gdf["longitude"] = gdf.geometry.x
gdf["latitude"] = gdf.geometry.y


# ============================================================
# SELECT USEFUL COLUMNS
# ============================================================

columns = [
    "mmsi",
    "base_date_time",
    "sog",
    "cog",
    "heading",
    "vessel_name",
    "imo",
    "call_sign",
    "vessel_type",
    "status",
    "length",
    "width",
    "draft",
    "cargo",
    "transceiver",
    "latitude",
    "longitude"
]

gdf = gdf[columns]


# ============================================================
# REMOVE INVALID POSITIONS
# ============================================================

print("\nRemoving invalid positions...")

gdf = gdf.dropna(
    subset=[
        "mmsi",
        "base_date_time",
        "latitude",
        "longitude"
    ]
)


# ============================================================
# SORT BY VESSEL AND TIME
# ============================================================

print("Sorting by vessel and timestamp...")

gdf = gdf.sort_values(
    ["mmsi", "base_date_time"]
)


# ============================================================
# SAVE
# ============================================================

gdf.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)

print("Final rows:", len(gdf))
print("Final columns:", len(gdf.columns))

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nProcessed sample:")

print(
    gdf.head(10).to_string(index=False)
)