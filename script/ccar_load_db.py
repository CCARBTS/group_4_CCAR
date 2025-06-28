import pandas as pd
import os
from dotenv import load_dotenv
from utils.logger import get_logger
from sqlalchemy import create_engine, text

# Load env variables
load_dotenv()

# Database connection settings
db_user = os.getenv('PG_DB_USER') #'myuser' 
db_password = os.getenv('PG_DB_PASSWORD') #'mypassword'
db_host = os.getenv('PG_DB_HOST') #'localhost'
db_port = os.getenv('PG_DB_PORT') #'5432'
db_name = os.getenv('PG_DB_NAME') #'mydatabase'
db_schema = os.getenv('PG_DB_SCHEMA') #'ccar'

#historical and prediction tables use same template
create_table_sql_template1 = """
CREATE TABLE "{schema}"."{table_name}" (
    date DATE NOT NULL,
    country TEXT NOT NULL,
    most_needs_idx DOUBLE PRECISION
);
"""

#merged table
create_table_sql_template2 = """
CREATE TABLE "{schema}"."{table_name}" (
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    country TEXT NOT NULL,
    num_deaths_battles DOUBLE PRECISION,
    num_deaths_explosions_remote_violence DOUBLE PRECISION,
    num_deaths_protests DOUBLE PRECISION,
    num_deaths_riots DOUBLE PRECISION,
    num_deaths_strategic_developments DOUBLE PRECISION,
    num_deaths_violence_against_civilians DOUBLE PRECISION,
    num_conflicts_battles DOUBLE PRECISION,
    num_conflicts_explosions_remote_violence DOUBLE PRECISION,
    num_conflicts_protests DOUBLE PRECISION,
    num_conflicts_riots DOUBLE PRECISION,
    num_conflicts_strategic_developments DOUBLE PRECISION,
    num_conflicts_violence_against_civilians DOUBLE PRECISION,
    num_disaster INTEGER,
    num_deaths_disaster DOUBLE PRECISION,
    num_injured_disaster DOUBLE PRECISION,
    num_affected_disaster DOUBLE PRECISION,
    hdi DOUBLE PRECISION
);
"""

#country and iso code table
create_table_sql_template3 = """
CREATE TABLE "{schema}"."{table_name}" (
    country TEXT NOT NULL,
    alpha_2 CHAR(2),
    alpha_3 CHAR(3) NOT NULL,
    iso INTEGER NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
"""

#HDI table
create_table_sql_template4 = """
CREATE TABLE "{schema}"."{table_name}" (
    iso CHAR(3) NOT NULL,
    country TEXT NOT NULL,
    year INTEGER NOT NULL,
    hdi DOUBLE PRECISION
);
"""

#Conflict table
create_table_sql_template5 = """
CREATE TABLE "{schema}"."{table_name}" (
    iso INTEGER NOT NULL,
    country TEXT NOT NULL,
    region TEXT,
    location TEXT,
    event_id_cnty TEXT,
    event_date DATE,
    year INTEGER,
    disorder_type TEXT,
    event_type TEXT,
    sub_event_type TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    fatalities INTEGER
);
"""

#Disaster table
create_table_sql_template6 = """
CREATE TABLE "{schema}"."{table_name}" (
    iso CHAR(3) NOT NULL,
    country TEXT NOT NULL,
    disaster_type TEXT,
    total_deaths INTEGER,
    no_injured INTEGER,
    no_affected INTEGER,
    start_year INTEGER,
    start_month INTEGER,
    start_day INTEGER,
    end_year INTEGER,
    end_month INTEGER,
    end_day INTEGER,
    entry_date DATE,
    last_update DATE
);
"""

