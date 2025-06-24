import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Connect to DuckDB
conn = duckdb.connect("db/phonepe_data.duckdb")

# Streamlit page config
st.set_page_config(page_title="PhonePe Insights Dashboard", layout="wide")
st.title("PhonePe Analytics - Strategic Insights")

# Query 1: States with Lowest App Open Rate
st.header("1. States with Lowest App Open Rate")
low_open_df = conn.execute("""
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
""").fetchdf()
st.dataframe(low_open_df, use_container_width=True)
fig1 = px.bar(low_open_df, x='state', y='open_rate_pct', color='year', title="Lowest App Open Rates")
st.plotly_chart(fig1, use_container_width=True)

# Query 2: App Opens vs Transactions Efficiency for Maharashtra
st.header("2. Maharashtra: Transactions per App Open")
maha_df = conn.execute("""
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
""").fetchdf()
st.line_chart(maha_df.set_index("quarter")[["txn_per_open"]])

# Query 3: Top Growing States by Transaction Volume
st.header("3. Top Growing States by Transaction Volume")
growth_df = conn.execute("""
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
""").fetchdf()
st.dataframe(growth_df, use_container_width=True)
fig2 = px.bar(growth_df, x="state", y="growth_pct", title="Top States by Transaction Growth (%)")
st.plotly_chart(fig2, use_container_width=True)

# Query 4: Heatmap of Quarterly Transactions by State
st.header("4. Quarterly Heatmap of Transactions by State")
heatmap_df = conn.execute("""
    SELECT 
        state, 
        CONCAT(year, '-Q', quarter) AS time_period,
        SUM(amount) AS total_txn_amount
    FROM aggregated_transactions
    GROUP BY state, year, quarter
    ORDER BY state, year, quarter;
""").fetchdf()

pivot = heatmap_df.pivot(index='state', columns='time_period', values='total_txn_amount').fillna(0)
st.dataframe(pivot, use_container_width=True)
fig3 = px.imshow(pivot, labels=dict(color="Total Amount"),
                 aspect="auto", title="Heatmap of Quarterly Transactions")
st.plotly_chart(fig3, use_container_width=True)

conn.close()

