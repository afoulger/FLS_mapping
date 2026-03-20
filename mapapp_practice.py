import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd

st.set_page_config(page_title="NHS England Regions & Sites", layout="wide")

st.title("🏥 NHS England: Regions & Facilities")

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
    
    # Apply colors and create a dedicated tooltip column for regions
    geo_df['fill_color'] = geo_df['NHSER21NM'].map(color_map).fillna("[200, 200, 200, 100]")
    geo_df['tooltip_text'] = "<b>Region:</b> " + geo_df['NHSER21NM']
    
    # 2. Create Site Data (Dots)
    dot_data = pd.DataFrame({
        'site_name': ['London HQ', 'Manchester Hub', 'Birmingham Site', 'Leeds Clinic', 'Bristol Office', 'Newcastle Base'],
        'lat': [51.5074, 53.4808, 52.4862, 53.8008, 51.4545, 54.9783],
        'lon': [-0.1278, -2.2426, -1.8904, -1.5491, -2.5879, -1.6178],
        'staff_count': [450, 310, 290, 120, 85, 115],
        'status': ['Operational', 'Operational', 'Under Reno', 'Operational', 'Closed', 'Operational']
    })
    
    # Create a dedicated tooltip column for dots
    dot_data['tooltip_text'] = (
        "<b>Facility:</b> " + dot_data['site_name'] + "<br/>" +
        "<b>Status:</b> " + dot_data['status'] + "<br/>" +
        "<b>Staff:</b> " + dot_data['staff_count'].astype(str)
    )
    
    return geo_df, dot_data

# Load data
try:
    geo_df, dot_df = get_map_data()

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
        dot_df,
        get_position=['lon', 'lat'],
        get_color=[255, 255, 255, 255], # Solid white dots
        get_radius=7000,
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
    with col2:
        st.subheader("Facility List")
        st.dataframe(dot_df[['site_name', 'status', 'staff_count']], width='stretch')

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check if 'nhs_regions.geojson' exists in your directory and the column 'NHSER21NM' is present.")