import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Connect to DuckDB database
conn = duckdb.connect("db/phonepe_data.duckdb")

st.set_page_config(page_title="PhonePe Business Insights Dashboard", layout="wide")
st.title("PhonePe Business Analytics")

# Query 1: States with Lowest App Engagement Rate
st.header("States with Lowest App Engagement Rate")
df1 = conn.execute("""
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
fig1 = px.bar(df1, x="state", y="open_rate_pct", color="year", title="Lowest App Open Rates by State")
st.plotly_chart(fig1, use_container_width=True)

# Query 2: Transactions per App Open (Maharashtra)
st.header("Transactions per App Open (Maharashtra)")
df2 = conn.execute("""
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
fig2 = px.line(df2, x="quarter", y="txn_per_open", markers=True, title="Transaction Efficiency per App Open in Maharashtra")
st.plotly_chart(fig2, use_container_width=True)

# Query 3: Top States by Transaction Growth
st.header("Top States by Transaction Growth")
df3 = conn.execute("""
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
fig3 = px.bar(df3, x="state", y="growth_pct", title="Top States by Transaction Growth (%)")
st.plotly_chart(fig3, use_container_width=True)

# Query 4: Quarterly Transaction Volume by State
st.header("Quarterly Transaction Volume by State")
df4 = conn.execute("""
    SELECT 
        state, 
        CONCAT(year, '-Q', quarter) AS time_period,
        SUM(amount) AS total_txn_amount
    FROM aggregated_transactions
    GROUP BY state, year, quarter
    ORDER BY state, year, quarter;
""").fetchdf()
fig4 = px.density_heatmap(df4, x="time_period", y="state", z="total_txn_amount",
                          title="Heatmap of Transaction Volume by State and Quarter",
                          nbinsx=30, color_continuous_scale="Viridis")
st.plotly_chart(fig4, use_container_width=True)

conn.close()
