import json
from pathlib import Path
import pandas as pd

SOURCE_DIR = Path("data/raw/map/user/hover/country/india/state/")
OUTPUT_FILE = Path("data/processed/map_users.csv")

rows = []

print(f"🚀 Starting ETL for map/user")
print(f"📁 Looking inside: {SOURCE_DIR.resolve()}")

for state_dir in SOURCE_DIR.iterdir():
    if state_dir.is_dir():
        state = state_dir.name
        print(f"🔍 State: {state}")
        for year_dir in state_dir.iterdir():
            year = year_dir.name
            for json_file in year_dir.glob("*.json"):
                quarter = json_file.stem
                print(f"📂 File: {json_file}")
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    hover_data = data.get("data", {}).get("hoverData", {})
                    if not hover_data:
                        print(f"⚠️ No hoverData in {json_file}")
                    for district, metrics in hover_data.items():
                        rows.append({
                            "state": state,
                            "year": int(year),
                            "quarter": int(quarter),
                            "district": district,
                            "registered_users": metrics.get("registeredUsers", 0),
                            "app_opens": metrics.get("appOpens", 0),
                        })

                except Exception as e:
                    print(f"❌ Error in {json_file}: {e}")

# Write CSV
if rows:
    df = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Extracted {len(df)} rows to {OUTPUT_FILE}")
else:
    print("\n⚠️ No data was extracted.")
