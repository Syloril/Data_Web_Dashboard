import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px

# PAGE CONFIG
st.set_page_config(page_title="Kiva Lender Insights", layout="wide")

# MONGODB CONNECTION
@st.cache_resource
def get_db():
    client = MongoClient('mongodb://localhost:27017/')
    return client['kiva_loans_db']

db = get_db()

# LOAD DATA FROM MONGODB
@st.cache_data
def load_data():
    cursor = db.loans.find({}, {
        "SECTOR_NAME": 1, 
        "COUNTRY_NAME": 1, 
        "LOAN_AMOUNT": 1, 
        "ACTIVITY_NAME": 1, 
        "DESCRIPTION": 1
    })
    return pd.DataFrame(list(cursor))

df = load_data()

# SIDEBAR FILTERS
st.sidebar.header("🔍 Search & Filter")

# Keyword Search
search_query = st.sidebar.text_input("Search Loan Descriptions", placeholder="e.g. organic, school, water")

# Sector Filter
all_sectors = ["All"] + sorted(df["SECTOR_NAME"].unique().tolist())
selected_sector = st.sidebar.selectbox("Select a Sector", all_sectors)

# FILTER
filtered_df = df.copy()

# Apply Sector Filter
if selected_sector != "All":
    filtered_df = filtered_df[filtered_df["SECTOR_NAME"] == selected_sector]

# Apply Keyword Search (Case-insensitive)
if search_query:
    # We use .str.contains and fillna to avoid errors on empty descriptions
    filtered_df = filtered_df[filtered_df['DESCRIPTION'].str.contains(search_query, case=False, na=False)]

# DASHBOARD
st.title("🌍 Kiva Lender Opportunity Dashboard")
if search_query:
    st.write(f"Showing results for: **'{search_query}'**")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Matches Found", len(filtered_df))
col2.metric("Total Value", f"${filtered_df['LOAN_AMOUNT'].sum():,.2f}")
col3.metric("Avg. Loan", f"${filtered_df['LOAN_AMOUNT'].mean():,.2f}" if len(filtered_df) > 0 else "$0")

st.divider()

# Visualization Row
left_col, right_col = st.columns(2)

if not filtered_df.empty:
    with left_col:
        st.subheader("Global Distribution")
        fig_map = px.choropleth(filtered_df, 
                                locations="COUNTRY_NAME", 
                                locationmode='country names',
                                color="LOAN_AMOUNT",
                                color_continuous_scale="Viridis",
                                template="plotly_white")
        st.plotly_chart(fig_map, use_container_width=True)

    with right_col:
        st.subheader("Top Activities in this Category")
        activity_counts = filtered_df["ACTIVITY_NAME"].value_counts().head(10)
        fig_bar = px.bar(activity_counts, 
                         orientation='h',
                         labels={'value': 'Count', 'index': 'Activity'},
                         color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig_bar, use_container_width=True)

    # Search-Specific Insight
    st.subheader("Recent Loan Descriptions")
    st.table(filtered_df[['COUNTRY_NAME', 'LOAN_AMOUNT', 'DESCRIPTION']].head(5))
else:
    st.warning("No loans found matching those keywords. Try something else!")

# Data Table
with st.expander("View All Filtered Data"):
    st.dataframe(filtered_df.drop(columns=['_id']), use_container_width=True)