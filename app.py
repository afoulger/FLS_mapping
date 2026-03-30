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

#dexa_trust_names_lookup = dl.grab_clean_df('Data/dexa_trust_names_lookup.csv')
#fls_list_2024 = dl.grab_clean_df('Data/FLS_List_2024.csv')
#nh_areas = dl.grab_clean_df('Data/Neighbourhood_Health_areas.csv')
#nhs_trusts = dl.grab_clean_df('Data/NHS_Trusts.csv')
cdcs = dl.grab_clean_df('Data/CDCs.csv', skiprows=1)
#trust_ics_region_mapping =  dl.grab_clean_df('Data/Trust_ICS_Region_mapping.csv')
regions_data = dl.grab_clean_df('Data/Regions_eauth_inc_headers.csv')
icbs_data = dl.grab_clean_df('Data/ICBs_eccg_inc_headers.csv')
nhs_trusts_data = dl.grab_clean_df('Data/NHS_Trusts_etr_inc_headers.csv')

regions_data = regions_data[['organisation_code', 'name', 'address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'postcode', 'open_date', 'close_date', 'lat', 'long']]
regions_data = regions_data.rename(columns = {'organisation_code':'region_code','name':'region_name'})

icbs_data = icbs_data[['national_grouping', 'high_level_health_geography', 'name','address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'postcode', 'open_date', 'close_date', 'lat', 'long']]
icbs_data = icbs_data.rename(columns = {'national_grouping':'region_code','high_level_health_geography':'icb_code', 'name':'icb_name'})

nhs_trusts_data = nhs_trusts_data[['organisation_code', 'name', 'national_grouping', 'high_level_health_geography','address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'postcode', 'open_date', 'close_date', 'lat', 'long']]
nhs_trusts_data = nhs_trusts_data.rename(columns = {'organisation_code':'trust_code','name':'trust_name'})


#Display datasets on streamlit
st.write("DEXA scanner data 2022-23")
dexa_data_2223

st.write("DEXA scanner data 2023-24")
dexa_data_2324

st.write("DEXA scanner data 2024-25")
dexa_data_2425

#st.write("DEXA Trust Names Lookup")
#dexa_trust_names_lookup

#st.write("FLS List 2024")
#fls_list_2024

#st.write("Neighbourhood Health areas")
#nh_areas

#st.write("NHS Trusts")
#nhs_trusts

st.write("CDCs")
cdcs

#st.write("Trust_ICS_Region_mapping")
#trust_ics_region_mapping

st.write("Regions_data")
regions_data

st.write("ICBs_data")
icbs_data

st.write("NHS_Trusts_data")
nhs_trusts_data


#Merge correct Trust names onto DEXA data
#dexa_data_2223 = dl.update_dexa_trust_names(dexa_data_2223, dexa_trust_names_lookup)
#dexa_data_2324 = dl.update_dexa_trust_names(dexa_data_2324, dexa_trust_names_lookup)
#dexa_data_2425 = dl.update_dexa_trust_names(dexa_data_2425, dexa_trust_names_lookup)

#st.write("DEXA scanner data 2022-23 updated")
#dexa_data_2223

#st.write("DEXA scanner data 2023-24 updated")
#dexa_data_2324

#st.write("DEXA scanner data 2024-25 updated")
#dexa_data_2425

#Count number of dexa scanners in each year
dexa_count_2223 = dexa_data_2223['dexa_count'].sum()
dexa_count_2324 = dexa_data_2324['dexa_count'].sum()
dexa_count_2425 = dexa_data_2425['dexa_count'].sum()

st.write('DEXA count for 22-23 = ', dexa_count_2223)
st.write('DEXA count for 23-24 = ', dexa_count_2324)
st.write('DEXA count for 24-25 = ', dexa_count_2425)

#Create a combined table

#st.write('Original NHS Trusts list', nhs_trusts.shape)

nhs_trusts_table = nhs_trusts_data   #ideally want to filter out closed trusts at this point
                            
st.write("NHS Trusts table columns")
nhs_trusts_table.columns   
dexa_data_2223.columns                         

nhs_trusts_table = dl.merge_data(dexa_data_2223, nhs_trusts_table, 'trust_code', 'dexa_trust_code', 'dexa_count',{'dexa_count':'dexa_count_2223'})
nhs_trusts_table = dl.merge_data(dexa_data_2324, nhs_trusts_table, 'trust_code', 'dexa_trust_code', 'dexa_count',{'dexa_count':'dexa_count_2324'})
nhs_trusts_table = dl.merge_data(dexa_data_2425, nhs_trusts_table, 'trust_code', 'dexa_trust_code', 'dexa_count',{'dexa_count':'dexa_count_2425'})

#Replace nulls with zeroes
nhs_trusts_table['dexa_count_2223'] = nhs_trusts_table['dexa_count_2223'].replace(np.nan, 0)
nhs_trusts_table['dexa_count_2324'] = nhs_trusts_table['dexa_count_2324'].replace(np.nan, 0)
nhs_trusts_table['dexa_count_2425'] = nhs_trusts_table['dexa_count_2425'].replace(np.nan, 0)

st.write("NHS Trusts table with DEXA data")
nhs_trusts_table    

st.write('After adding DEXA data', nhs_trusts_table.shape)

#Count number of dexa scanners in each year
st.write('dexa_count_2223 = ', nhs_trusts_table['dexa_count_2223'].sum())
st.write('dexa_count_2324 = ', nhs_trusts_table['dexa_count_2324'].sum())
st.write('dexa_count_2425 = ', nhs_trusts_table['dexa_count_2425'].sum())

#nhs_trusts_table = dl.merge_data(fls_list_2024, nhs_trusts_table, 'nhs_trust_name', 'nhs_trust', 'fls_service_unit', {})
#nhs_trusts_table['fls_count'] = np.where(nhs_trusts_table['fls_service_unit'].notnull(), 1, nhs_trusts_table['fls_service_unit'])
#nhs_trusts_table = nhs_trusts_table.groupby(['nhs_trust_name', 'acute', 'non_acute', 'ambulance_trust', 'closed_disbanded_merged', 'dexa_count_2223', 'dexa_count_2324', 'dexa_count_2425']).agg(fls_total=('fls_count','sum')).reset_index()

#st.write('After adding FLS data', nhs_trusts_table.shape)

#nhs_trusts_table = dl.merge_data(cdcs, nhs_trusts_table, 'nhs_trust_name', 'updated_nhs_trust_name', 'name_of_cdc', {})
#nhs_trusts_table['cdc_count'] = np.where(nhs_trusts_table['name_of_cdc'].notnull(), 1, nhs_trusts_table['name_of_cdc'])
#nhs_trusts_table = nhs_trusts_table.groupby(['nhs_trust_name', 'acute', 'non_acute', 'ambulance_trust', 'closed_disbanded_merged', 'dexa_count_2223', 'dexa_count_2324', 'dexa_count_2425', 'fls_total']).agg(cdc_total=('cdc_count','sum')).reset_index()

#st.write('After adding CDC data', nhs_trusts_table.shape)

#nhs_trusts_table = dl.merge_data(nh_areas, nhs_trusts_table, 'nhs_trust_name', 'associated_trust_1', 'nnhip_places', {'nnhip_places':'nnhip_places_1'})
#nhs_trusts_table = dl.merge_data(nh_areas, nhs_trusts_table, 'nhs_trust_name', 'associated_trust_2', 'nnhip_places', {'nnhip_places':'nnhip_places_2'})
#nhs_trusts_table = dl.merge_data(nh_areas, nhs_trusts_table, 'nhs_trust_name', 'associated_trust_3', 'nnhip_places', {'nnhip_places':'nnhip_places_3'})

#nhs_trusts_table['nnhip_count_1'] = np.where(nhs_trusts_table['nnhip_places_1'].notnull(), 1, 0)
#nhs_trusts_table['nnhip_count_2'] = np.where(nhs_trusts_table['nnhip_places_2'].notnull(), 1, 0)
#nhs_trusts_table['nnhip_count_3'] = np.where(nhs_trusts_table['nnhip_places_3'].notnull(), 1, 0)

#nhs_trusts_table['nnhip_count'] = nhs_trusts_table['nnhip_count_1'] + nhs_trusts_table['nnhip_count_2'] + nhs_trusts_table['nnhip_count_3']
#nhs_trusts_table = nhs_trusts_table.groupby(['nhs_trust_name', 'acute', 'non_acute', 'ambulance_trust', 'closed_disbanded_merged', 'dexa_count_2223', 'dexa_count_2324', 'dexa_count_2425', 'fls_total', 'cdc_total']).agg(nnhip_total=('nnhip_count','sum')).reset_index()

#st.write('After adding NNHIP data', nhs_trusts_table.shape)

#st.write(trust_ics_region_mapping.columns)

#nhs_trusts_table = nhs_trusts_table.merge(trust_ics_region_mapping[['trust_name','ics', 'region']], left_on='nhs_trust_name', right_on='trust_name', how='left')
#nhs_trusts_table = nhs_trusts_table.drop(columns=['trust_name'])

#st.write('After adding ICSs and regions', nhs_trusts_table.shape)

st.write("NHS Trusts table")
nhs_trusts_table

nhs_trusts_table.to_csv('Outputs/nhs_trusts_table.csv', index=False, encoding='utf-8-sig')

#Check totals

st.write('dexa_count_2223 = ', nhs_trusts_table['dexa_count_2223'].sum())
st.write('dexa_count_2324 = ', nhs_trusts_table['dexa_count_2324'].sum())
st.write('dexa_count_2425 = ', nhs_trusts_table['dexa_count_2425'].sum())
#st.write('fls_total = ', nhs_trusts_table['fls_total'].sum())
#st.write('cdc_total = ', nhs_trusts_table['cdc_total'].sum())
#st.write('nnhip_total = ', nhs_trusts_table['nnhip_total'].sum())


regions_table = nhs_trusts_table.groupby(['region']).agg(dexa_count_2223=('dexa_count_2223','sum'), dexa_count_2324=('dexa_count_2324','sum'), dexa_count_2425=('dexa_count_2425','sum'), fls_total=('fls_total','sum'), cdc_total=('cdc_total','sum') ).reset_index()

st.write("Regions table")
regions_table

#Check regional totals

st.write('dexa_count_2223 = ', regions_table['dexa_count_2223'].sum())
st.write('dexa_count_2324 = ', regions_table['dexa_count_2324'].sum())
st.write('dexa_count_2425 = ', regions_table['dexa_count_2425'].sum())
#st.write('fls_total = ', regions_table['fls_total'].sum())
st.write('cdc_total = ', regions_table['cdc_total'].sum())
#st.write('nnhip_total = ', regions_table['nnhip_total'].sum())