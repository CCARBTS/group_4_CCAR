
import pandas as pd
import os
from utils.logger import get_logger

logger = get_logger("acled_prepare")

def main():

    logger.info("[acled_prepare] Running... ")

    directory = "data/ACLED/"
    start_substr = "raw_acled_data_"
    end_substr = ".csv"

    matching_files = [
        f for f in os.listdir(directory)
        if f.startswith(start_substr) and f.endswith(end_substr)
    ]

    matching_files.sort()
    df = pd.DataFrame()
    for file in matching_files:
        #print(file)
        df_file = pd.read_csv(directory+file)
        df = pd.concat([df, df_file], ignore_index=True)

    #removing features not relevant
    df = df[["iso", "country", "region", "location", "event_id_cnty", "event_date", "year", "disorder_type","event_type", "sub_event_type", "latitude", "longitude", "fatalities"]]
    
    df.to_csv('data/ACLED/cleaned_acled.csv', index=False)

    logger.info("[acled_prepare] finshed successfully ")