#View Criris data
create_view_sql_template = """
CREATE OR REPLACE VIEW public.crisis_data 
AS SELECT row_number() OVER () AS id,
    m.year,
    m.week_number,
    h.date,
    m.country,
    COALESCE(m.num_deaths_battles, 0::double precision) + COALESCE(m.num_deaths_explosions_remote_violence, 0::double precision) + COALESCE(m.num_deaths_protests, 0::double precision) + COALESCE(m.num_deaths_riots, 0::double precision) + COALESCE(m.num_deaths_strategic_developments, 0::double precision) + COALESCE(m.num_deaths_violence_against_civilians, 0::double precision) AS num_deaths,
    COALESCE(m.num_deaths_disaster, 0::double precision) AS num_deaths_disasters,
    COALESCE(m.num_conflicts_battles, 0::double precision) + COALESCE(m.num_conflicts_explosions_remote_violence, 0::double precision) + COALESCE(m.num_conflicts_protests, 0::double precision) + COALESCE(m.num_conflicts_riots, 0::double precision) + COALESCE(m.num_conflicts_strategic_developments, 0::double precision) + COALESCE(m.num_conflicts_violence_against_civilians, 0::double precision) AS num_conflicts,
    COALESCE(m.num_disaster, 0) AS num_disasters,
    COALESCE(m.num_injured_disaster, 0::double precision) AS num_injured,
    COALESCE(m.num_affected_disaster, 0::double precision) AS num_affected,
    round(COALESCE(m.hdi, 0::double precision)::numeric, 3) AS hdi,
    round(h.most_needs_idx::numeric, 3) AS most_needs
   FROM public.merged m
     LEFT JOIN public.historical h ON h.country = m.country AND EXTRACT(year FROM h.date) = m.year::numeric AND EXTRACT(week FROM h.date) = m.week_number::numeric;
"""

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

logger = get_logger("ccar_load_db")


def load_csv_to_postgres(df, table_name, engine, schema, create_table_sql_template):

    full_table_name = f'"{schema}"."{table_name}"'
    
    with engine.begin() as conn:
        # Check if the table exists in the specified schema
        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = :schema_name AND table_name = :table_name
                )
            """),
            {"schema_name": schema, "table_name": table_name}
        )
        exists = result.scalar()
        
        if exists:
            logger.info(f"Table {full_table_name} exists. Truncating...")
            #print(f"Table {full_table_name} exists. Truncating...")
            conn.execute(text(f'TRUNCATE TABLE {full_table_name} RESTART IDENTITY'))
        else:
            logger.info(f"Table {full_table_name} does not exist. Creating...")
            #print(f"Table {full_table_name} does not exist. Creating...")
            create_sql = create_table_sql_template.format(schema=schema, table_name=table_name)
            conn.execute(text(create_sql))
        
        # Load the data
        df.columns = (
            df.columns
            .str.strip()          # remove leading/trailing whitespace
            .str.lower()          # lowercase all
            .str.replace(r"[.\s]+", "_", regex=True)  # replace '.' and spaces with '_'
        )
        df.to_sql(table_name, con=conn, schema=schema, if_exists='append', index=False)
        logger.info(f"Loaded data into {full_table_name}")
        #print(f"Loaded data into {full_table_name}")

        
def main():

    logger.info("[ccar_load_db] Running... ")
    #print("[ccar_load_db] Running... ")

    #df_hist = pd.read_csv('data/ccar_historical.csv')
    #df_pred = pd.read_csv('data/ccar_prediction.csv')
    df_hist = pd.read_csv('data/ccar_historical_data.csv')
    df_pred_past = pd.read_csv('data/ccar_predicted_past.csv')
    df_pred_fut = pd.read_csv('data/ccar_predicted_future.csv')
    df_merged = pd.read_csv('data/ccar_merged.csv')
    df_country = pd.read_csv('data/countries_codes_and_coordinates.csv')
    df_hdi = pd.read_csv('data/HDI/cleaned_hdi.csv')
    df_conflict = pd.read_csv('data/ACLED/cleaned_acled.csv')
    df_disaster = pd.read_csv('data/EM-DAT/cleaned_em_dat.csv')


    load_csv_to_postgres(df_hist, 'historical', engine, db_schema, create_table_sql_template1)
    #load_csv_to_postgres(df_pred, 'prediction', engine, db_schema, create_table_sql_template1)
    load_csv_to_postgres(df_pred_past, 'prediction_past', engine, db_schema, create_table_sql_template1)
    load_csv_to_postgres(df_pred_fut, 'prediction_future', engine, db_schema, create_table_sql_template1)
    load_csv_to_postgres(df_merged, 'merged', engine, db_schema, create_table_sql_template2)
    load_csv_to_postgres(df_country, 'country', engine, db_schema, create_table_sql_template3)
    load_csv_to_postgres(df_hdi, 'hdi', engine, db_schema, create_table_sql_template4)
    load_csv_to_postgres(df_conflict, 'conflict', engine, db_schema, create_table_sql_template5)
    load_csv_to_postgres(df_disaster, 'disaster', engine, db_schema, create_table_sql_template6)

    with engine.connect() as conn:
        conn.execute(text(create_view_sql_template))
        conn.commit()

    logger.info("[ccar_load_db] finshed successfully ")
    #print("[ccar_load_db] finshed successfully ")


if __name__ == "__main__":
    main()