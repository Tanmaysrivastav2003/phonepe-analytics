import duckdb
from pathlib import Path
import pandas as pd

# Connect to DuckDB database
DB_PATH = Path("db/phonepe_data.duckdb")
conn = duckdb.connect(str(DB_PATH))

print("Connected to DuckDB")

# Define updated queries
queries = {
    "Top 10 States by Transaction Amount": """
        SELECT 
            state, 
            ROUND(SUM(amount)/10000000, 2) AS amount_cr
        FROM aggregated_transactions
        GROUP BY state
        ORDER BY amount_cr DESC
        LIMIT 10;
    """,

    "Transaction Types in 2024 for Andaman & Nicobar": """
        SELECT 
            transaction_type, 
            SUM(count) AS total_txns, 
            ROUND(SUM(amount)/10000000, 2) AS amount_cr
        FROM aggregated_transactions
        WHERE year = 2024 AND state = 'andaman-&-nicobar-islands'
        GROUP BY transaction_type
        ORDER BY total_txns DESC;
    """,

    "Quarterly App Opens Trend": """
        SELECT 
            year, 
            quarter, 
            SUM(app_opens) AS total_opens
        FROM map_users
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """,

    "Top 10 Districts by Transaction Volume": """
        SELECT 
            district, 
            ROUND(SUM(amount)/10000000, 2) AS amount_cr, 
            SUM(count) AS txn_count
        FROM map_transactions
        GROUP BY district
        ORDER BY amount_cr DESC
        LIMIT 10;
    """,

    "Top 10 Pincodes by Transaction Volume": """
                SELECT 
            pincode, 
            ROUND(SUM(amount)/10000000, 2) AS amount_cr,
            SUM(count) AS txn_count
            FROM top_pincodes
            WHERE TRY_CAST(pincode AS BIGINT) IS NOT NULL
            GROUP BY pincode
            ORDER BY amount_cr DESC
            LIMIT 10;

    """,

    "Recharge & Bill Payments Trend": """
        SELECT 
            year, 
            quarter, 
            SUM(count) AS total_txns
        FROM aggregated_transactions
        WHERE transaction_type = 'Recharge & bill payments'
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """
}

# Run and display results
for name, query in queries.items():
    print(f"\n{name}")
    df = conn.execute(query).fetchdf()
    print(df)

conn.close()
print("\nAll queries executed.")