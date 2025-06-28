import os
import pandas as pd
import requests
from io import BytesIO
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("hdi_collect")

def main():

    #print(f"[hdi_collect] Running")
    logger.info("[hdi_collect] Running... ")

    config = load_config()
    
    url = config.get("hdi_url")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError if status is 4xx or 5xx

    df_hdi = pd.read_csv(BytesIO(response.content), encoding='latin1')  # or try 'cp1252'

    # save raw/bronze file
    df_hdi.to_csv("data/HDI/raw_hdi.csv", index=False)

    logger.info("[hdi_collect] finshed successfully ")