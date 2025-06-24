import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# DB Connection
conn = duckdb.connect("db/phonepe_data.duckdb")

# Page setup
st.set_page_config(page_title="PhonePe Data Dashboard", layout="wide")
st.title("PhonePe India Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
years = conn.execute("SELECT DISTINCT year FROM aggregated_transactions ORDER BY year").fetchdf()['year'].tolist()
states = conn.execute("SELECT DISTINCT state FROM aggregated_transactions ORDER BY state").fetchdf()['state'].tolist()

selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
selected_state = st.sidebar.selectbox("Select State", states)

# Section: States with Low App Opens Despite Large User Base
st.subheader("States with Low App Opens Despite Large User Base")
low_opens_query = """
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
"""
low_opens_df = conn.execute(low_opens_query).fetchdf()
if not low_opens_df.empty:
    fig_low_opens = px.bar(low_opens_df, x="state", y="open_rate_pct", color="year", title="Lowest App Open Rate by State")
    st.plotly_chart(fig_low_opens, use_container_width=True)
else:
    st.info("No data available for Low App Opens analysis.")

# Section: App Opens vs Transactions Efficiency (State-wise Dropdown)
st.subheader("App Opens vs Transactions Efficiency")
st_efficiency = st.selectbox("Select State for Efficiency Analysis", states)
efficiency_query = f"""
    SELECT 
        mu.quarter,
        SUM(mu.app_opens) AS opens,
        SUM(mt.count) AS txns,
        ROUND(SUM(mt.count) * 1.0 / NULLIF(SUM(mu.app_opens), 0), 2) AS txn_per_open
    FROM map_users mu
    JOIN map_transactions mt 
      ON mu.state = mt.state AND mu.year = mt.year AND mu.quarter = mt.quarter
    WHERE mu.state = '{st_efficiency}'
    GROUP BY mu.quarter
    ORDER BY mu.quarter;
"""
txn_vs_open = conn.execute(efficiency_query).fetchdf()
if not txn_vs_open.empty:
    fig_efficiency = px.line(txn_vs_open, x="quarter", y="txn_per_open", markers=True,
                              title=f"Quarterly Transactions per App Open in {st_efficiency}")
    st.plotly_chart(fig_efficiency, use_container_width=True)
else:
    st.warning(f"No data found for {st_efficiency}.")

conn.close()
