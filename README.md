# PhonePe India Analytics Dashboard

This interactive dashboard visualizes transaction trends, user growth, and digital adoption across India using PhonePe Pulse data. Built with Streamlit, DuckDB, Plotly, and Pandas, this project offers a powerful yet lightweight analytics experience.

---

## Features

- Top States & Districts by transaction volume
- Filter by Year and State to explore regional insights
- Transaction Type Distribution (Recharge, P2P, Merchant, etc.)
- Quarterly App Opens Trend
- Quarterly Transaction Growth Visualization

---

## Project Structure

```
phonepe-analytics/
│
├── data/
│   ├── raw/                  # Raw JSON data
│   └── processed/            # Cleaned CSVs
│
├── etl/                     # Data extraction scripts
│
├── db/
│   └── phonepe_data.duckdb  # DuckDB database file
│
├── analysis/
│   └── queries.py           # Exploratory queries
│
├── dashboard/
│   └── app.py               # Streamlit dashboard
│
├── README.md
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/phonepe-analytics.git
cd phonepe-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Dashboard
```bash
streamlit run dashboard/app.py
```

---

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Visit: https://streamlit.io/cloud
3. Link your GitHub repo
4. Set the app entry point as:
```
dashboard/app.py
```
5. Click Deploy

---
# PhonePe India Analytics Dashboard
 [Live Demo on Streamlit](https://phonepeanalyticsbasic.streamlit.app/)


## Sample Insights

- Maharashtra consistently ranks #1 in transaction volume
- P2P payments dominate digital usage
- App opens peaked significantly in 2021–22

---

## Contact

For questions, contributions, or collaboration:
**Tanmay Srivastav**  
Email: [tanmayrajsrivastav2003@gmail.com ]  
LinkedIn: https://www.linkedin.com/in/tanmay-srivastav-766952251/

---

## Star the repo if you found it helpful!

---

**License**: MIT
