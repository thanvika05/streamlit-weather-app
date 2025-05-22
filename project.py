import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(layout="wide")
st.title("Real-Time Air Quality Monitoring Dashboard")

@st.cache_data
def load_data():
    # Try to read from local file first
    try:
        df = pd.read_csv("aqi_data.csv", parse_dates=["timestamp"])
    except FileNotFoundError:
        # If missing, show error and return empty DataFrame
        st.error("'aqi_data.csv' not found. Please upload or place the file in the project folder.")
        return pd.DataFrame()
    # Extract hour for heatmap
    df["hour"] = df["timestamp"].dt.hour
    return df

# Load the data
df = load_data()

# If load_data returned empty, allow upload
if df.empty:
    uploaded_file = st.file_uploader("Upload AQI CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
    else:
        st.stop()  # nothing to show until user uploads

# Sidebar Filters
regions = st.sidebar.multiselect("Select Regions", df["region"].unique(), default=df["region"].unique())
pollutants = st.sidebar.multiselect("Select Pollutants", df["pollutant"].unique(), default=df["pollutant"].unique())
filtered_df = df[df["region"].isin(regions) & df["pollutant"].isin(pollutants)]

# Line Plot: AQI over Time
st.subheader("AQI Over Time")
line_data = (
    filtered_df
    .groupby(["timestamp", "region"], as_index=False)["AQI"]
    .mean()
)
line_chart = alt.Chart(line_data).mark_line().encode(
    x='timestamp:T',
    y='AQI:Q',
    color='region:N',
    tooltip=['timestamp:T', 'region:N', 'AQI:Q']
).properties(width=800, height=400)
st.altair_chart(line_chart, use_container_width=True)

# Heatmap: Region vs Hour
st.subheader("Pollution Heatmap (Region vs Hour)")
heatmap_data = filtered_df.pivot_table(values='AQI', index='region', columns='hour', aggfunc='mean')
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(heatmap_data, cmap='coolwarm', annot=True, fmt=".1f", ax=ax)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Region")
st.pyplot(fig)

# Bar Plot: Top Pollutants
st.subheader(" Top Pollutants by Average AQI")
bar_data = (
    filtered_df
    .groupby("pollutant")["AQI"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
st.bar_chart(data=bar_data, x='pollutant', y='AQI')

# Footer
st.markdown("---")
st.markdown("Data source: `aqi_data.csv` / user upload")
