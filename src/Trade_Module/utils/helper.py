from src.Trade_Module.paramters.hscodes import timba_commodity_list, timba_comcode
from src.Trade_Module.paramters.paths import CONFIG_PATH

import yaml

def hs_to_fao_dict(commodity_list):
    hs_to_fao_map = {
        hs_code: entry["fao_code"]
        for entry in commodity_list
        for hs_code in entry["hs02_codes"]
    }

    return dict(sorted(hs_to_fao_map.items()))

def load_config() -> dict:
    """Load full YAML configuration."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_ras_parameters() -> dict:
    """Return config dict for RAS parameters"""
    config = load_config()
    print(config)
    print(config["RAS_PARAMETERS"]["cutoff"])
    print(type(config["RAS_PARAMETERS"]["cutoff"]))
    return config["RAS_PARAMETERS"]
