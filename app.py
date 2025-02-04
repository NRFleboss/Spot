import streamlit as st
import pandas as pd
import plotly.express as px

# Function to check the password
def check_password():
    password = st.text_input("Enter password:", type="password")
    if password != st.secrets["auth"]["password"]:
        st.warning("Incorrect password. Try again.")
        st.stop()

# Call the password check before loading the app
check_password()

# App title
st.title("🎵 Spotify Playlist Data Analyzer")

# Sidebar: File Upload and Filters
st.sidebar.header("Upload Data and Filters")
uploaded_files = st.sidebar.file_uploader("Upload CSV Files", accept_multiple_files=True, type="csv")

@st.cache_data
def load_data(files):
    """Load and combine data from uploaded CSV files."""
    all_data = []
    for file in files:
        df = pd.read_csv(file)
        # Convert date_added to datetime (if available)
        if "date_added" in df.columns:
            df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        # Extract artist name from filename (assuming format "artist-....csv")
        df["artist"] = file.name.split("-")[0]
        all_data.append(df)
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Load the data if files are uploaded
if uploaded_files:
    df = load_data(uploaded_files)
    
    # Clean data: remove rows missing essential values
    df.dropna(subset=["listeners", "streams"], inplace=True)
    
    # Sidebar filter: Artist selection
    artists = sorted(df["artist"].unique())
    selected_artist = st.sidebar.selectbox("Filter by Artist", ["All"] + artists)
    if selected_artist != "All":
        df = df[df["artist"] == selected_artist]
    
    # Sidebar filter: Date Range selection (if date_added exists)
    if "date_added" in df.columns and not df["date_added"].isnull().all():
        min_date = df["date_added"].min().date()
        max_date = df["date_added"].max().date()
        selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date],
                                                 min_value=min_date, max_value=max_date)
        if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            df = df[(df["date_added"].dt.date >= start_date) & (df["date_added"].dt.date <= end_date)]
    
    # Optionally show the raw data
    if st.sidebar.checkbox("Show Raw Data"):
        st.write(df)
    
    # Display Overview Metrics
    st.subheader("Overview Metrics")
    total_streams = int(df["streams"].sum())
    total_listeners = int(df["listeners"].sum())
    col1, col2 = st.columns(2)
    col1.metric("Total Streams", f"{total_streams:,}")
    col2.metric("Total Listeners", f"{total_listeners:,}")
    
    # Main visualization options
    viz_option = st.selectbox("Choose a visualization", 
                              ["Top Playlists by Streams", 
                               "Top Playlists by Listeners", 
                               "Streams vs. Listeners", 
                               "Time Series Evolution"])
    
    if viz_option == "Top Playlists by Streams":
        # Select top 10 playlists by streams
        top_streams = df.nlargest(10, "streams")
        fig = px.bar(top_streams, 
                     x="streams", 
                     y="title", 
                     orientation="h",
                     title=f"Top 10 Playlists by Streams ({selected_artist})",
                     labels={"streams": "Streams", "title": "Playlist"})
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_option == "Top Playlists by Listeners":
        # Select top 10 playlists by listeners
        top_listeners = df.nlargest(10, "listeners")
        fig = px.bar(top_listeners, 
                     x="listeners", 
                     y="title", 
                     orientation="h",
                     title=f"Top 10 Playlists by Listeners ({selected_artist})",
                     labels={"listeners": "Listeners", "title": "Playlist"})
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_option == "Streams vs. Listeners":
        # Scatter plot: Streams vs. Listeners
        fig = px.scatter(df, 
                         x="listeners", 
                         y="streams", 
                         hover_data=["title", "artist"],
                         title=f"Streams vs. Listeners ({selected_artist})",
                         labels={"listeners": "Listeners", "streams": "Streams"})
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_option == "Time Series Evolution":
        # Line chart to display daily evolution of streams and listeners
        if "date_added" in df.columns:
            # Aggregate data by day
            daily_data = df.groupby(df["date_added"].dt.date).agg({
                "streams": "sum",
                "listeners": "sum"
            }).reset_index().rename(columns={"date_added": "date"})
            fig = px.line(daily_data, 
                          x="index",  # dates will be on x-axis
                          y=["streams", "listeners"],
                          title=f"Daily Evolution of Streams and Listeners ({selected_artist})",
                          labels={"value": "Count", "index": "Date", "variable": "Metric"})
            # Alternative: use the date column directly if preferred:
            # fig = px.line(daily_data, x="date", y=["streams", "listeners"], ...)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date information available for time series analysis.")
else:
    st.info("Please upload CSV files to begin.")
