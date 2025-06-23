import os
import json
import pandas as pd
from pathlib import Path

SOURCE_DIR = Path("data/raw/top/user/country/india/")
OUTPUT_FILE = Path("data/processed/top_users.csv")

rows = []

# Iterate year folders: 2018, 2019, ...
for year_dir in SOURCE_DIR.iterdir():
    if year_dir.is_dir():
        year = year_dir.name

        # Iterate JSON files: 1.json, 2.json, etc.
        for json_file in year_dir.glob("*.json"):
            quarter = json_file.stem
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Extract top pincodes (if available)
                top_users = data.get("data", {}).get("pincodes", [])

                for item in top_users:
                    pincode = item.get("entityName")
                    metric = item.get("metric", {})
                    rows.append({
                        "year": int(year),
                        "quarter": int(quarter),
                        "pincode": pincode,
                        "registered_users": metric.get("registeredUsers", 0)
                    })

            except Exception as e:
                print(f"❌ Error reading {json_file}: {e}")

df = pd.DataFrame(rows)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Top users extracted to: {OUTPUT_FILE}")
