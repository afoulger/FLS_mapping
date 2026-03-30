import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import app

st.set_page_config(page_title="Example Map: Regions", layout="wide")

st.title("Example Map: Regions")

@st.cache_data
def get_map_data():
    # 1. Load and prepare Region Polygons
    # Ensure nhs_regions.geojson is in your root folder
    geo_df = gpd.read_file("Data/nhs_regions.geojson")
    
    # Force GPS coordinates (Pydeck requirement)
    if geo_df.crs != "EPSG:4326":
        geo_df = geo_df.to_crs(epsg="4326")
    
    # Standard color mapping
    color_map = {
        "London": [255, 99, 71, 100],
        "South East": [60, 179, 113, 100],
        "South West": [30, 144, 255, 100],
        "Midlands": [255, 165, 0, 100],
        "East of England": [147, 112, 219, 100],
        "North West": [255, 215, 0, 100],
        "North East and Yorkshire": [0, 206, 209, 100]
    }
    
     # 2. Create Site Data (Dots)
    regions_data = app.regions_table
    
    st.write(regions_data)

    geo_df = geo_df.merge(regions_data, left_on='NHSER21NM', right_on='region', how='left')

    # Apply colors and create a dedicated tooltip column for regions   Not working!
    geo_df['fill_color'] = geo_df['NHSER21NM'].map(color_map).fillna("[200, 200, 200, 100]")
    geo_df['tooltip_text'] = (
        "<b>Region:</b> " + geo_df['NHSER21NM'] + "<br/>" +
        "<b>DEXA count 2223:</b> " + geo_df['dexa_count_2223'].astype(str) + "<br/>" +
        "<b>DEXA count 2324:</b> " + geo_df['dexa_count_2324'].astype(str) + "<br/>" +
        "<b>DEXA count 2425:</b> " + geo_df['dexa_count_2425'].astype(str)
    )

    trusts_data = pd.read_csv('Data/NHS_Trusts_etr_inc_headers.csv')
    print(trusts_data.columns)

    trusts_data = trusts_data[['Organisation Code', 'Name', 'Lat', 'Long']]

    # Create a dedicated tooltip column for dots     Need to define lat and lon for dots
    trusts_data['tooltip_text'] = (
        "<b>Trust Name:</b> " + trusts_data['Name'].astype(str)
    )
    
    return geo_df, trusts_data

# Load data
try:
    geo_df, trusts_data = get_map_data()

    # --- LAYERS ---
    # Layer 1: Regions
    region_layer = pdk.Layer(
        "GeoJsonLayer",
        geo_df,
        pickable=True,
        filled=True,
        get_fill_color="fill_color",
        get_line_color=[255, 255, 255],
        get_line_width=150,
    )

    # Layer 2: Dots
    dot_layer = pdk.Layer(
        "ScatterplotLayer",
        trusts_data,
        get_position=['Long', 'Lat'],
        get_color=[255, 255, 255, 255], # Solid white dots
        get_radius=700,
        radius_min_pixels=6,
        pickable=True,
    )

    # --- MAP VIEW ---
    view_state = pdk.ViewState(
        latitude=52.5, 
        longitude=-1.1, 
        zoom=5.8,
        pitch=0
    )

    # --- RENDER ---
    st.pydeck_chart(pdk.Deck(
        layers=[region_layer, dot_layer],
        initial_view_state=view_state,
        height=800, 
        tooltip={
            "html": "{tooltip_text}",
            "style": {
                "backgroundColor": "#2b2b2b",
                "color": "white",
                "fontFamily": "sans-serif",
                "fontSize": "13px",
                "padding": "10px",
                "zIndex": "10000" # Ensures tooltip stays on top of tall maps
            }
        }
    ))
    # --- DATA TABLES ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Region List")
        st.dataframe(geo_df[['NHSER21NM']], width='stretch')
    #with col2:
    #    st.subheader("Facility List")
    #    st.dataframe(dot_df[['site_name', 'status', 'staff_count']], width='stretch')

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check if 'nhs_regions.geojson' exists in your directory and the column 'NHSER21NM' is present.")