import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import data_loading as dl

st.set_page_config(page_title="Example Map: Regions", layout="wide")

st.title("NHS Mapping Tool: ICB & Regional Views")

# -- Load all datasets -- 

#Load DEXA data
dexa_data_2425, dexa_count_2425 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2024-25-v1-FINAL.csv', skiprows=13)  

#Load CDC data
cdcs = dl.load_cdc_data('Data/CDCs.csv')

#Load regions, ICBs and NHS Trusts data
regions_data = dl.load_regions_data('Data/Regions_eauth_inc_headers.csv')
icbs_data, icbs_summary = dl.load_icbs_data('Data/ICBs_eccg_inc_headers.csv')
icb_pop = dl.load_icb_pop(('Data/Mid_2024_ICB_populations.csv'))
nhs_trusts_data = dl.load_nhs_trusts_data('Data/NHS_Trusts_etr_inc_headers.csv')

#Create CDCs Trust level data
cdcs_trust_level = dl.create_trust_level_cdc_data(cdcs)

#Create NHS Trusts table 
nhs_trusts_table = dl.create_nhs_trusts_table(nhs_trusts_data, dexa_data_2425, cdcs_trust_level)

#Create ICB level table
icb_level_summary, icbs_summary = dl.create_icb_level_table(nhs_trusts_table, icbs_summary)

#Create ICBs code mapping
icbs_code_mapping = dl.load_icbs_code_mapping('Data/code_mapping.csv')

#Create aggregated ICB population table
icb_pop_agg = dl.create_icb_pop_agg(icb_pop)

#Create Region level table
regions_summary, regions_data = dl.create_region_level_table(nhs_trusts_table, regions_data)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Map Settings")
    # THE SWITCHER: This controls which data path we take
    map_mode = st.radio(
        "Select View Layer:",
        options=["ICB Boundaries", "NHS Regions"],
        index=0
    )
    
    show_cdc_dots = st.checkbox("Show CDC Locations", value=True)

    show_nhs_trust_dots = st.checkbox("Show NHS Trust Locations", value=True)

with st.sidebar:
    st.divider() # Adds a clean line between controls and info
    with st.expander("ℹ️ About this Tool"):
        st.markdown("""
        ### NHS Mapping Tool
        This dashboard provides a visual overview of **Integrated Care Boards (ICBs)** and **NHS Regions**.
        
        **Data Sources:**
        * **DEXA Stats:** 2024-25 National Imaging Collection.
        * **Boundaries:** ONS Geography Portal.
        * **Locations:** CDC and Trust master lists.
        
        **Version:** 1.0.4  
        **Last Updated:** April 2026
                    
        **Contact**: anne.foulger@dhsc.gov.uk
        """)

@st.cache_data
def load_icb_data():
    """Loads ICB GeoJSON and merges with ICB data"""
    gdf = gpd.read_file("Data/icb_boundaries.geojson")
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    
    gdf = gdf.merge(icbs_code_mapping, left_on="ICB23CD", right_on="icb24cd", how="left")
    gdf = gdf.merge(icbs_summary, left_on="icb24cdh", right_on="icb_code", how="left")
    gdf = gdf.merge(icb_pop_agg, left_on="icb24cd", right_on="icb_2024_code", how="left")
    gdf['dexas_per_million'] = gdf["dexa_count_2425"] / gdf["total_icb_pop"] * 1000000
    gdf['dexas_per_million'] = gdf['dexas_per_million'].round(1)

    # Generate random colors
    #np.random.seed(42)
    #gdf['fill_color'] = [
    #    [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255), 140] 
    #    for _ in range(len(gdf))
    #]

    #Apply colors
    #gdf['fill_color'] = [     
    #    [242, 242, 242, 100] if count < 1 else [32, 115, 188, 100]     
    #    for count in gdf['dexas_per_million']
    #]

    colours =[[242, 242, 242, 255], 
              [173, 209, 241, 255],
              [107, 172, 230, 255],
              [ 32, 115, 188, 255],
              [ 18,  67, 109, 255],
              [  9,  33,  53, 255]
              ]


    gdf['bin'] = pd.cut(
        gdf["dexas_per_million"],
        bins=[0,1,2,3,4,5,float("inf")],
        labels=False
        )

    gdf['fill_color'] = gdf['bin'].map(lambda i: colours[int(i)] if pd.notna(i) else [255,255,255,255])

    # Create a dedicated tooltip column for ICBs
    gdf['tooltip_text'] = (
        "<b>ICB:</b> " + gdf['icb_name'] + "<br/>" +
        "<b>DEXA count:</b> " + gdf['dexa_count_2425'].astype(str) + "<br/>" +
        "<b>DEXAs per million people:</b> " + gdf['dexas_per_million'].astype(str) + "<br/>" +
        "<b>CDC count:</b> " + gdf['cdc_count'].astype(str)
    )

    # Create regional population table

    region_pop = gdf[['region_code', 'total_icb_pop']]
    region_pop_agg = region_pop.groupby(['region_code']).agg(total_region_pop=('total_icb_pop', 'sum')).reset_index()

    return json.loads(gdf.to_json()), region_pop_agg

