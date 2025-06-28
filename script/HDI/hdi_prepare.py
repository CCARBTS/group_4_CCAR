import os
import pandas as pd
import requests
from io import BytesIO
from utils.logger import get_logger
#from utils.config_loader import load_config

logger = get_logger("hdi_prepare")

# Function to get the first non-null value for each row
def get_min_value(row, hdi_columns):
    # Find the first non-null value in the row
    first_non_null = row[hdi_columns].first_valid_index()  # First valid (non-null) index
    if pd.notnull(first_non_null):
        return row[first_non_null]  # Return the value at the first non-null index
    return None  # If all values are NaN, return None


def main():

    #print(f"[hdi_collect] Running")
    logger.info("[hdi_prepare] Running... ")

    #config = load_config()
    
    #url = config.get("hdi_url")

    df_hdi = pd.read_csv("data/HDI/raw_hdi.csv")

    col_name = "le_1990"
    col_index = df_hdi.columns.get_loc(col_name)
    df_hdi = df_hdi.iloc[:, :col_index] # Keep all columns to the *left* of 'col_name'

    df_hdi = df_hdi.dropna(subset=['hdi_rank_2022']) #clean up unnecessary rows

    df_hdi = df_hdi.rename(columns = {'iso3' : 'iso'})  #renaming columns
    
    df_hdi = df_hdi.drop(['hdicode', 'region', 'hdi_rank_2022'], axis=1) #drop columns that will not be used

    # DataFrame and columns are in the format hdi_1990, hdi_1991, ..., hdi_2022
    hdi_columns = df_hdi.filter(regex='^hdi_').columns

    # Apply the function to each row and fill NaN values
    for index, row in df_hdi.iterrows():
        min_value = get_min_value(row, hdi_columns)  # Get the minimum non-null value for the row
        if pd.notnull(min_value):
            # Convert columns to numeric (just in case they are objects) before filling NaNs
            df_hdi.loc[index, hdi_columns] = row[hdi_columns].apply(pd.to_numeric, errors='coerce').fillna(min_value)

    # Since hdi 2023, 2024, 2025 atre not available, assume last available hdi
    df_hdi['hdi_2023'] = df_hdi['hdi_2022']
    df_hdi['hdi_2024'] = df_hdi['hdi_2022']
    df_hdi['hdi_2025'] = df_hdi['hdi_2022']

    hdi_columns = df_hdi.filter(regex='^hdi_').columns
    
    # Melt the DataFrame
    df_hdi = df_hdi.melt(
        id_vars=[col for col in df_hdi.columns if col not in hdi_columns],
        value_vars=hdi_columns,
        var_name="year",
        value_name="HDI"
    )

    # Clean the 'year' column by removing the "hdi_" prefix and converting to int
    df_hdi['year'] = df_hdi['year'].str.replace("hdi_", "").astype(int)

    # save prepared/silver file
    df_hdi.to_csv("data/HDI/cleaned_hdi.csv", index=False)

    logger.info("[hdi_prepare] finshed successfully ")