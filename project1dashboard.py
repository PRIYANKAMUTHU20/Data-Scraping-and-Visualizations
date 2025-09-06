import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import mysql.connector
# ---------- Page Config ----------
st.set_page_config(page_title="Movie Dashboard", page_icon="🎬", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6 {
    font-family: 'Arial Black', Gadget, sans-serif;
    font-weight: 900;
    color: #FF4B4B;
}
.stMetricDelta, .stMetricValue {
    font-weight: 900 !important;
    font-size: 24px !important;
    color: #1F77B4;
}
.css-1d391kg {
    font-family: 'Verdana', sans-serif;
    font-weight: bold;
    font-size: 14px;
}
.stSlider label, .stNumberInput label {
    font-weight: bold;
    font-size: 16px;
    color: #FF5733;
}
</style>
""", unsafe_allow_html=True)

# Load Data from TiDB
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

    # Rename lowercase → TitleCase for consistency with Streamlit code
    df.rename(columns={
        "title": "Title",
        "rating": "Rating",
        "votes": "Votes",
        "duration": "Duration",
        "duration_min": "Duration_min",
        "genre": "Genre"
    }, inplace=True)

    # Ensure numeric conversion
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce")
    df["Duration_min"] = pd.to_numeric(df["Duration_min"], errors="coerce")

    return df

# Load once
df = load_data()

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.title("🎬 Movie Data Analysis & Visualization")

# ---------- 1. Top 10 Movies ----------
st.markdown("### 🎥 Top 10 Movies by Rating")
rating_top10 = df.sort_values(by="Rating", ascending=False).head(10)
st.dataframe(rating_top10[["Title", "Rating", "Votes", "Genre"]])
st.markdown("### 🎥 Top 10 Movies by Voting Counts")
votes_top10 = df.sort_values(by="Votes", ascending=False).head(10)
st.dataframe(votes_top10[["Title", "Rating", "Votes", "Genre"]])

# ---------- 2. Genre Distribution ----------
st.subheader("🎭 Genre Distribution")
genre_counts = df["Genre"].value_counts().reset_index()
genre_counts.columns = ["Genre", "Count"]

fig = px.bar(
    genre_counts,
    x="Genre",
    y="Count",
    title="Number of Movies per Genre",
    labels={"Genre": "Movie Genre", "Count": "Number of Movies"},
    color_discrete_sequence=["#9d075F"]
)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(genre_counts)

# ---------- 3. Average Duration by Genre ----------
st.subheader("⏱️ Average Duration by Genre")
avg_duration = df.groupby("Genre")["Duration_min"].mean().reset_index()

fig = px.bar(
    avg_duration,
    x="Duration_min",
    y="Genre",
    orientation="h",
    title="Average Movie Duration per Genre (minutes)",
    labels={"Duration_min": "Average Duration (min)", "Genre": "Movie Genre"},
    color_discrete_sequence=["#48079c"]  # Any hex color you like
)
st.plotly_chart(fig, use_container_width=True)


# ---------- 4. Voting Trends by Genre ----------
st.subheader("🗳️ Voting Trends by Genre")
avg_votes = df.groupby("Genre")["Votes"].mean().reset_index()

fig = px.bar(
    avg_votes,
    x="Genre",
    y="Votes",
    title="Average Voting Counts per Genre",
    labels={"Votes": "Average Votes", "Genre": "Movie Genre"},
    color="Votes",
    color_continuous_scale="greens"
)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(avg_votes)

# ---------- 5. Rating Distribution ----------
st.subheader("⭐ Rating Distribution")
chart_type = st.radio("Choose a visualization type:", ("Histogram", "Boxplot"), horizontal=True)

if chart_type == "Histogram":
    fig = px.histogram(
        df,
        x="Rating",
        nbins=20,
        title="Distribution of Movie Ratings",
        labels={"Rating": "Movie Rating"},
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Boxplot":
    fig = px.box(
        df,
        y="Rating",
        title="Boxplot of Movie Ratings",
        labels={"Rating": "Movie Rating"},
        color_discrete_sequence=["#ff7f0e"]
    )
    st.plotly_chart(fig, use_container_width=True)

st.write("📊 Summary Statistics of Ratings")
st.write(df["Rating"].describe())

# ---------- 6. Genre-Based Rating Leaders ----------
st.subheader("🎬 Genre-Based Rating Leaders")
genre_rating_df = df.dropna(subset=["Genre", "Rating"])

top_movies_per_genre = (
    genre_rating_df.sort_values(["Genre", "Rating"], ascending=[True, False])
    .groupby("Genre")
    .first()
    .reset_index()
)
st.dataframe(top_movies_per_genre[["Genre", "Title", "Rating"]], use_container_width=True)

# ---------- 7. Most Popular Genres by Voting ----------
st.subheader("📊 Most Popular Genres by Voting")
votes_by_genre = df.groupby("Genre")["Votes"].sum().sort_values(ascending=False).reset_index()

fig = px.pie(
    votes_by_genre,
    values="Votes",
    names="Genre",
    title="Most Popular Genres by Total Voting Counts",
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)

# ---------- 8. Duration Extremes ----------
st.subheader("⏱️ Duration Extremes")
shortest = df.loc[df["Duration_min"].idxmin()]
longest = df.loc[df["Duration_min"].idxmax()]

col1, col2 = st.columns(2)
with col1:
    st.metric("🎬 Shortest Movie", shortest["Title"], delta=f'-{shortest["Duration_min"]} mins')
with col2:
    st.metric("🎬 Longest Movie", longest["Title"], delta=f'+{longest["Duration_min"]} mins')

# ---------- 9.Ratings by Genre  ----------
st.subheader("🎭 Ratings by Genre (Heatmap)")

# Calculate average rating + count
avg_rating_by_genre = df.groupby("Genre").agg(
    Avg_Rating=("Rating", "mean"),
    Count=("Rating", "count")
).reset_index()

# Sort by rating
avg_rating_by_genre = avg_rating_by_genre.sort_values("Avg_Rating", ascending=False)

# Create pivot for heatmap
pivot = avg_rating_by_genre.set_index("Genre")[["Avg_Rating"]]

# Create annotation text (same shape as pivot)
annot_text = avg_rating_by_genre.apply(
    lambda row: f"{row['Avg_Rating']:.2f}\n({row['Count']})", axis=1
).to_frame()
annot_text.index = pivot.index  # align indices

# Plot heatmap
fig, ax = plt.subplots(figsize=(8, len(pivot) * 0.6))
sns.heatmap(
    pivot,
    annot=annot_text,   # ✅ same shape
    fmt="",
    cmap="YlGnBu",
    linewidths=0.7,
    linecolor="gray",
    cbar_kws={'label': 'Average Rating'}
)

# Styling
ax.set_title("⭐ Average Movie Ratings by Genre (with Counts) ⭐", fontsize=16, weight="bold", pad=15)
ax.set_ylabel("")
ax.set_xlabel("")

st.pyplot(fig, use_container_width=True)



# ---------- 10. Correlation Analysis ----------
st.subheader("📊 Correlation Analysis: Ratings vs Votes")

# Ensure Votes and Rating are numeric
df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Drop rows with zero or negative values
df = df[(df['Votes'] > 0) & (df['Rating'] > 0)]

# Use actual votes for plotting
df['Votes_plot'] = df['Votes']

# Debug check (optional - remove once confirmed)
print("Min Votes:", df['Votes'].min(), "Min Rating:", df['Rating'].min())

# Scatter plot with log scale
fig, ax = plt.subplots(figsize=(7, 4))
sns.scatterplot(
    x="Votes_plot",
    y="Rating",
    data=df,
    ax=ax,
    color="#1f77b4",
    alpha=0.6,
    s=50
)

# Apply log scale to x-axis
ax.set_xscale("log")

# Titles and labels
ax.set_title("Scatter Plot: Votes vs Ratings", fontsize=14, weight='bold')
ax.set_xlabel("Number of Votes", fontsize=12)
ax.set_ylabel("Rating", fontsize=12)

# Grid (for both major and minor ticks)
ax.grid(True, linestyle='--', alpha=0.5, which="both")

# Show the plot in Streamlit
st.pyplot(fig, use_container_width=True)




