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

# Year-on-Year Transaction Growth
st.subheader("Year-on-Year Growth in Transactions Per State")
growth_df = conn.execute("""
    SELECT 
        state, 
        year, 
        ROUND(SUM(amount)/10000000, 2) AS amount_cr
    FROM aggregated_transactions
    GROUP BY state, year
    ORDER BY state, year;
""").fetchdf()
fig_growth = px.line(growth_df[growth_df['state'] == selected_state], x="year", y="amount_cr", title=f"Transaction Growth in {selected_state}")
st.plotly_chart(fig_growth, use_container_width=True)

# Transaction Type Composition
st.subheader(f"Transaction Type Breakdown in {selected_state}")
txn_types = conn.execute(f"""
    SELECT 
        transaction_type,
        SUM(amount) AS total_amount
    FROM aggregated_transactions
    WHERE state = '{selected_state}'
    GROUP BY transaction_type
""").fetchdf()
fig_txn_type = px.pie(txn_types, names="transaction_type", values="total_amount", title="Transaction Composition")
st.plotly_chart(fig_txn_type, use_container_width=True)

# Merchant vs Peer-to-Peer Ratio
st.subheader("Merchant vs Peer-to-Peer Transaction Share")
merchant_vs_p2p = conn.execute("""
    SELECT 
        state,
        SUM(CASE WHEN transaction_type = 'Merchant payments' THEN amount ELSE 0 END) AS merchant_amt,
        SUM(CASE WHEN transaction_type = 'Peer-to-peer payments' THEN amount ELSE 0 END) AS p2p_amt,
        ROUND(SUM(CASE WHEN transaction_type = 'Merchant payments' THEN amount ELSE 0 END) * 100.0 / NULLIF(SUM(amount), 0), 2) AS merchant_ratio
    FROM aggregated_transactions
    GROUP BY state
    ORDER BY merchant_ratio ASC;
""").fetchdf()
fig_merchant = px.bar(merchant_vs_p2p.sort_values("merchant_ratio", ascending=False).head(10), x="state", y="merchant_ratio", title="Top 10 States by Merchant Payment Ratio")
st.plotly_chart(fig_merchant, use_container_width=True)

# App Opens vs Transactions
st.subheader("App Opens vs Transactions Efficiency")
txn_vs_open = conn.execute("""
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
""").fetchdf()
fig_efficiency = px.scatter(txn_vs_open, x="opens", y="txns", size="txn_per_open", color="state", title="Transactions vs App Opens")
st.plotly_chart(fig_efficiency, use_container_width=True)

# States with Low App Open Rates
st.subheader("States with Low App Opens Despite Large User Base")
low_opens = conn.execute("""
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
""").fetchdf()
fig_low_open = px.bar(low_opens, x="state", y="open_rate_pct", text="open_rate_pct", title="Low App Open Rate States")
st.plotly_chart(fig_low_open, use_container_width=True)

conn.close()
