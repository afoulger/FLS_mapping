import streamlit as st
import pandas as pd
import numpy as np
import re

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