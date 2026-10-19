from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def init_path(folder):
    folder.mkdir(parents=True, exist_ok=True)

PACKAGEDIR = Path(__file__).parent.parent

INPUT_DATA_PATH = Path(r"data/input/")
CONFIG_PATH = PACKAGEDIR / Path(r"config/user_config.yml")
BACI_FILE = "BACI_DATA_as_vector.parquet"

OUTPUT_PATH = Path(r"data/output/")
LOG_PATH = Path(r"data/output/logs/")

LOG_PATH = LOG_PATH / Path(f"{timestamp}.log")
