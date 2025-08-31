IMDB 2024 Data Scraping and Visualizations

This project demonstrates end-to-end data scraping, cleaning, storage, and interactive visualization for IMDB movies released in 2024.
It covers scraping movie data by genre, cleaning and consolidating the data, storing it in a SQL database, and building interactive dashboards using Streamlit.

Workflow
1. Data Scraping
Uses Selenium to scrape movie details (title, rating, votes, duration, genre) from IMDB for selected genres and release year 2024.
Handles dynamic loading ("50 more" button) and robust extraction of votes and runtime.
2. Data Consolidation & Cleaning
Individual genre CSVs are merged into a single consolidated dataset.
Cleans and converts columns to appropriate data types.
Converts duration strings (e.g., "2h 15m") to total minutes.
3. Database Storage
Stores cleaned data in a TiDB Cloud SQL database.
Table schema includes: Title, Rating, Votes, Duration, Duration_Min, Genre.
4. Interactive Visualization
Streamlit dashboard for movie analysis:
Top 10 movies by rating and voting counts.
Genre-wise statistics and visualizations (pie charts, heatmaps, scatter plots).
Interactive filtering by duration, rating, votes, and genre.

