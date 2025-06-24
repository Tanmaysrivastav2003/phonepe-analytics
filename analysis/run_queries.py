import duckdb
from pathlib import Path
import pandas as pd

# Connect to DuckDB database
DB_PATH = Path("db/phonepe_data.duckdb")
conn = duckdb.connect(str(DB_PATH))

print("✅ Connected to DuckDB")

# Define business-critical queries
queries = {
    "Low App Opens but High User Base": """
        SELECT 
            state, 
            year,
            SUM(registered_users) AS total_users, 
            SUM(app_opens) AS total_opens,
            ROUND(SUM(app_opens) * 100.0 / NULLIF(SUM(registered_users), 0), 2) AS open_rate_pct
        FROM aggregated_users
        GROUP BY state, year
        HAVING total_users > 10000
        ORDER BY open_rate_pct ASC
        LIMIT 10;
    """,

    "Year-on-Year Growth in Transactions Per State": """
        SELECT 
            state, 
            year, 
            ROUND(SUM(amount)/10000000, 2) AS amount_cr
        FROM aggregated_transactions
        GROUP BY state, year
        ORDER BY state, year;
    """,

    "Transaction Type Composition by State": """
        SELECT 
            state,
            transaction_type,
            SUM(amount) AS total_amount
        FROM aggregated_transactions
        GROUP BY state, transaction_type
        ORDER BY state, transaction_type;
    """,

    "App Opens vs Transactions Correlation": """
        SELECT 
            mu.state, 
            mu.year, 
            mu.quarter,
            SUM(mu.app_opens) AS opens,
            SUM(mt.count) AS txns,
            ROUND(SUM(mt.count) * 1.0 / NULLIF(SUM(mu.app_opens), 0), 2) AS txn_per_open
        FROM map_users mu
        JOIN map_transactions mt 
          ON mu.state = mt.state AND mu.year = mt.year AND mu.quarter = mt.quarter
        GROUP BY mu.state, mu.year, mu.quarter
        ORDER BY txn_per_open ASC;
    """,

    "Merchant vs P2P Ratio per State": """
        SELECT 
            state,
            SUM(CASE WHEN transaction_type = 'Merchant payments' THEN amount ELSE 0 END) AS merchant_amt,
            SUM(CASE WHEN transaction_type = 'Peer-to-peer payments' THEN amount ELSE 0 END) AS p2p_amt,
            ROUND(SUM(CASE WHEN transaction_type = 'Merchant payments' THEN amount ELSE 0 END) * 100.0 / NULLIF(SUM(amount), 0), 2) AS merchant_ratio
        FROM aggregated_transactions
        GROUP BY state
        ORDER BY merchant_ratio ASC;
    """
}

# Run and display results
for name, query in queries.items():
    print(f"\n🔎 {name}")
    df = conn.execute(query).fetchdf()
    print(df)

conn.close()
print("\n✅ All queries executed.")
