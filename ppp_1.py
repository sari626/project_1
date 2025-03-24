import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="4628@Saru",
        database="project_1",
        auth_plugin="mysql_native_password"
    )

def fetch_data():
    connection = get_db_connection()
    query = """
    SELECT 
        c.competition_id, c.competition_name, c.parent_id, c.type, c.gender, c.category_id
    FROM Competitions c
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def display_interface():
    st.title("🎾 Tennis Competitions Dashboard")
    
    # Fetch Data
    df = fetch_data()
    
    # Filters
    st.sidebar.header("🔍 Filters")
    gender_filter = st.sidebar.multiselect("Select Gender", options=["men", "women"], default=["men", "women"])
    type_filter = st.sidebar.multiselect("Select Type", options=["singles", "doubles"], default=["singles", "doubles"])
    category_filter = st.sidebar.text_input("Search Category (e.g., ATP, WTA, ITF)", "")
    name_search = st.sidebar.text_input("Search Competition Name", "")
    
    # Apply Filters
    if gender_filter:
        df = df[df['gender'].isin(gender_filter)]
    if type_filter:
        df = df[df['type'].isin(type_filter)]
    if category_filter:
        df = df[df['competition_name'].str.contains(category_filter, case=False, na=False)]
    if name_search:
        df = df[df['competition_name'].str.contains(name_search, case=False, na=False)]
    
    # Display Data
    st.dataframe(df)
    
    # Visualizations
    st.subheader("📊 Visualizations")
    
    # Bar Chart: Gender Distribution
    gender_chart = px.bar(df, x='gender', title='Competitions by Gender', color='gender')
    st.plotly_chart(gender_chart)
    
    # Pie Chart: Competition Type Distribution
    type_chart = px.pie(df, names='type', title='Competition Types Distribution')
    st.plotly_chart(type_chart)

def main():
    display_interface()

if __name__ == '__main__':
    main()
