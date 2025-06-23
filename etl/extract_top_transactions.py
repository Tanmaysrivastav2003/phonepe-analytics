import os
import json
import pandas as pd
from pathlib import Path

# Define paths
SOURCE_DIR = Path("data/raw/top/transaction/country/india/state/")
DISTRICT_CSV = Path("data/processed/top_districts.csv")
PINCODE_CSV = Path("data/processed/top_pincodes.csv")

district_rows = []
pincode_rows = []

for state_dir in SOURCE_DIR.iterdir():
    if state_dir.is_dir():
        state = state_dir.name
        for year_dir in state_dir.iterdir():
            year = year_dir.name
            for quarter_file in year_dir.glob("*.json"):
                quarter = quarter_file.stem
                try:
                    with open(quarter_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    districts = data.get("data", {}).get("districts", [])
                    pincodes = data.get("data", {}).get("pincodes", [])

                    for district in districts:
                        name = district.get("entityName")
                        metric = district.get("metric", {})
                        district_rows.append({
                            "state": state,
                            "year": int(year),
                            "quarter": int(quarter),
                            "district": name,
                            "count": metric.get("count", 0),
                            "amount": metric.get("amount", 0.0)
                        })

                    for pincode in pincodes:
                        code = pincode.get("entityName")
                        metric = pincode.get("metric", {})
                        pincode_rows.append({
                            "state": state,
                            "year": int(year),
                            "quarter": int(quarter),
                            "pincode": code,
                            "count": metric.get("count", 0),
                            "amount": metric.get("amount", 0.0)
                        })

                except Exception as e:
                    print(f"❌ Error reading {quarter_file}: {e}")

# Save district and pincode CSVs
pd.DataFrame(district_rows).to_csv(DISTRICT_CSV, index=False)
pd.DataFrame(pincode_rows).to_csv(PINCODE_CSV, index=False)

print(f"✅ Top districts saved to: {DISTRICT_CSV}")
print(f"✅ Top pincodes saved to: {PINCODE_CSV}")
