import streamlit as st
import pandas as pd
import numpy as np
import re
import data_loading as dl


st.title("My FLS mapping app")

#Identify which columns are needed
dexa_data_cols = ['Region Code', 'Region', 'ICB - Integrated Care Board',
       'Imaging Network', 'Organisation Code', 'Organisation Name',' DEXA ']

#Load data
dexa_data_2223 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2022-23-v1.csv', skiprows=13, usecols=dexa_data_cols)  
dexa_data_2324 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2023-24-v1.csv', skiprows=13, usecols=dexa_data_cols)  
dexa_data_2425 = dl.load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2024-25-v1-FINAL.csv', skiprows=13, usecols=dexa_data_cols)  

fls_list_2024 = dl.grab_clean_df('Data/FLS_List_2024.csv')
neighbourhood_health_areas = dl.grab_clean_df('Data/Neighbourhood_Health_areas.csv')
nhs_trusts = dl.grab_clean_df('Data/NHS_Trusts.csv')

#Display datasets on streamlit
st.write("DEXA scanner data 2022-23")
dexa_data_2223

st.write("DEXA scanner data 2023-24")
dexa_data_2324

st.write("DEXA scanner data 2024-25")
dexa_data_2425

st.write("FLS List 2024")
fls_list_2024

st.write("Neighbourhood Health areas")
neighbourhood_health_areas

st.write("NHS Trusts")
nhs_trusts

#Count number of dexa scanners in each year
dexa_count_2223 = dexa_data_2223['dexa_count'].sum()
dexa_count_2324 = dexa_data_2324['dexa_count'].sum()
dexa_count_2425 = dexa_data_2425['dexa_count'].sum()

#dexa_count_2223 #need to check
st.write('DEXA count for 23-24 = ', dexa_count_2324)
st.write('DEXA count for 24-25 = ', dexa_count_2425)