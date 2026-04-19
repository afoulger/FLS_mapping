import streamlit as st
import pandas as pd
import numpy as np
import re

def load_dexa_data(df_name, skiprows):
   
       #Identify which columns are needed
       dexa_data_cols = ['Region Code', 'Region', 'ICB - Integrated Care Board',
       'Imaging Network', 'Organisation Code', 'Organisation Name',' DEXA ']
       
       #Load data 
       df = grab_clean_df(df_name, skiprows, dexa_data_cols)
       
       #Rename columns
       df = df.rename(columns = {'icb_integrated_care_board':'icb', 'organisation_code': 'dexa_trust_code', 'organisation_name':'org_name', 'dexa':'dexa_count'})
    
       #Remove blank rows at the bottom  
       df = df.loc[df['region'].notnull()] 

       #Change dexa_count column to numeric and change null values to zeroes for consistency
       df['dexa_count'] = pd.to_numeric(df['dexa_count'], errors='coerce')
       df['dexa_count'] = df['dexa_count'].replace(np.nan, 0)

       dexa_count_2425 = df['dexa_count'].sum()

       return df, dexa_count_2425

def load_cdc_data(filepath):
       
       cdcs = grab_clean_df(filepath, skiprows=1)
       cdcs['host_trust'] = cdcs['host_trust'].str.strip()

       return cdcs

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


def load_regions_data(filepath): 
       #Add regions data
       regions_data = grab_clean_df(filepath)
       regions_data = regions_data[['organisation_code', 'name', 'open_date', 'close_date', 'lat', 'lon']]
       regions_data = regions_data.rename(columns = {'organisation_code':'region_code','name':'region_name'})

       regions_data = regions_data[regions_data.region_name.str.contains('COMMISSIONING REGION')]
       regions_data['region_name'] = regions_data['region_name'].str.split(' COMMISSIONING').str[0]
       regions_data = regions_data[regions_data['close_date'].isnull()].reset_index()
       regions_data = regions_data[regions_data['open_date'] < 20260401].reset_index()
       regions_data = regions_data.drop(columns = ['index', 'level_0'])

       return regions_data

def load_icbs_data(filepath):
   
       #Add ICBs data
       icbs_data = grab_clean_df(filepath)
       icbs_data = icbs_data[['national_grouping', 'high_level_health_geography', 'name','address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'postcode', 'open_date', 'close_date', 'lat', 'lon']]
       icbs_data = icbs_data.rename(columns = {'national_grouping':'region_code','high_level_health_geography':'icb_code', 'name':'icb_name'})

       icbs_data = icbs_data[icbs_data.icb_name.str.contains(' ICB ')]
       icbs_data = icbs_data[icbs_data['close_date'].isnull()].reset_index()
       icbs_data = icbs_data[icbs_data['open_date'] < 20260401].reset_index()
       icbs_data = icbs_data.drop(columns = ['index', 'level_0'])

       icbs_summary = icbs_data[['region_code', 'icb_code', 'icb_name']]
       icbs_summary['icb_name'] = icbs_summary['icb_name'].str.split(' -').str[0]
       icbs_summary = pd.DataFrame(icbs_summary)  #check this
       icbs_summary = icbs_summary.drop_duplicates().reset_index()
       icbs_summary = icbs_summary.drop(columns = ['index'])

       return icbs_data, icbs_summary

def load_icbs_code_mapping(filepath):
       icbs_code_mapping = grab_clean_df(filepath)
       icbs_code_mapping = icbs_code_mapping[['icb24cd', 'icb24cdh']].drop_duplicates()

       return icbs_code_mapping

def load_icb_pop(filepath):
       icb_pop = grab_clean_df(filepath)
       icb_pop = icb_pop.rename(columns = {'total':'total_icb_pop'})
       icb_pop['total_icb_pop'] = icb_pop['total_icb_pop'].str.replace(',','')
       icb_pop['total_icb_pop'] = icb_pop['total_icb_pop'].apply(pd.to_numeric, errors='coerce')
       
       return icb_pop

def create_icb_pop_agg(icb_pop):
       icb_pop_agg = icb_pop.groupby(['icb_2024_code']).agg(total_icb_pop=('total_icb_pop', 'sum')).reset_index()

       return icb_pop_agg

def load_nhs_trusts_data(filepath):

       #Add NHS Trusts data
       nhs_trusts_data = grab_clean_df(filepath)
       nhs_trusts_data = nhs_trusts_data[['organisation_code', 'name', 'national_grouping', 'high_level_health_geography','address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'postcode', 'open_date', 'close_date', 'lat', 'lon']]
       nhs_trusts_data = nhs_trusts_data.rename(columns = {'organisation_code':'trust_code','name':'trust_name', 'national_grouping':'region_code', 'high_level_health_geography':'icb_code'})

       nhs_trusts_data = nhs_trusts_data[nhs_trusts_data['close_date'].isnull()].reset_index()
       nhs_trusts_data = nhs_trusts_data[nhs_trusts_data['open_date'] < 20260401].reset_index()
       nhs_trusts_data = nhs_trusts_data.drop(columns = ['index', 'level_0'])

       return nhs_trusts_data

def create_trust_level_cdc_data(cdcs):

       #Create Trust level CDCs dataset
       cdcs['cdc_count'] = 1
       cdcs_trust_level = cdcs.groupby(['updated_nhs_trust_name','cdc_trust_code']).agg(cdc_count=('cdc_count','sum')).reset_index()

       return cdcs_trust_level


def create_nhs_trusts_table(nhs_trusts_data, dexa_data_2425, cdcs_trust_level):
       #Create NHS Trusts level table

       nhs_trusts_table = nhs_trusts_data
       nhs_trusts_table = merge_data(dexa_data_2425, nhs_trusts_table, 'trust_code', 'dexa_trust_code', 'dexa_count',{'dexa_count':'dexa_count_2425'})

       #Replace nulls with zeroes
       nhs_trusts_table['dexa_count_2425'] = nhs_trusts_table['dexa_count_2425'].replace(np.nan, 0)

       nhs_trusts_table = merge_data(cdcs_trust_level, nhs_trusts_table, 'trust_code', 'cdc_trust_code', 'cdc_count', {})
       nhs_trusts_table['cdc_count'] = nhs_trusts_table['cdc_count'].replace(np.nan, 0)

       nhs_trusts_table.to_csv('Outputs/nhs_trusts_table.csv', index=False, encoding='utf-8-sig')

       return nhs_trusts_table


def create_icb_level_table(nhs_trusts_table, icbs_summary):

       #Create ICB level table

       #Aggregate the NHS Trusts table to ICB level
       icb_level_summary = nhs_trusts_table.groupby(['icb_code']).agg(dexa_count_2425=('dexa_count_2425', 'sum'), cdc_count=('cdc_count','sum')).reset_index()

       #Merge this onto the original regions data to create regions table
       icbs_summary = icbs_summary.merge(icb_level_summary, on='icb_code', how='left')

       #Save output file
       icbs_summary.to_csv('Outputs/icbs_summary.csv', index=False, encoding='utf-8-sig')

       return icb_level_summary, icbs_summary


def create_region_level_table(nhs_trusts_table, regions_data):
       #Create Region level table

       #Aggregate the NHS Trusts table to region level
       regions_summary = nhs_trusts_table.groupby(['region_code']).agg(dexa_count_2425=('dexa_count_2425', 'sum'), cdc_count=('cdc_count','sum')).reset_index()

       #Merge this onto the original regions data to create regions table
       regions_data = regions_data.merge(regions_summary, on='region_code', how='left')

       return regions_summary, regions_data