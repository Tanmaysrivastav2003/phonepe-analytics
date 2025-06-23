import os
import json
import pandas as pd
from pathlib import Path

# Path to the map/transaction data
SOURCE_DIR = Path("data/raw/map/transaction/hover/country/india/state/")
OUTPUT_FILE = Path("data/processed/map_transactions.csv")

rows = []

# Loop through states
for state_dir in SOURCE_DIR.iterdir():
    if state_dir.is_dir():
        state = state_dir.name
        # Loop through years (e.g., 2018 to 2024)
        for year_dir in state_dir.iterdir():
            year = year_dir.name
            # Loop through each quarter JSON file (e.g., 1.json, 2.json, etc.)
            for quarter_file in year_dir.glob("*.json"):
                quarter = quarter_file.stem
                try:
                    with open(quarter_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Extract hoverDataList (list of districts with metrics)
                    hover_list = data.get("data", {}).get("hoverDataList", [])

                    for entry in hover_list:
                        district = entry.get("name")
                        metric_list = entry.get("metric", [])

                        if metric_list and isinstance(metric_list, list):
                            metric = metric_list[0]  # Usually only one item
                            count = metric.get("count", 0)
                            amount = metric.get("amount", 0.0)

                            rows.append({
                                "state": state,
                                "year": int(year),
                                "quarter": int(quarter),
                                "district": district,
                                "count": count,
                                "amount": amount
                            })

                except Exception as e:
                    print(f"❌ Error reading {quarter_file}: {e}")

# Convert to DataFrame and save
df = pd.DataFrame(rows)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Map-level transactions extracted to: {OUTPUT_FILE}")
