
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.options import Options
import os
import glob
from dotenv import load_dotenv
from pathlib import Path
from utils.logger import get_logger
from utils.config_loader import load_config

logger = get_logger("em_dat_collect")

def main():
    #debug = os.getenv("DEBUG")
    #print(f"[em_dat_collect] Running... Debug mode is {'on' if debug == 'True' else 'off'}")
    logger.info("[em_dat_collect] Running... ")

    #env_path = Path('..') / '.env'
    #load_dotenv(dotenv_path=env_path)

    #access the variables
    username = os.getenv('EM_DAT_USER') #EM_DAT_USER
    password = os.getenv('EM_DAT_PASSWD')
    #url = os.getenv('EM_DAT_URL')

    config = load_config()
    
    url = config.get("em_dat_url")

    #download_dir = os.path.join(os.getcwd())  # or any path you want
    download_dir = os.path.join(os.getcwd(), "data/EM-DAT/")

    # Create the directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--headless=new")  # for latest Chrome

    # Create a Service object and pass it to Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Go to the login page
    driver.get(url)

    wait = WebDriverWait(driver, 10)  # 10 seconds timeout

    # Wait for and fill in username
    username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    username_input.send_keys(username)

    # Wait for and fill in password
    password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    password_input.send_keys(password)

    # Wait for and click the login button
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-btn.css-b8z9rn.ant-btn-primary")))
    login_button.click()

    # Step 2: Enter credentials
    #driver.find_element(By.ID, "username").send_keys(username)
    #driver.find_element(By.ID, "password").send_keys(password)
    #driver.find_element(By.CLASS_NAME, "ant-btn.css-b8z9rn.ant-btn-primary").click()

    # Wait and go to "Access Data" area
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Access Data"))
    ).click()

    # Apply filters (example: check a box, select from dropdown, etc.)
    # This part varies depending on the site structure
    #WebDriverWait(driver, 10).until(
    #    EC.presence_of_element_located((By.ID, "filter-checkbox"))
    #).click()

    # Click download button
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME , "ant-btn.css-b8z9rn.ant-btn-primary"))
    ).click()

    # Wait for download to complete
    time.sleep(5)

    # Optional: Close browser
    driver.quit()

    list_of_files = glob.glob(os.path.join(download_dir, '*'))
    latest_file = max(list_of_files, key=os.path.getctime)

    # Rename the latest file
    os.rename(latest_file, os.path.join(download_dir, "raw_em_dat.xlsx"))

    #Raw/Bronze file saved for later clean up process

    logger.info("[em_dat_collect] finshed successfully ")