import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# DB Connection
conn = duckdb.connect("db/phonepe_data.duckdb")

# Page setup
st.set_page_config(page_title="PhonePe Analytics Dashboard", layout="wide")
st.title("PhonePe India Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
years = conn.execute("SELECT DISTINCT year FROM aggregated_transactions ORDER BY year").fetchdf()['year'].tolist()
states = conn.execute("SELECT DISTINCT state FROM aggregated_transactions ORDER BY state").fetchdf()['state'].tolist()

selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
selected_state = st.sidebar.selectbox("Select State", states)

# 1. Top 10 States by Transaction Amount
st.subheader("Top 10 States by Transaction Amount")
top_states = conn.execute("""
    SELECT state, ROUND(SUM(amount)/10000000, 2) AS amount_cr
    FROM aggregated_transactions
    GROUP BY state
    ORDER BY amount_cr DESC
    LIMIT 10;
""").fetchdf()
fig1 = px.bar(top_states, x="state", y="amount_cr", title="Top 10 States by Amount (Cr)", text="amount_cr")
st.plotly_chart(fig1, use_container_width=True)

# 2. Transaction Types for Selected Year & State
st.subheader(f"Transaction Types in {selected_year} - {selected_state}")
txn_by_type = conn.execute(f"""
    SELECT transaction_type, SUM(count) AS total_txns, ROUND(SUM(amount)/10000000, 2) AS amount_cr
    FROM aggregated_transactions
    WHERE year = {selected_year} AND state = '{selected_state}'
    GROUP BY transaction_type
    ORDER BY total_txns DESC;
""").fetchdf()
fig2 = px.bar(txn_by_type, x="transaction_type", y="total_txns", color="amount_cr", text="amount_cr", title="Transaction Types")
st.plotly_chart(fig2, use_container_width=True)

# 3. Quarterly App Opens Trend
st.subheader("Quarterly App Opens Trend")
app_opens = conn.execute("""
    SELECT year, quarter, SUM(app_opens) AS total_opens
    FROM map_users
    GROUP BY year, quarter
    ORDER BY year, quarter;
""").fetchdf()
fig3 = px.line(app_opens, x=[f"Q{q} {y}" for y, q in zip(app_opens['year'], app_opens['quarter'])], y="total_opens", markers=True, title="Quarterly App Opens")
st.plotly_chart(fig3, use_container_width=True)

# 4. Top Districts by Transaction Volume
st.subheader("Top Districts by Transaction Volume")
top_districts = conn.execute("""
    SELECT district, ROUND(SUM(amount)/10000000, 2) AS amount_cr, SUM(count) AS txn_count
    FROM map_transactions
    GROUP BY district
    ORDER BY amount_cr DESC
    LIMIT 10;
""").fetchdf()
fig4 = px.bar(top_districts, x="district", y="amount_cr", text="amount_cr", title="Top Districts by Transaction Volume")
st.plotly_chart(fig4, use_container_width=True)

# 5. Top 10 Pincodes by Transaction Volume
st.subheader("Top 10 Pincodes by Transaction Volume")
top_pincodes = conn.execute("""
    SELECT pincode, ROUND(SUM(amount)/10000000, 2) AS amount_cr, SUM(count) AS txn_count
    FROM top_pincodes
    WHERE pincode IS NOT NULL AND pincode != ''
    GROUP BY pincode
    ORDER BY amount_cr DESC
    LIMIT 10;
""").fetchdf()
fig5 = px.bar(top_pincodes, x="pincode", y="amount_cr", text="amount_cr", title="Top 10 Pincodes by Transaction Volume")
st.plotly_chart(fig5, use_container_width=True)

# 6. Recharge & Bill Payments Trend
st.subheader("Recharge & Bill Payments Trend")
recharge_trend = conn.execute("""
    SELECT year, quarter, SUM(count) AS total_txns
    FROM aggregated_transactions
    WHERE transaction_type = 'Recharge & bill payments'
    GROUP BY year, quarter
    ORDER BY year, quarter;
""").fetchdf()
fig6 = px.line(recharge_trend, x=[f"Q{q} {y}" for y, q in zip(recharge_trend['year'], recharge_trend['quarter'])], y="total_txns", markers=True, title="Recharge & Bill Payments Trend")
st.plotly_chart(fig6, use_container_width=True)

conn.close()
