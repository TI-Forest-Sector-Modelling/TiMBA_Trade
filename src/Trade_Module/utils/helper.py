from src.Trade_Module.paramters.hscodes import timba_commodity_list, timba_comcode

def hs_to_fao_dict(commodity_list):
    hs_to_fao_map = {
        hs_code: entry["fao_code"]
        for entry in commodity_list
        for hs_code in entry["hs02_codes"]
    }

    return dict(sorted(hs_to_fao_map.items()))