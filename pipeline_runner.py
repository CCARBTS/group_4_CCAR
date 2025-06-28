import os
from dotenv import load_dotenv
from utils.logger import get_logger
import importlib.util
import yaml
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load env variables
load_dotenv()

logger = get_logger("pipeline")

# load config.yaml
with open("conf/config.yaml") as f:
    config = yaml.safe_load(f)

# Import scripts dynamically
def import_script(path, function_name="main"):
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    return getattr(module, function_name)

def run_pipeline():
    logger.info("Starting pipeline")

    try:

        hdi_collect_main = import_script("script/HDI/hdi_collect.py")
        em_data_collect_main = import_script("script/EM-DAT/em_dat_collect.py")
        acled_collect_main = import_script("script/ACLED/acled_collect.py")

        hdi_prepare_main = import_script("script/HDI/hdi_prepare.py")
        em_data_prepare_main = import_script("script/EM-DAT/em_dat_prepare.py")
        acled_prepare_main = import_script("script/ACLED/acled_prepare.py")

        ccar_merge_main = import_script("script/ccar_merge.py")

        ccar_model_main = import_script("script/ccar_model.py")

        ccar_load_db = import_script("script/ccar_load_db.py")

        logger.info("=============== start data collection ===============")
        hdi_collect_main()
        em_data_collect_main()
        acled_collect_main()
        logger.info("=============== finished data collection ===============")

        logger.info("=============== start data preparation ===============")
        hdi_prepare_main()
        em_data_prepare_main()
        acled_prepare_main()
        logger.info("=============== finished data preparation ===============")

        logger.info("=============== start data merging ===============")
        ccar_merge_main()
        logger.info("=============== finished data merging ===============")

        logger.info("=============== start data modeling ===============")
        ccar_model_main()
        logger.info("=============== finished data modeling ===============")

        logger.info("=============== start data load to db ===============")
        ccar_load_db()
        logger.info("=============== finished data load to db ===============")

        logger.info("finshed successfully")

    except Exception as e:

        logger.exception("An error occurred during pipeline execution")
    
    

if __name__ == "__main__":
    run_pipeline()

