import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# DB Connection
conn = duckdb.connect("db/phonepe_data.duckdb")

# Page setup
st.set_page_config(page_title="PhonePe India Dashboard", layout="wide")
st.title("PhonePe India Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
years = conn.execute("SELECT DISTINCT year FROM aggregated_transactions ORDER BY year").fetchdf()['year'].tolist()
states = conn.execute("SELECT DISTINCT state FROM aggregated_transactions ORDER BY state").fetchdf()['state'].tolist()

selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
selected_state = st.sidebar.selectbox("Select State", states)

# Top States by Transaction Amount
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

# Transaction Types in Selected Year & State
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

# App opens trend
st.subheader("Quarterly App Opens Trend")
app_opens = conn.execute("""
    SELECT year, quarter, SUM(app_opens) AS total_opens
    FROM map_users
    GROUP BY year, quarter
    ORDER BY year, quarter;
""").fetchdf()
fig3 = px.line(app_opens, x=[f"Q{q} {y}" for y, q in zip(app_opens['year'], app_opens['quarter'])], y="total_opens", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# Top Districts by Transaction Volume
st.subheader("Top 10 Districts by Transaction Volume")
top_districts = conn.execute("""
    SELECT district, ROUND(SUM(amount)/10000000, 2) AS amount_cr, SUM(count) AS txn_count
    FROM map_transactions
    GROUP BY district
    ORDER BY amount_cr DESC
    LIMIT 10;
""").fetchdf()
fig4 = px.bar(top_districts, x="district", y="amount_cr", text="amount_cr", title="Top Districts by Transaction Volume")
st.plotly_chart(fig4, use_container_width=True)

# Monthly Transaction Trend for Selected State and Year
st.subheader(f"Monthly Transaction Trend in {selected_state} ({selected_year})")
monthly_trend = conn.execute(f"""
    SELECT quarter, SUM(amount) AS total_amount
    FROM aggregated_transactions
    WHERE state = '{selected_state}' AND year = {selected_year}
    GROUP BY quarter
    ORDER BY quarter;
""").fetchdf()
fig5 = px.line(monthly_trend, x="quarter", y="total_amount", markers=True, title="Quarterly Transaction Trend")
st.plotly_chart(fig5, use_container_width=True)

conn.close()
