import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import numpy as np
import json
import data_loading as dl

st.set_page_config(layout="wide", page_title="NHS Mapping Tool")

st.title("NHS Mapping Tool: ICB & Regional Views")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Map Settings")
    # THE SWITCHER: This controls which data path we take
    map_mode = st.radio(
        "Select View Layer:",
        options=["ICB Boundaries", "NHS Regions"],
        index=0
    )
    
    show_dots = st.checkbox("Show Site Locations", value=True)

# --- DATA LOADING FUNCTIONS ---

#Load all data 

#Load DEXA data
dexa_data_2425, dexa_count_2425 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2024-25-v1-FINAL.csv', skiprows=13)  

#Load CDC data
cdcs = dl.load_cdc_data('Data/CDCs.csv')

#Load regions, ICBs and NHS Trusts data
regions_data = dl.load_regions_data('Data/Regions_eauth_inc_headers.csv')
icbs_data, icbs_summary = dl.load_icbs_data('Data/ICBs_eccg_inc_headers.csv')
nhs_trusts_data = dl.load_nhs_trusts_data('Data/NHS_Trusts_etr_inc_headers.csv')

#Create CDCs Trust level data
cdcs_trust_level = dl.create_trust_level_cdc_data(cdcs)

#Create NHS Trusts table 
nhs_trusts_table = dl.create_nhs_trusts_table(nhs_trusts_data, dexa_data_2425, cdcs_trust_level)

#Create ICB level table
icb_level_summary, icbs_summary = dl.create_icb_level_table(nhs_trusts_table, icbs_summary)

#Create ICBs code mapping
icbs_code_mapping = dl.load_icbs_code_mapping('Data/code_mapping.csv')

#Create Region level table
regions_summary, regions_data = dl.create_region_level_table(nhs_trusts_table, regions_data)

@st.cache_data
def load_icb_data():
    """Loads ICB GeoJSON and merges with CSV mapping."""
    # Using local paths as per your first snippet
    gdf = gpd.read_file("Data/icb_boundaries.geojson")
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    
    df_csv = pd.read_csv("Data/code_mapping.csv")
    merged_gdf = gdf.merge(df_csv, left_on="ICB23CD", right_on="ICB24CD", how="left")
    
    # Generate random colors
    np.random.seed(42)
    merged_gdf['fill_color'] = [
        [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255), 140] 
        for _ in range(len(merged_gdf))
    ]
    return json.loads(merged_gdf.to_json())

@st.cache_data
def load_region_data():
    """Loads Regional GeoJSON and merges with region statistics."""
    geo_df = gpd.read_file("Data/nhs_regions.geojson")
    if geo_df.crs != "EPSG:4326":
        geo_df = geo_df.to_crs(epsg="4326")

    color_map = {
        "London": [255, 99, 71, 150],
        "South East": [60, 179, 113, 150],
        "South West": [30, 144, 255, 150],
        "Midlands": [255, 165, 0, 150],
        "East of England": [147, 112, 219, 150],
        "North West": [255, 215, 0, 150],
        "North East and Yorkshire": [0, 206, 209, 150]
    }
    
    #merge regions data and regions geojson 
    geo_df = geo_df.merge(regions_data, left_on=geo_df['NHSER21NM'].str.upper(), right_on='region_name', how='left')

    # Apply colors (Fixed mapping logic)
    geo_df['fill_color'] = geo_df['NHSER21NM'].map(color_map)
    # Fill missing with grey
    geo_df['fill_color'] = geo_df['fill_color'].apply(lambda x: x if isinstance(x, list) else [200, 200, 200, 100])
    
    return json.loads(geo_df.to_json())

@st.cache_data
def get_dexa_dots():
    """Placeholder for your site/trust dot data."""
    # This uses your 'Dot 1-5' example or nhs_trusts_data
    cdcs_data = cdcs[['lat', 'long', 'cdc_name']]
    return pd.DataFrame(cdcs_data)

# --- MAIN LOGIC ---

try:
    map_layers = []

    # 1. Select the Base GeoJSON Layer based on Radio Button
    if map_mode == "ICB Boundaries":
        geojson_data = load_icb_data()
        tooltip_html = """
            <b>ICB:</b> {ICB23NM}<br/>
            <b>Code 24:</b> {ICB24CD}
        """
    else:
        geojson_data = load_region_data()
        tooltip_html = """
            <b>Region:</b> {NHSER21NM}<br/>
            <b>Code:</b> {NHSER21CD}
        """

    base_layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
    )
    map_layers.append(base_layer)

    # 2. Add Dots if enabled
    if show_dots:
        dots_df = get_site_dots()
        dots_layer = pdk.Layer(
            "ScatterplotLayer",
            dots_df,
            get_position=["lon", "lat"],
            get_color=[255, 255, 255, 200],
            get_radius=8000,
            pickable=True,
        )
        map_layers.append(dots_layer)

    # 3. Render Map
    view_state = pdk.ViewState(latitude=52.5, longitude=-1.5, zoom=6)

    # Final Tooltip Logic
    # If the hovered object has 'name', it's a dot. Otherwise, it's a polygon.
    st.pydeck_chart(pdk.Deck(
        layers=map_layers,
        initial_view_state=view_state,
        tooltip={
            "html": f"""
                <div style="font-family: sans-serif; padding: 5px;">
                    {{% if name %}}
                        <b style="color: #FF4B4B;">Location:</b> {{name}}
                    {{% else %}}
                        {tooltip_html}
                    {{% endif %}}
                </div>
            """,
            "style": {"color": "white", "backgroundColor": "#222"}
        }
    ))

except Exception as e:
    st.error(f"Error loading map: {e}")
    st.info("Ensure 'icb_boundaries.geojson' and 'Data/nhs_regions.geojson' exist.")