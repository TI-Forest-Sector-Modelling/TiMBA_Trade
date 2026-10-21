from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def init_path(folder):
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

PACKAGEDIR = Path(__file__).parent.parent

INPUT_FOLDER = Path(r"data/input/")
CONFIG_PATH = PACKAGEDIR / Path(r"config/user_config.yml")
BACI_FILE = Path(r"BACI_DATA_as_vector.parquet")

OUTPUT_FOLDER = Path(f"data/output/")
LOG_FOLDER = Path("logs")
RESPATH = Path("data")

SCENARIO_DIR = PACKAGEDIR / INPUT_FOLDER
BACI_DIR = PACKAGEDIR / INPUT_FOLDER
LOG_DIR = PACKAGEDIR / OUTPUT_FOLDER / LOG_FOLDER
OUTPUT_DIR = PACKAGEDIR / OUTPUT_FOLDER / RESPATH

default_paths = {
    "SCENARIO_DIR": None,
    "BACI_DIR": None,
    "OUTPUT_DIR": None,
    "LOG_DIR": Path("E:/log"),
    "scen_name": None,
    "baci_file_name": None,
}
