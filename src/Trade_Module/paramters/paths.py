from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def init_path(folder):
    folder.mkdir(parents=True, exist_ok=True)

PACKAGEDIR = Path(__file__).parent.parent

INPUT_PATH = PACKAGEDIR / Path(r"data/input/")
BACI_FILE = "BACI_DATA_as_vector.parquet"
BITRADEPATH = INPUT_PATH / BACI_FILE

OUTPUT_PATH = PACKAGEDIR / Path(r"data/output/")
LOG_PATH = PACKAGEDIR / Path(r"data/output/logs/")
init_path(OUTPUT_PATH)
init_path(LOG_PATH)

LOG_PATH = LOG_PATH / Path(f"{timestamp}.log")
