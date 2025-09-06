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
    df = pd.read_sql_query(query, mydb)
    mydb.close()

    # Convert column names to lowercase
    df.columns = df.columns.str.lower()

    # Convert numeric columns
    for col in ["rating", "votes", "duration_min"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure genre is string
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str)

    return df

df = load_data()

st.title("🎬 Interactive Movie Filtering")

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Duration filter
duration_option = st.sidebar.selectbox(
    "Duration (Hrs)",
    ("All", "< 2 hrs", "2–3 hrs", "> 3 hrs")
)

# Ratings filter
min_rating = st.sidebar.slider("IMDb Rating", 0.0, 10.0, 0.0, 0.1)

# Votes filter
votes_max = df["votes"].max() if "votes" in df.columns else 100000
min_votes = st.sidebar.number_input("Minimum Voting Counts", 0, int(votes_max), 0)

# Genre filter (starts empty)
genres = df["genre"].unique().tolist() if "genre" in df.columns else []
selected_genres = st.sidebar.multiselect("Select Genres", genres, default=[])

# --- Apply filters only if genre AND at least one other filter is applied ---
filters_applied = (min_rating > 0 or min_votes > 0 or duration_option != "All")

if selected_genres and filters_applied:
    filtered_df = df.copy()

    # --- Genre filter supporting multi-genre cells ---
    filtered_df = filtered_df[filtered_df["genre"].apply(
        lambda x: any(g.strip() in x.split(",") for g in selected_genres)
    )]

    # --- Duration filter ---
    if duration_option == "< 2 hrs":
        filtered_df = filtered_df[filtered_df["duration_min"] < 120]
    elif duration_option == "2–3 hrs":
        filtered_df = filtered_df[(filtered_df["duration_min"] >= 120) & (filtered_df["duration_min"] <= 180)]
    elif duration_option == "> 3 hrs":
        filtered_df = filtered_df[filtered_df["duration_min"] > 180]

    # --- Ratings filter (exact match) ---
    # For floats, you can use a small tolerance if needed
    tolerance = 0.1
    filtered_df = filtered_df[(filtered_df["rating"] >= min_rating) & (filtered_df["rating"] < min_rating + tolerance)]

    # --- Votes filter ---
    filtered_df = filtered_df[filtered_df["votes"] >= min_votes]

else:
    filtered_df = df.iloc[0:0]  # empty dataframe until both genre & filter applied

# --- Display filtered movies ---
st.subheader("Filtered Movies")
st.dataframe(filtered_df[["title", "genre", "duration_min", "rating", "votes"]], use_container_width=True)
st.write(f"Total movies after filtering: {len(filtered_df)}")
