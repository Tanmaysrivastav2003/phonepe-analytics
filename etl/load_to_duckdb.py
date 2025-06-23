# etl/load_to_duckdb.py
import duckdb
import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
DB_PATH = "db/phonepe_data.duckdb"
Path("db").mkdir(exist_ok=True)

# Connect to DuckDB
conn = duckdb.connect(DB_PATH)
print(f"🦆 Creating DuckDB at: {DB_PATH}")

tables = {
    "aggregated_transactions": "aggregated_transactions.csv",
    "aggregated_users": "aggregated_users.csv",
    "map_transactions": "map_transactions.csv",
    "map_users": "map_users.csv",
    "top_pincodes": "top_pincodes.csv",
    "top_districts": "top_districts.csv",
    "top_users": "top_users.csv"
}

for table, file in tables.items():
    path = PROCESSED_DIR / file
    if not path.exists():
        print(f"⚠️ {file} not found. Skipping.")
        continue

    print(f"📥 Loading {file} → {table}")
    df = pd.read_csv(path)
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.register("df_view", df)
    conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df_view")

print("✅ DuckDB loaded successfully!")
conn.close()
