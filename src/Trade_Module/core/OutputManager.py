import pandas as pd
from pathlib import Path

from src.Trade_Module.paramters.paths import OUTPUT_PATH


class OutputManager:
    def __init__(self):
        pass

    def save_df(self, df:pd.DataFrame, file_name:str):
        df = df[df.Country == "DEU"]
        output_path = OUTPUT_PATH / Path(file_name + ".csv")
        df.to_csv(output_path) 