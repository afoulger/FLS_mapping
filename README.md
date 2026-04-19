# FLS_mapping

## Project summary
I have produced a map to visualise the locations of DEXA scanners and Community Diagnostic Centres in England. The map can show either Regional or Integrated Care Board (ICB) boundaries and these are coloured based on the number of DEXA scanners per million people. The Community Diagnostic Centres (CDCs) and locations of NHS Trusts are shown as dots on the map.  

## Purpose of project
I have completed this project for the Data Science Accelerator 2026. I used geopandas and pydeck to create my map and streamlit to create a web app. My aim was to make it easy to visualise the locations of key facilites relating to musculoskeletal health, in order to identify areas of the country with less access to facilities. I do not have specific locations of DEXA scanners but do have a count of the number of scanners in each NHS Trust, which I have aggregated to ICB and Regional level. These counts can be seen by hovering over each Region or ICB. The map is coloured based on the number of DEXA scanners per million population. I have postcodes for CDCs and NHS Trusts so these are shown as dots on the map. The user can select the ICB or Regional view and can select whether to show CDCs and/or NHS Trusts. 

## Note on datasets
All datasets are publicly available. 

DEXA scanners data available from: https://www.england.nhs.uk/statistics/statistical-work-areas/diagnostic-imaging-dataset/national-imaging-data-collection/ 

NHS Trusts, ICB, Regional and CDC data available from: https://www.odsdatasearchandexport.nhs.uk/

Geographic boundaries data available from: https://geoportal.statistics.gov.uk/

ICB population data available here: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/clinicalcommissioninggroupmidyearpopulationestimates

## Link to web app
https://flsmapping.streamlit.app/

## Contact details
anne.foulger@dhsc.gov.uk
