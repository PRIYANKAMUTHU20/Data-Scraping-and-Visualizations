import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Movie Filter Dashboard", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    mydb = mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="2DnwFtxWENyGXLF.root",
        password="3er4ekP3FXgFptI3",
        database="imdb"
    )
    query = "SELECT * FROM movies;"
    df = pd.read_sql(query, mydb)
    mydb.close()
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce")
    df["Duration_min"] = pd.to_numeric(df["Duration_min"], errors="coerce")
    return df

df = load_data()

st.title("🎬 Interactive Movie Filtering")

# --- Duration Filter ---
st.sidebar.header("Filter Options")
duration_option = st.sidebar.selectbox(
    "Duration (Hrs)",
    ("All", "< 2 hrs", "2–3 hrs", "> 3 hrs")
)
if duration_option == "< 2 hrs":
    df = df[df["Duration_min"] < 120]
elif duration_option == "2–3 hrs":
    df = df[(df["Duration_min"] >= 120) & (df["Duration_min"] <= 180)]
elif duration_option == "> 3 hrs":
    df = df[df["Duration_min"] > 180]

# --- Ratings Filter ---
min_rating = st.sidebar.slider("Minimum IMDb Rating", 0.0, 10.0, 0.0, 0.1)
df = df[df["Rating"] >= min_rating]

# --- Voting Counts Filter ---
votes_max = df["Votes"].max()
if pd.isna(votes_max):
    votes_max = 100000  # or any reasonable default max value

min_votes = st.sidebar.number_input("Minimum Voting Counts", 0, int(votes_max), 0)
df = df[df["Votes"] >= min_votes]

# --- Genre Filter ---
genres = df["Genre"].unique().tolist()
selected_genres = st.sidebar.multiselect("Select Genres", genres, default=genres)
df = df[df["Genre"].isin(selected_genres)]

st.subheader("Filtered Movies")
st.dataframe(df[["Title", "Genre", "Duration_min", "Rating", "Votes"]], use_container_width=True)
st.write(f"Total movies after filtering: {len(df)}")