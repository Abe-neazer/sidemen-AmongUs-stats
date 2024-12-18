import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configurations
st.set_page_config(
    page_title="SIDEMEN AMONG US STATS",
    layout="wide"
)

@st.cache_data
def load_data(path: str):
    # Load the Excel file into a DataFrame
    data = pd.read_excel(path)
    return data

# File path to the Excel file
file_path = "./MoreSidemen Among Us.xlsx"
df = load_data(file_path)

# Display the loaded data
st.write("Loaded Data:")
st.dataframe(df)

# Interactive Filters
st.sidebar.header("Filter Options")

# Dropdown to select a column
selected_column = st.sidebar.selectbox(
    "Select a Column to Visualize",
    options=df.columns
)

# Multiselect for excluding names
if 'Name' in df.columns:  # Assuming there's a column named 'Name'
    excluded_names = st.sidebar.multiselect(
        "Exclude Names",
        options=df['Name'].unique(),
        default=[]
    )
    # Filter the DataFrame to exclude selected names
    filtered_df = df[~df['Name'].isin(excluded_names)]
else:
    filtered_df = df

# Plot Bar Chart
st.subheader(f"Bar Chart of {selected_column}")
if not filtered_df.empty:
    fig = px.bar(
        filtered_df,
        x='Name' if 'Name' in df.columns else filtered_df.index,
        y=selected_column,
        title=f"{selected_column} by Name (Excluding Selected)",
        labels={'Name': 'Player Name', selected_column: 'Value'},
        height=600  # Adjust chart height for larger bars
    )
    # Customize layout for larger bars
    fig.update_layout(
        bargap=0.2,  # Adjust bar gap
        bargroupgap=0.1  # Adjust gap between grouped bars
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available after applying the filters.")

# Display filtered data at the bottom
st.write("Filtered Data:")
st.dataframe(filtered_df)
