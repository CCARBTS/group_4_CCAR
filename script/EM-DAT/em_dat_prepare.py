
import pandas as pd
from utils.logger import get_logger
#from utils.config_loader import load_config

logger = get_logger("em_dat_prepare")

def main():

    logger.info("[em_dat_prepare] Running... ")

    #config = load_config()
    
    #url = config.get("em_dat_url")

    df = pd.read_excel("data/EM-DAT/raw_em_dat.xlsx")

    #Filtering relevant features (total affected = No. Affected + No. Injured, so removing to avoid colinearity)
    df = df[["ISO", "Country", "Disaster Type", "Total Deaths", "No. Injured", "No. Affected", "Start Year", "Start Month", "Start Day", "End Year", "End Month", "End Day", "Entry Date", "Last Update"]]

    # Fill Start Month with End Month if available
    df['Start Month'] = df['Start Month'].fillna(df['End Month'])

    # Fill End Month with Start Month if available
    df['End Month'] = df['End Month'].fillna(df['Start Month'])

    # Fill remaining NaNs with 1
    df['Start Month'] = df['Start Month'].fillna(1)
    df['End Month'] = df['End Month'].fillna(1)

    # Fill Start Day with End Day if available
    df['Start Day'] = df['Start Day'].fillna(df['End Day'])

    # Fill End Day with Start Day if available
    df['End Day'] = df['End Day'].fillna(df['Start Day'])

    # Fill remaining NaNs with 1
    df['Start Day'] = df['Start Day'].fillna(1)
    df['End Day'] = df['End Day'].fillna(1)

    # Define condition: all three columns are NaN
    mask = df[['Total Deaths', 'No. Injured', 'No. Affected']].isna().all(axis=1)

    # Fill only those rows with 0 in the specified columns
    df.loc[mask, ['Total Deaths', 'No. Injured', 'No. Affected']] = 0

    #Fill remaining with 0
    df['No. Injured'] = df['No. Injured'].fillna(0).astype(int)
    df['No. Affected'] = df['No. Affected'].fillna(0).astype(int)
    df['Total Deaths'] = df['Total Deaths'].fillna(0).astype(int)

    #Raw/Bronze file saved for later clean up process
    df.to_csv("data/EM-DAT/cleaned_em_dat.csv", index=False)

    logger.info("[em_dat_prepare] finshed successfully ")