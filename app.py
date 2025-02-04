import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Title
st.title("🎵 Spotify Playlist Data Analyzer")

# Password Protection
def check_password():
    password = st.text_input("Enter password:", type="password")
    if password != st.secrets["auth"]["password"]:
        st.warning("Incorrect password. Try again.")
        st.stop()

check_password()

# File Upload
uploaded_files = st.file_uploader("Upload CSV Files", accept_multiple_files=True, type="csv")

if uploaded_files:
    # Read and merge all uploaded CSV files
    all_data = []
    for file in uploaded_files:
        df = pd.read_csv(file)
        df["artist"] = file.name.split("-")[0]  # Extract artist name from filename
        all_data.append(df)

    merged_df = pd.concat(all_data, ignore_index=True)

    # Remove missing values
    merged_df.dropna(subset=["listeners", "streams"], inplace=True)

    # Show raw data
    if st.checkbox("Show Raw Data"):
        st.write(merged_df)

    # Select artist
    artists = merged_df["artist"].unique().tolist()
    selected_artist = st.selectbox("Filter by Artist", ["All"] + artists)

    if selected_artist != "All":
        merged_df = merged_df[merged_df["artist"] == selected_artist]

    # Select visualization type
    option = st.selectbox("Choose a visualization", 
                          ["Top Playlists by Streams", "Top Playlists by Listeners", "Streams vs. Listeners"])

    if option == "Top Playlists by Streams":
        top_streams = merged_df.nlargest(10, "streams")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(y=top_streams["title"], x=top_streams["streams"], palette="Blues_r", ax=ax)
        ax.set_xlabel("Streams")
        ax.set_ylabel("Playlist")
        ax.set_title(f"Top 10 Playlists by Streams ({selected_artist})")
        st.pyplot(fig)

    elif option == "Top Playlists by Listeners":
        top_listeners = merged_df.nlargest(10, "listeners")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(y=top_listeners["title"], x=top_listeners["listeners"], palette="Greens_r", ax=ax)
        ax.set_xlabel("Listeners")
        ax.set_ylabel("Playlist")
        ax.set_title(f"Top 10 Playlists by Listeners ({selected_artist})")
        st.pyplot(fig)

    elif option == "Streams vs. Listeners":
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(x=merged_df["listeners"], y=merged_df["streams"], alpha=0.7, ax=ax)
        ax.set_xlabel("Listeners")
        ax.set_ylabel("Streams")
        ax.set_title(f"Streams vs. Listeners ({selected_artist})")
        st.pyplot(fig)
