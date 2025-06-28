import requests
import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("acled_collect")

def main():

    logger.info("[acled_collect] Running... ")

    #access env variables
    key = os.getenv('ACLED_API_KEY')
    email = os.getenv('ACLED_API_EMAIL')
    config = load_config()
    
    url = config.get("acled_url")

    # set variables - begin
    start_date = "2025-05-01"
    end_date = "2026-01-01"
    # set variables - end

    #per_page = 5000 - API default/fixed value, can't be changed
    page = 1
    df = pd.DataFrame()

    try:

        while True:
                
            # API endpoint and parameters
            #url = "https://api.acleddata.com/acled/read"
            params = {
                "key": key,
                "email": email,
                "page": page,
                "event_date": start_date+"|"+end_date,
                "event_date_where": "BETWEEN"
            }

            # Make the API request
            response = requests.get(url, params=params, stream=True)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()

                # Extract the status attribute as the response.status_code do not cover all error messages
                if data["status"] != 200:
                    print("API request failed with status code "+str(data["status"])+": "+response.text)
                    break
                
                # Extract the data attribute 
                if "data" in data:
                    results = data["data"]
                    
                    # Convert the results array into a DataFrame
                    df_paging = pd.DataFrame(results)

                    # Break the loop if no items are returned
                    if len(df_paging) == 0:
                        break

                    dtype_dict = {
                        "event_id_cnty": "string",
                        "event_date": "datetime64[ns]",
                        "year": "int",
                        "time_precision": "int",
                        "disorder_type": "string",
                        "event_type": "string",
                        "sub_event_type": "string",
                        "actor1": "string",
                        "assoc_actor_1": "string",
                        "inter1": "string",
                        "actor2": "string",
                        "assoc_actor_2": "string",
                        "inter2": "string",
                        "interaction": "string",
                        "civilian_targeting": "string",
                        "iso": "int",
                        "region": "string",
                        "country": "string",
                        "admin1": "string",
                        "admin2": "string",
                        "admin3": "string",
                        "location": "string",
                        "latitude": "float", 
                        "longitude": "float",
                        "geo_precision": "int",
                        "source": "string",
                        "source_scale": "string",
                        "notes": "string",
                        "fatalities": "int",
                        "tags": "string",
                        "timestamp": "string",
                    }
                    
                    # convert df data types into data dictionary types
                    df_paging = df_paging.astype(dtype_dict)

                    # merge df pagings
                    df = pd.concat([df, df_paging], ignore_index=True)

                    #print("page: "+str(page)+" - number of rows: "+str(len(df_paging)))

                else:
                    print("The 'data' attribute was not found in the response.")
                    break
            else:
                print("API request failed with status code {response.status_code}: {response.text}")
                break

            # Move to the next page
            page += 1

    except Exception as e:
    #except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")

    finally:
        if not df.empty:
            # Concatenate all partial chunks into a single DataFrame
            #df = pd.concat(partial_data, ignore_index=True)
            #df.to_csv("partial_dataset.csv", index=False)
            logger.info("Total number of rows in the dataframe: "+str(len(df)))
            logger.info("Total memory used by the dataframe: "+str(df.memory_usage(deep=True).sum() / (1024**2))+"  MB")  # in MB

            df.to_csv("data/ACLED/raw_acled_data_"+start_date+"_"+end_date+".csv")
        else:
            print("No data collected.")
        
        logger.info("[acled_collect] finshed successfully ")
