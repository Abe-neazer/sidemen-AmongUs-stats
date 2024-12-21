import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configurations ---
st.set_page_config(
    page_title="Sidemen Among Us Stats",
    layout="wide"
)

# --- Function to Fetch Data from Google Sheet ---
def fetch_data(sheet_url: str):
    try:
        return pd.read_csv(sheet_url)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- Updated Google Sheet CSV URL ---
sheet_url = "https://docs.google.com/spreadsheets/d/1g3Esmr1-Z5jt5_mqOv9-f9fvyFezgT_2Z-8G7w5ChSU/export?format=csv"

# Fetch data from the Google Sheet
df = fetch_data(sheet_url)

# --- Helper Function to Convert Data to CSV ---
def convert_df_to_csv(data):
    return data.to_csv(index=False).encode('utf-8')

# --- App Layout ---
st.title("Sidemen Among Us Stats")
st.caption("Explore and analyze player stats dynamically with filters and interactive visuals.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Light/Dark Mode Toggle
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])
st.markdown(
    f"""
    <style>
        .main {{
            background-color: {"#0E1117" if theme == "Dark" else "#FFFFFF"};
            color: {"#FFFFFF" if theme == "Dark" else "#000000"};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Check if data is loaded successfully
if not df.empty:
    # Select a Column to Visualize
    selected_column = st.sidebar.selectbox(
        "Select a Column to Visualize",
        options=df.columns
    )

    # Multiselect to Exclude Players
    if 'Name' in df.columns:
        excluded_names = st.sidebar.multiselect(
            "Exclude Names",
            options=df['Name'].unique(),
            default=[]
        )
        filtered_df = df[~df['Name'].isin(excluded_names)]
    else:
        filtered_df = df

    # Add Sliders for Numeric Filters
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        min_val, max_val = df[col].min(), df[col].max()
        selected_range = st.sidebar.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
        filtered_df = filtered_df[(filtered_df[col] >= selected_range[0]) & (filtered_df[col] <= selected_range[1])]

    # Add Search Box for Text Filters
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        search_term = st.sidebar.text_input(f"Search in {col}")
        if search_term:
            filtered_df = filtered_df[filtered_df[col].str.contains(search_term, case=False, na=False)]

    # --- Tabs for Navigation ---
    tab1, tab2, tab3 = st.tabs(["Overview", "Filters", "Charts"])

    # Tab 1: Overview
    with tab1:
        st.header("Overview")
        st.dataframe(df, column_config={
            "Name": st.column_config.Column(pinned=True),
        },)     

        # Stats Summary
        st.subheader("Interactive Stats Summary")
        cols = st.columns(3)
        for i, col in enumerate(numeric_cols):
            cols[i % 3].metric(
                label=f"{col} (Avg)",
                value=f"{filtered_df[col].mean():.2f}" if not filtered_df.empty else "N/A"
            )

    # Tab 2: Filtered Data
    with tab2:
        st.header("Filtered Data")
        st.dataframe(filtered_df)

        # Download Filtered Data Button
        csv_data = convert_df_to_csv(filtered_df)
        st.download_button(
            label="Download Filtered Data",
            data=csv_data,
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    # Tab 3: Charts
    with tab3:
        st.header("Charts")

        # Dynamic Chart Type Selection
        chart_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])

        # Generate Chart
        st.subheader(f"{chart_type} of {selected_column}")
        if not filtered_df.empty:
            chart_kwargs = {
                "data_frame": filtered_df,
                "x": 'Name' if 'Name' in df.columns else filtered_df.index,
                "y": selected_column,
                "title": f"{selected_column} by Name (Excluding Selected)",
                "labels": {"Name": "Player Name", selected_column: "Value"},
                "height": 600,
            }

            if chart_type == "Bar Chart":
                fig = px.bar(**chart_kwargs)
            elif chart_type == "Line Chart":
                fig = px.line(**chart_kwargs)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(**chart_kwargs)

            # Update Chart Theme
            fig.update_layout(
                template="plotly_dark" if theme == "Dark" else "plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available after applying the filters.")
else:
    st.warning("No data available. Please check the Google Sheet URL or try again later.")

# --- Manual Refresh Button ---
if st.button("Refresh Data"):
    df = fetch_data(sheet_url)
    st.write("Data refreshed successfully!")
