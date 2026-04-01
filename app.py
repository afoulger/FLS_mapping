import streamlit as st
import pandas as pd
import numpy as np
import re
import data_loading as dl


st.title("My FLS mapping app")
      
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


#Check counts

#dexa_count_2425 = dexa_data_2425['dexa_count'].sum()
st.write('DEXA count for 24-25 = ', dexa_count_2425)

st.write('cdc_count = ', cdcs_trust_level['cdc_count'].sum())

st.write('dexa_count_2425 = ', nhs_trusts_table['dexa_count_2425'].sum())
st.write('cdc_count = ', nhs_trusts_table['cdc_count'].sum())

#st.write('dexa_count_2425 = ', icb_level_summary['dexa_count_2425'].sum())
#st.write('cdc_count = ', icb_level_summary['cdc_count'].sum())

#st.write('dexa_count_2425 = ', icbs_summary['dexa_count_2425'].sum())
#st.write('cdc_count = ', icbs_summary['cdc_count'].sum())
       
st.write('dexa_count_2425 = ', regions_summary['dexa_count_2425'].sum())
st.write('cdc_count = ', regions_summary['cdc_count'].sum())

st.write('dexa_count_2425 = ', regions_data['dexa_count_2425'].sum())
st.write('cdc_count = ', regions_data['cdc_count'].sum())

#Display datasets on streamlit

st.write("DEXA scanner data 2024-25")
dexa_data_2425

st.write("CDCs")
cdcs

st.write("Regions_data")
st.write(regions_data)

#st.write("ICBs_data")
#st.write(icbs_data)

#st.write("ICBs_summary")
#st.write(icbs_summary)

st.write("NHS_Trusts_data")
st.write(nhs_trusts_data)
       
st.write("CDCs Trust level")
cdcs_trust_level

st.write("NHS Trusts table with DEXA and CDC data")
nhs_trusts_table    

#st.write("ICB_level_summary")
#icb_level_summary

#st.write("ICBs_data")
#icbs_summary

st.write("Regions_summary")
regions_summary

st.write("Regions_data")
regions_data