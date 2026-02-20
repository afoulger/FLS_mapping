import streamlit as st
import pandas as pd
import numpy as np
import re

st.title("My FLS mapping app")

def load_dexa_data(df_name, skiprows, usecols):
   
       #Load data 
       df = grab_clean_df(df_name, skiprows, usecols)
       
       #Rename columns
       df = df.rename(columns = {'icb_integrated_care_board':'icb', 'organisation_code': 'org_code', 'organisation_name':'org_name', 'dexa':'dexa_count'})
    
       #Remove blank rows at the bottom  
       df = df.loc[df['region'].notnull()] 

       #Note: Need to sort out null values as displayed differently in each dataset

       return df

def grab_clean_df(df_name, skiprows=None, usecols=None):
       #Load csv files and tidy up column names
       df = pd.read_csv(df_name, skiprows=skiprows, usecols=usecols)
       df = df.rename(columns=lambda x: tokenize(x))

       return df

def tokenize(text):
       #Keep all alphanumeric characters and join with underscore
       try: 
              text = re.findall(r'[a-zA-Z0-9]+', text)
              text = "_".join(text).lower()
       except:
              text = ""
       return text


#Identify which columns are needed
dexa_data_cols = ['Region Code', 'Region', 'ICB - Integrated Care Board',
       'Imaging Network', 'Organisation Code', 'Organisation Name',' DEXA ']

#Load data
dexa_data_2223 = load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2022-23-v1.csv', skiprows=13, usecols=dexa_data_cols)  
dexa_data_2324 = load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2023-24-v1.csv', skiprows=13, usecols=dexa_data_cols)  
dexa_data_2425 = load_dexa_data('Data/National-Imaging-Data-Collection-Asset-Count-2024-25-v1-FINAL.csv', skiprows=13, usecols=dexa_data_cols)  

fls_list_2024 = grab_clean_df('Data/FLS_List_2024.csv')
neighbourhood_health_areas = grab_clean_df('Data/Neighbourhood_Health_areas.csv')
nhs_trusts = grab_clean_df('Data/NHS_Trusts.csv')

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