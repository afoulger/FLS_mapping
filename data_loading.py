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

       #Change dexa_count column to numeric and change null values to zeroes for consistency
       df['dexa_count'] = pd.to_numeric(df['dexa_count'], errors='coerce')
       df['dexa_count'] = df['dexa_count'].replace(np.nan, 0)

       return df

def grab_clean_df(df_name, skiprows=None, usecols=None):
       #Load csv files and tidy up column names
       df = pd.read_csv(df_name, skiprows=skiprows, usecols=usecols)
       df = df.rename(columns=lambda x: tokenize(x))
       df = pd.DataFrame(df)

       return df

def tokenize(text):
       #Keep all alphanumeric characters and join with underscore
       try: 
              text = re.findall(r'[a-zA-Z0-9]+', text)
              text = "_".join(text).lower()
       except:
              text = ""
       return text

def merge_data(df, df_orig, left_merge_col, merge_col, second_col, new_col_names_dict=None):
    
    new_table = df_orig.merge(df[[merge_col, second_col]].rename(columns = new_col_names_dict), left_on=left_merge_col, right_on=merge_col, how='left')
    new_table = new_table.drop(columns=[merge_col])

    return new_table

def update_dexa_trust_names(df, lookup_df):
       df = merge_data(lookup_df, df, 'org_name', 'dexa_data_trust_name', 'new_trust_name', new_col_names_dict={})
       df['org_name'] = np.where(df['new_trust_name'].notnull(), df['new_trust_name'], df['org_name'])
       df = df.drop(columns=['new_trust_name'])

       return df