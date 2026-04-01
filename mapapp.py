import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import data_loading as dl

st.set_page_config(page_title="Example Map: Regions", layout="wide")

st.title("Example Map: Regions")

#Load all datasets

#Load DEXA data
dexa_data_2425, dexa_count_2425 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2024-25-v1-FINAL.csv', skiprows=13)  

#Load CDC data
cdcs = dl.load_cdc_data('Data/CDCs.csv')

#Load regions, ICBs and NHS Trusts data
regions_data = dl.load_regions_data('Data/Regions_eauth_inc_headers.csv')
icbs_summary = dl.load_icbs_data('Data/ICBs_eccg_inc_headers.csv')
nhs_trusts_data = dl.load_nhs_trusts_data('Data/NHS_Trusts_etr_inc_headers.csv')

#Create CDCs Trust level data
cdcs_trust_level = dl.create_trust_level_cdc_data(cdcs)

#Create NHS Trusts table 
nhs_trusts_table = dl.create_nhs_trusts_table(nhs_trusts_data, dexa_data_2425, cdcs_trust_level)

#Create ICB level table
#icb_level_summary, icbs_summary = dl.create_icb_level_table(nhs_trusts_table, icbs_summary)

#Create Region level table
regions_summary, regions_data = dl.create_region_level_table(nhs_trusts_table, regions_data)


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
    
    #Create variable with region names in upper case
    geo_df['NHSER21NM_upper'] = geo_df['NHSER21NM'].str.upper() 
   
    
    # 2. Create Site Data (Dots)
    
    st.write(regions_data)

    geo_df = geo_df.merge(regions_data, left_on='NHSER21NM_upper', right_on='region_name', how='left')

    # Apply colors and create a dedicated tooltip column for regions   Not working!
    geo_df['fill_color'] = geo_df['NHSER21NM'].map(color_map).fillna("[200, 200, 200, 100]")
    geo_df['tooltip_text'] = (
        "<b>Region:</b> " + geo_df['NHSER21NM'] + "<br/>" +
        "<b>DEXA count:</b> " + geo_df['dexa_count_2425'].astype(str) + "<br/>" +
        "<b>CDC count:</b> " + geo_df['cdc_count'].astype(str)
    )

    # Create a dedicated tooltip column for dots
    nhs_trusts_data['tooltip_text'] = (
        "<b>Trust Name:</b> " + nhs_trusts_data['trust_name'].astype(str)
    )
    
    return geo_df, nhs_trusts_data

# Load data
try:
    geo_df, nhs_trusts_data = get_map_data()

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
        nhs_trusts_data,
        get_position=['long', 'lat'],
        get_color=[255, 255, 255, 255], # Solid white dots
        get_radius=100,
        radius_min_pixels=4,
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