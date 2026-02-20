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
nh_areas = dl.grab_clean_df('Data/Neighbourhood_Health_areas.csv')
nhs_trusts = dl.grab_clean_df('Data/NHS_Trusts.csv')
cdcs = dl.grab_clean_df('Data/CDCs.csv', skiprows=1)

print(dexa_data_2223.columns)
print(dexa_data_2324.columns)
print(dexa_data_2425.columns)
print(fls_list_2024.columns)
print(nh_areas.columns)
print(nhs_trusts.columns)
print(cdcs.columns)

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
nh_areas

st.write("NHS Trusts")
nhs_trusts

st.write("CDCs")
cdcs

#Count number of dexa scanners in each year
dexa_count_2223 = dexa_data_2223['dexa_count'].sum()
dexa_count_2324 = dexa_data_2324['dexa_count'].sum()
dexa_count_2425 = dexa_data_2425['dexa_count'].sum()

st.write('DEXA count for 22-23 = ', dexa_count_2223)
st.write('DEXA count for 23-24 = ', dexa_count_2324)
st.write('DEXA count for 24-25 = ', dexa_count_2425)

#Create a combined table

nhs_trusts_table = nhs_trusts.merge(dexa_data_2223[['org_name','dexa_count']].rename(columns = {'dexa_count':'dexa_count_2223'}), left_on='nhs_trust_name', right_on='org_name', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['org_name'])

nhs_trusts_table = nhs_trusts_table.merge(dexa_data_2324[['org_name','dexa_count']].rename(columns = {'dexa_count':'dexa_count_2324'}), left_on='nhs_trust_name', right_on='org_name', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['org_name'])

nhs_trusts_table = nhs_trusts_table.merge(dexa_data_2425[['org_name','dexa_count']].rename(columns = {'dexa_count':'dexa_count_2425'}), left_on='nhs_trust_name', right_on='org_name', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['org_name'])

nhs_trusts_table = nhs_trusts_table.merge(fls_list_2024[['fls_service_unit','nhs_trust']], left_on='nhs_trust_name', right_on='nhs_trust', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['nhs_trust'])

nhs_trusts_table = nhs_trusts_table.merge(nh_areas[['nnhip_places','associated_trust_1']].rename(columns = {'nnhip_places':'nnhip_places_1'}), left_on='nhs_trust_name', right_on='associated_trust_1', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['associated_trust_1'])

nhs_trusts_table = nhs_trusts_table.merge(nh_areas[['nnhip_places','associated_trust_2']].rename(columns = {'nnhip_places':'nnhip_places_2'}), left_on='nhs_trust_name', right_on='associated_trust_2', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['associated_trust_2'])

nhs_trusts_table = nhs_trusts_table.merge(nh_areas[['nnhip_places','associated_trust_3']].rename(columns = {'nnhip_places':'nnhip_places_3'}), left_on='nhs_trust_name', right_on='associated_trust_3', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['associated_trust_3'])

nhs_trusts_table = nhs_trusts_table.merge(cdcs[['name_of_cdc','updated_nhs_trust_name']], left_on='nhs_trust_name', right_on='updated_nhs_trust_name', how='left')
nhs_trusts_table = nhs_trusts_table.drop(columns=['updated_nhs_trust_name'])

st.write("NHS Trusts table")
nhs_trusts_table