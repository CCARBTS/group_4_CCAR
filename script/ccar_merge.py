
import pandas as pd
import numpy as np
from utils.logger import get_logger

logger = get_logger("ccar_merge")

def main():

    logger.info("[ccar_merge] Running... ")

    df_acled = pd.read_csv('data/ACLED/cleaned_acled.csv')
    df_emdat = pd.read_csv('data/EM-DAT/cleaned_em_dat.csv')
    df_hdi   = pd.read_csv('data/HDI/cleaned_hdi.csv')
    df_iso_countries = pd.read_csv('data/countries_iso_codes.csv')

    df_acled['event_date'] = pd.to_datetime(df_acled['event_date'], errors='coerce')
    df_acled['week_number'] = df_acled['event_date'].dt.isocalendar().week

    #weekly conflict_data dataset grouped by country, event_type, number of fatalities and number of events
    conflict_data = df_acled.groupby(['year', 'week_number', 'iso', 'country', 'event_type']).agg(
        num_deaths_conflict=('fatalities', 'sum'),   # Sum of 'value'
        num_conflicts=('event_id_cnty', 'count') # Count of events
    ).reset_index()

    # First, normalize the event_type values to clean column names
    conflict_data['event_type_clean'] = conflict_data['event_type'].str.lower().str.replace(r'[^a-z0-9]+', '_', regex=True)

    # Pivot deaths
    deaths_pivot = conflict_data.pivot_table(
        index=['year', 'week_number', 'iso', 'country'],
        columns='event_type_clean',
        values='num_deaths_conflict',
        aggfunc='sum'
    ).add_prefix('num_deaths_')

    # Pivot conflicts
    conflicts_pivot = conflict_data.pivot_table(
        index=['year', 'week_number', 'iso', 'country'],
        columns='event_type_clean',
        values='num_conflicts',
        aggfunc='sum'
    ).add_prefix('num_conflicts_')

    # Combine them
    df_conflict = pd.concat([deaths_pivot, conflicts_pivot], axis=1).reset_index()

    df_conflict.fillna(0, inplace=True)


    # Combine into datetime
    df_emdat['Start Month'] = df_emdat['Start Month'].astype('Int64')
    df_emdat['Start Day'] = df_emdat['Start Day'].astype('Int64')
    df_emdat['Start Year'] = df_emdat['Start Year'].astype('Int64')
    df_emdat['start_date'] = pd.to_datetime(
        df_emdat[['Start Year', 'Start Month', 'Start Day']].rename(
            columns={'Start Year': 'year', 'Start Month': 'month', 'Start Day': 'day'}
        ),
        errors='coerce'
    )

    # Combine into datetime
    df_emdat['End Month'] = df_emdat['End Month'].astype('Int64')
    df_emdat['End Day'] = df_emdat['End Day'].astype('Int64')
    df_emdat['End Year'] = df_emdat['End Year'].astype('Int64')
    df_emdat['end_date'] = pd.to_datetime(
        df_emdat[['End Year', 'End Month', 'End Day']].rename(
            columns={'End Year': 'year', 'End Month': 'month', 'End Day': 'day'}
        ),
        errors='coerce'
    )

    df_emdat['start_date'] = df_emdat['start_date'].fillna(df_emdat['end_date'])

    # Extract week number
    df_emdat['week_number'] = df_emdat['start_date'].dt.isocalendar().week

    #weekly disaster_data dataset grouped by country, disaster_type, number of fatalities and number of events
    disaster_data = df_emdat.groupby(['week_number', 'Start Year', 'ISO', 'Country']).agg(
        num_disaster=('week_number', 'count'), # Count of events
        num_deaths_disaster=('Total Deaths', 'sum'),   # Sum of 'value'
        num_injured_disaster=("No. Injured", 'sum'),
        num_affected_disaster=("No. Affected", 'sum')
    ).reset_index()

    disaster_data = disaster_data.rename(columns={"Start Year": "year", "Country": "country"})

    df_conflict = pd.merge(df_conflict, df_iso_countries, on=['iso'], how='left')

    df_conflict = df_conflict.drop(columns=["iso"])

    df_conflict = df_conflict.drop(columns=["Country"])

    df_conflict = df_conflict.rename(columns={"Alpha_3": "ISO"})

    # Merge datasets
    df_merged = pd.merge(
        df_conflict,
        disaster_data,
        on=['year', 'week_number', 'ISO'],
        how='outer'
    )

    df_merged['country_x'] = df_merged['country_x'].fillna(df_merged['country_y'])

    df_merged = df_merged.rename(columns={"country_x": "country"})

    df_merged = df_merged.drop(columns=["country_y"])


    df_hdi = df_hdi.rename(columns={"iso": "ISO"})
    df_hdi = df_hdi.drop(columns=["country"])


    #merge with hdi
    df_merged = pd.merge(df_merged, df_hdi, on=['year', 'ISO'], how='left')

    df_merged = df_merged.dropna(subset=['ISO'])

    df_merged.drop('ISO', axis=1, inplace=True)

    df_merged = df_merged.fillna(0)

    #scale disaster columns
    #df_merged['num_injured_disaster1'] = np.log1p(df_merged['num_injured_disaster'])
    #df_merged['num_affected_disaster1'] = np.log1p(df_merged['num_affected_disaster'])
    #df_merged['num_deaths_disaster1'] = np.log1p(df_merged['num_deaths_disaster'])

    #df_merged['num_injured_disaster'] = df_merged['num_injured_disaster1']
    #df_merged['num_affected_disaster'] = df_merged['num_affected_disaster1']
    #df_merged['num_deaths_disaster'] = df_merged['num_deaths_disaster1']

    #df_merged.drop('num_injured_disaster1', axis=1, inplace=True)
    #df_merged.drop('num_affected_disaster1', axis=1, inplace=True)
    #df_merged.drop('num_deaths_disaster1', axis=1, inplace=True)


    df_merged.to_csv('data/ccar_merged.csv', index=False)

    logger.info("[ccar_merge] finshed successfully ")