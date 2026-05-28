import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ======================================================
# CONFIGURATION
# ======================================================
st.set_page_config(page_title="Staff Appraisal System", layout="wide")

# ======================================================
# CUSTOM CSS (Orange, Black, White Theme)
# ======================================================
st.markdown("""
<style>
    .main {
        background-color: white;
    }
    h1, h2, h3 {
        color: black;
    }
    .stApp {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# TITLE
# ======================================================
st.title("Staff Performance Appraisal Dashboard")

# ======================================================
# PATH TO REPORTS
# ======================================================
BASE_DIR = "reports"

# ======================================================
# GET MONTH FOLDERS
# ======================================================
month_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
selected_month = st.selectbox("Select Month", month_folders)

month_path = os.path.join(BASE_DIR, selected_month)

# ======================================================
# GET FILES IN MONTH
# ======================================================
files = [f for f in os.listdir(month_path) if f.endswith(".csv")]
selected_file = st.selectbox("Select Daily Report File", files)

file_path = os.path.join(month_path, selected_file)

# ======================================================
# LOAD DATA
# ======================================================
df = pd.read_csv(file_path)

# Normalize column names (safety)
df.columns = df.columns.str.strip()

# ======================================================
# PERFORMANCE CALCULATION
# ======================================================

df["Task1_Score"] = df["Was Task 1 completed?"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
df["Task2_Score"] = df["Was Task 2 completed?"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)

df["Daily_Score"] = (df["Task1_Score"] + df["Task2_Score"]) / 2 * 100

# ======================================================
# GROUP BY STAFF (MONTHLY VIEW)
# ======================================================
performance = df.groupby(["Name", "Department", "Designation"]).agg({
    "Task1_Score": "mean",
    "Task2_Score": "mean",
    "Daily_Score": "mean"
}).reset_index()

performance["Performance %"] = performance["Daily_Score"]

# ======================================================
# RANKING
# ======================================================
performance = performance.sort_values(by="Performance %", ascending=False)
performance["Rank"] = range(1, len(performance) + 1)

top_performers = performance.head(5)
low_performers = performance.tail(5)

# ======================================================
# DASHBOARD METRICS
# ======================================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Staff", len(performance))
col2.metric("Top Performer Score", round(performance["Performance %"].max(), 2))
col3.metric("Lowest Score", round(performance["Performance %"].min(), 2))

# ======================================================
# PIE CHART (Performance Distribution)
# ======================================================
st.subheader("Performance Distribution")

performance["Performance Band"] = pd.cut(
    performance["Performance %"],
    bins=[0, 50, 75, 100],
    labels=["Low", "Average", "High"]
)

pie_data = performance["Performance Band"].value_counts().reset_index()
pie_data.columns = ["Band", "Count"]

fig_pie = px.pie(
    pie_data,
    names="Band",
    values="Count",
    color_discrete_sequence=["black", "orange", "#ffcc99"]
)

st.plotly_chart(fig_pie, use_container_width=True)

# ======================================================
# BAR CHART (Ranking)
# ======================================================
st.subheader("Staff Performance Ranking")

fig_bar = px.bar(
    performance,
    x="Name",
    y="Performance %",
    color="Performance %",
    color_continuous_scale=["black", "orange", "white"],
    text="Performance %"
)

st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# TOP & LOW PERFORMERS
# ======================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Performers")
    st.dataframe(top_performers, use_container_width=True)

with col2:
    st.subheader("⚠️ Low Performers")
    st.dataframe(low_performers, use_container_width=True)

# ======================================================
# FULL TABLE
# ======================================================
st.subheader("Full Appraisal Table")
st.dataframe(performance, use_container_width=True)

# ======================================================
# CHALLENGES SUMMARY
# ======================================================
st.subheader("Daily Challenges Report")
st.dataframe(df[["Name", "Challenges faced during the day"]])
