import duckdb
from pathlib import Path
import pandas as pd

# Connect to DuckDB database
DB_PATH = Path("db/phonepe_data.duckdb")
conn = duckdb.connect(str(DB_PATH))

print("Connected to DuckDB")

# Define meaningful business insights
queries = {
    "States with Lowest App Open Rate": """
        SELECT 
            state, 
            year,
            SUM(registered_users) AS total_users, 
            SUM(app_opens) AS total_opens,
            ROUND(SUM(app_opens) * 100.0 / NULLIF(SUM(registered_users), 0), 2) AS open_rate_pct
        FROM aggregated_users
        GROUP BY state, year
        HAVING total_users > 1000
        ORDER BY open_rate_pct ASC
        LIMIT 10;
    """,

    "App Opens vs Transactions Efficiency (Example: Maharashtra)": """
        SELECT 
            mu.quarter,
            SUM(mu.app_opens) AS opens,
            SUM(mt.count) AS txns,
            ROUND(SUM(mt.count) * 1.0 / NULLIF(SUM(mu.app_opens), 0), 2) AS txn_per_open
        FROM map_users mu
        JOIN map_transactions mt 
          ON mu.state = mt.state AND mu.year = mt.year AND mu.quarter = mt.quarter
        WHERE mu.state = 'maharashtra'
        GROUP BY mu.quarter
        ORDER BY mu.quarter;
    """,

    "Top Growing States by Transaction Volume": """
        SELECT 
            state,
            MIN(year) AS start_year,
            MAX(year) AS end_year,
            ROUND((MAX(yearly_amount) - MIN(yearly_amount)) * 100.0 / NULLIF(MIN(yearly_amount), 0), 2) AS growth_pct
        FROM (
            SELECT state, year, SUM(amount) AS yearly_amount
            FROM aggregated_transactions
            GROUP BY state, year
        ) AS yearly_data
        GROUP BY state
        HAVING growth_pct IS NOT NULL
        ORDER BY growth_pct DESC
        LIMIT 10;
    """,

    "Quarterly Heatmap of Transactions by State": """
        SELECT 
            state, 
            CONCAT(year, '-Q', quarter) AS time_period,
            SUM(amount) AS total_txn_amount
        FROM aggregated_transactions
        GROUP BY state, year, quarter
        ORDER BY state, year, quarter;
    """
}

# Run and display results
for name, query in queries.items():
    print(f"\n{name}")
    df = conn.execute(query).fetchdf()
    print(df)

conn.close()
print("All queries executed.")