@st.cache_data
def load_region_data(region_pop_agg):
    # 1. Load and prepare Region Polygons
    # Ensure nhs_regions.geojson is in your root folder
    geo_df = gpd.read_file("Data/nhs_regions.geojson")
    
    # Force GPS coordinates (Pydeck requirement)
    if geo_df.crs != "EPSG:4326":
        geo_df = geo_df.to_crs(epsg="4326")
    
    # Standard color mapping
    #color_map = {
    #    "London": [255, 99, 71, 100],
    #    "South East": [60, 179, 113, 100],
    #    "South West": [30, 144, 255, 100],
    #    "Midlands": [255, 165, 0, 100],
    #    "East of England": [147, 112, 219, 100],
    #    "North West": [255, 215, 0, 100],
    #    "North East and Yorkshire": [0, 206, 209, 100]
    #}
    
    #merge regions data and regions geojson 
    geo_df = geo_df.merge(regions_data, left_on=geo_df['NHSER21NM'].str.upper(), right_on='region_name', how='left')
    geo_df = geo_df.merge(region_pop_agg, left_on='region_code', right_on='region_code', how='left')
    geo_df['dexas_per_million'] = geo_df["dexa_count_2425"] / geo_df["total_region_pop"] * 1000000
    geo_df['dexas_per_million'] = geo_df['dexas_per_million'].round(1)
    
    # Apply colors 
    #geo_df['fill_color'] = geo_df['NHSER21NM'].map(color_map).fillna("[200, 200, 200, 100]")

    colours =[[242, 242, 242, 255], 
              [173, 209, 241, 255],
              [107, 172, 230, 255],
              [ 32, 115, 188, 255],
              [ 18,  67, 109, 255],
              [  9,  33,  53, 255]
              ]


    geo_df['bin'] = pd.cut(
        geo_df["dexas_per_million"],
        bins=[0,1,2,3,4,5,float("inf")],
        labels=False
        )

    geo_df['fill_color'] = geo_df['bin'].map(lambda i: colours[int(i)] if pd.notna(i) else [255,255,255,255])



    #geo_df['fill_color'] = [     
    #    [0, 206, 209, 100] if count > 20 else [255, 215, 0, 100]     
    #    for count in geo_df['dexa_count_2425'] 
    #]
 

    # Fill missing with grey
    #geo_df['fill_color'] = geo_df['fill_color'].apply(lambda x: x if isinstance(x, list) else [200, 200, 200, 100])
    
    # Create a dedicated tooltip column for regions
    geo_df['tooltip_text'] = (
        "<b>Region:</b> " + geo_df['NHSER21NM'] + "<br/>" +
        "<b>DEXA count:</b> " + geo_df['dexa_count_2425'].astype(str) + "<br/>" +
        "<b>DEXAs per million people:</b> " + geo_df['dexas_per_million'].astype(str) + "<br/>" +
        "<b>CDC count:</b> " + geo_df['cdc_count'].astype(str)
    )

    return json.loads(geo_df.to_json())

    
@st.cache_data
def get_cdc_dots():
 
    # Create a dedicated tooltip column for dots
    cdcs['tooltip_text'] = (
        "<b>CDC Name:</b> " + cdcs['name_of_cdc'].astype(str)
        )

    return pd.DataFrame(cdcs)

@st.cache_data
def get_nhs_trust_dots():
 
    # Create a dedicated tooltip column for dots
    nhs_trusts_data['tooltip_text'] = (
        "<b>Trust Name:</b> " + nhs_trusts_data['trust_name'].astype(str)
        )

    return pd.DataFrame(nhs_trusts_data)

