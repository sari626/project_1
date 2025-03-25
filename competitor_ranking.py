import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# ✅ Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="4628@Saru",   # Replace with your actual password
        database="project_1",
        auth_plugin="mysql_native_password"
    )

# ✅ Fetch ranking data
def fetch_ranking_data():
    """Fetch competitor rankings data from the database"""
    connection = get_db_connection()
    query = """
    SELECT 
        cr.rank_id, cr.rank, cr.movement, cr.points, cr.competitions_played, 
        c.name AS competitor_name, c.country
    FROM Competitor_Rankings cr
    JOIN Competitors c ON cr.competitor_id = c.competitor_id
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# ✅ Homepage Dashboard
def display_homepage_dashboard(ranking_df):
    st.title("🏅 Player Ranking Dashboard")

    # 📊 Summary statistics
    total_competitors = ranking_df['competitor_name'].nunique()
    total_countries = ranking_df['country'].nunique()
    highest_points = ranking_df['points'].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Competitors", total_competitors)
    col2.metric("🌍 Countries Represented", total_countries)
    col3.metric("⭐ Highest Points", highest_points)

# ✅ Search and Filter Competitors
def search_and_filter(ranking_df):
    st.sidebar.header("🔍 Search and Filter")

    # Search by competitor name
    name_search = st.sidebar.text_input("Search Competitor by Name", "")

    # Filter by rank range
    min_rank = st.sidebar.slider(
        "Minimum Rank", 
        min_value=int(ranking_df['rank'].min()), 
        max_value=int(ranking_df['rank'].max()), 
        value=int(ranking_df['rank'].min())
    )

    max_rank = st.sidebar.slider(
        "Maximum Rank", 
        min_value=int(ranking_df['rank'].min()), 
        max_value=int(ranking_df['rank'].max()), 
        value=int(ranking_df['rank'].max())
    )

    # Filter by country
    country_filter = st.sidebar.multiselect("Select Country", ranking_df['country'].unique())

    # Filter by points threshold
    min_points = st.sidebar.slider("Minimum Points", min_value=0, max_value=int(ranking_df['points'].max()), value=0)
    max_points = st.sidebar.slider("Maximum Points", min_value=0, max_value=int(ranking_df['points'].max()), value=int(ranking_df['points'].max()))

    # Apply filters
    if name_search:
        ranking_df = ranking_df[ranking_df['competitor_name'].str.contains(name_search, case=False)]
    
    ranking_df = ranking_df[(ranking_df['rank'] >= min_rank) & (ranking_df['rank'] <= max_rank)]
    
    if country_filter:
        ranking_df = ranking_df[ranking_df['country'].isin(country_filter)]

    ranking_df = ranking_df[(ranking_df['points'] >= min_points) & (ranking_df['points'] <= max_points)]

    st.dataframe(ranking_df)
    return ranking_df

# ✅ Competitor Details Viewer
def display_competitor_details(ranking_df):
    st.subheader("🔎 Competitor Details Viewer")

    # Select a competitor from dropdown
    competitor = st.selectbox("Select Competitor", ranking_df['competitor_name'].unique())

    # Display detailed information
    competitor_data = ranking_df[ranking_df['competitor_name'] == competitor].iloc[0]
    st.write(f"**Rank:** {competitor_data['rank']}")
    st.write(f"**Movement:** {competitor_data['movement']}")
    st.write(f"**Competitions Played:** {competitor_data['competitions_played']}")
    st.write(f"**Country:** {competitor_data['country']}")
    st.write(f"**Points:** {competitor_data['points']}")

# ✅ Country-Wise Analysis
def country_wise_analysis(ranking_df):
    st.subheader("🌍 Country-Wise Analysis")

    country_stats = ranking_df.groupby('country').agg(
        total_competitors=('competitor_name', 'count'),
        avg_points=('points', 'mean')
    ).reset_index()

    st.dataframe(country_stats)

    # Visualization
    country_chart = px.bar(
        country_stats, 
        x='country', 
        y='total_competitors', 
        color='avg_points',
        title="Total Competitors and Average Points by Country",
        labels={'total_competitors': 'Number of Competitors', 'avg_points': 'Average Points'}
    )
    st.plotly_chart(country_chart)

# ✅ Leaderboards
def display_leaderboards(ranking_df):
    st.subheader("🏆 Leaderboards")

    # Top-ranked competitors
    top_ranked = ranking_df.nsmallest(10, 'rank')
    st.write("🥇 **Top 10 Ranked Competitors**")
    st.dataframe(top_ranked[['competitor_name', 'rank', 'country', 'points']])

    # Highest-point competitors
    highest_points = ranking_df.nlargest(10, 'points')
    st.write("💥 **Top 10 Highest Points Competitors**")
    st.dataframe(highest_points[['competitor_name', 'rank', 'country', 'points']])

# ✅ Main Streamlit app
def main():
    ranking_df = fetch_ranking_data()

    # Display homepage dashboard
    display_homepage_dashboard(ranking_df)

    # Search and filter competitors
    filtered_df = search_and_filter(ranking_df)

    # Display competitor details
    display_competitor_details(filtered_df)

    # Country-wise analysis
    country_wise_analysis(filtered_df)

    # Leaderboards
    display_leaderboards(filtered_df)

# Run the Streamlit app
if __name__ == '__main__':
    main()
