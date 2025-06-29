# utils/config_loader.py
import yaml
import os

def load_config(config_path="conf/config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
