from pathlib import Path

def init_path(folder):
    folder.mkdir(parents=True, exist_ok=True)

PACKAGEDIR = Path(__file__).parent.parent

INPUT_PATH = PACKAGEDIR / Path(r"data/input/")

OUTPUT_PATH = PACKAGEDIR / Path(r"data/output/")
init_path(OUTPUT_PATH)