try:
    map_layers = []

    # 1. Select the Base GeoJSON Layer based on Radio Button
    if map_mode == "ICB Boundaries":
        geojson_data, region_pop_agg = load_icb_data()
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**This map shows ICB Boundaries**")

        with col2:
            st.write("DEXA scanners per million population:")

        col1, col2, col3, col4 = st.columns(4)
        
        with col3:
          
            legend_items = [
                ("0.1 - 1.0", [242, 242, 242]),
                ("1.1 - 2.0", [173, 209, 241]), 
                ("2.1 - 3.0", [107, 172, 230])
            ]

            for label, rgb in legend_items:
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin:4px 0;">'
                    f'<span style="background:rgb({rgb[0]},{rgb[1]},{rgb[2]});'
                    f'width:16px;height:16px;display:inline-block;margin-right:8px;'
                    f'border:1px solid #999;"></span>{label}</div>',
                    unsafe_allow_html=True,
                )

            st.write("")

        with col4: 
            legend_items = [
                ("3.1 - 4.0", [32, 115, 188]), 
                ("4.1 - 5.0", [18, 67, 109]), 
                ("5.1 or more", [9, 33, 53])
            ]

            for label, rgb in legend_items:
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin:4px 0;">'
                    f'<span style="background:rgb({rgb[0]},{rgb[1]},{rgb[2]});'
                    f'width:16px;height:16px;display:inline-block;margin-right:8px;'
                    f'border:1px solid #999;"></span>{label}</div>',
                    unsafe_allow_html=True,
                )
            
            st.write("")

    else:
        geojson_data, region_pop_agg = load_icb_data() #this is needed for regional population figures
        geojson_data = load_region_data(region_pop_agg)
       
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**This map shows NHS Regions**")

        with col2:
            st.write("DEXA scanners per million population:")

        col1, col2, col3, col4 = st.columns(4)
        
        with col3:
          
            legend_items = [
                ("0.1 - 1.0", [242, 242, 242]),
                ("1.1 - 2.0", [173, 209, 241]), 
                ("2.1 - 3.0", [107, 172, 230])
            ]

            for label, rgb in legend_items:
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin:4px 0;">'
                    f'<span style="background:rgb({rgb[0]},{rgb[1]},{rgb[2]});'
                    f'width:16px;height:16px;display:inline-block;margin-right:8px;'
                    f'border:1px solid #999;"></span>{label}</div>',
                    unsafe_allow_html=True,
                )

            st.write("")

        with col4: 
            legend_items = [
                ("3.1 - 4.0", [32, 115, 188]), 
                ("4.1 - 5.0", [18, 67, 109]), 
                ("5.1 or more", [9, 33, 53])
            ]

            for label, rgb in legend_items:
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin:4px 0;">'
                    f'<span style="background:rgb({rgb[0]},{rgb[1]},{rgb[2]});'
                    f'width:16px;height:16px;display:inline-block;margin-right:8px;'
                    f'border:1px solid #999;"></span>{label}</div>',
                    unsafe_allow_html=True,
                )
            
            st.write("")

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

    # 2. Add CDC Dots if enabled
    if show_cdc_dots:
        dots_df = get_cdc_dots()
        dots_layer = pdk.Layer(
            "ScatterplotLayer",
            dots_df,
            get_position=["lon", "lat"],
            get_color=[255, 14, 203, 240], # CDC dots colour
            get_radius=10000,
            radius_min_pixels=3,  # Prevents dots from disappearing when zooming out
            radius_max_pixels=10, # Prevents dots from becoming "blobs" when zooming in
            pickable=True,
        )
        map_layers.append(dots_layer)

    #  2. Add NHS Trust Dots if enabled
    if show_nhs_trust_dots:
        dots_df2 = get_nhs_trust_dots()
        dots_layer2 = pdk.Layer(
            "ScatterplotLayer",
            dots_df2,
            get_position=["lon", "lat"],
            get_color=[255, 255, 255, 200], # Trust dots colour
            get_radius=4000,
            radius_min_pixels=3,  # Prevents dots from disappearing when zooming out
            radius_max_pixels=10, # Prevents dots from becoming "blobs" when zooming in
            pickable=True,
        )
        map_layers.append(dots_layer2)

    # --- MAP VIEW ---
    view_state = pdk.ViewState(
        latitude=52.5, 
        longitude=-1.1, 
        zoom=4.8,
        pitch=0
    )

    # --- RENDER ---
    st.pydeck_chart(pdk.Deck(
        layers=map_layers,
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
    st.subheader("Data Explorer")

    # 1. NHS Trusts Expander
    with st.expander(f"🏥 NHS Trusts ({len(nhs_trusts_data)} sites)"):
        st.write("Full list of NHS Trusts including DEXA and CDC mapping.")
        # width makes the table fill the expander
        st.dataframe(nhs_trusts_data, width="stretch")

    # 2. CDCs Expander
    with st.expander(f"📍 Community Diagnostic Centres ({len(cdcs)} sites)"):
        st.info("Note: Longitude and Latitude for some CDCs may be estimated.")
        st.dataframe(cdcs, width="stretch")

    # 3. Boundaries Expander (Optional, but useful for the polygons)
    with st.expander("🗺️ Boundary Metadata"):
        # Extracts the 'properties' from the GeoJSON features into a table
        geo_props = pd.DataFrame([f['properties'] for f in geojson_data['features']])
        st.dataframe(geo_props, width="stretch")



except Exception as e:
    st.error(f"Error: {e}")