import os
import json
import pandas as pd
from pathlib import Path

print("🚀 Starting PhonePe aggregated transaction ETL...")

# Set paths
RAW_DATA_PATH = Path("data/raw/aggregated/transaction/country/india/state").resolve()
OUTPUT_PATH = Path("data/processed/aggregated_transactions.csv").resolve()

print(f"📂 Looking for JSON files in: {RAW_DATA_PATH}")
print(f"📄 Will save output to: {OUTPUT_PATH}")

# Check if data exists
if not RAW_DATA_PATH.exists():
    print("❌ ERROR: Data folder not found.")
    exit()

# Store extracted rows
rows = []

# Walk through folders
for state_dir in RAW_DATA_PATH.iterdir():
    if state_dir.is_dir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = year_dir.name
            for quarter_file in year_dir.glob("*.json"):
                quarter = quarter_file.stem  # e.g., '1' for Q1
                try:
                    with open(quarter_file, 'r') as f:
                        data = json.load(f)
                        txns = data.get("data", {}).get("transactionData", [])
                        for entry in txns:
                            tx_type = entry["name"]
                            for instrument in entry.get("paymentInstruments", []):
                                rows.append({
                                    "state": state,
                                    "year": int(year),
                                    "quarter": int(quarter),
                                    "transaction_type": tx_type,
                                    "count": instrument.get("count", 0),
                                    "amount": instrument.get("amount", 0)
                                })
                except Exception as e:
                    print(f"⚠️ Skipped {quarter_file} due to error: {e}")

# Convert to CSV
if rows:
    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Extracted {len(df)} rows to {OUTPUT_PATH}")
else:
    print("❌ No data extracted. Check your paths and JSON files.")
