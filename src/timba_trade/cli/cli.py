import click
import pandas as pd
from pathlib import Path

from timba_trade.main import main
from timba_trade.paramters.paths import default_paths


@click.group()
def cli():
    """CLI of the TiMBA Trade module."""
    pass

@cli.command("run")

@click.option(
    '-S', '--save_file', 
    default=True, 
    show_default=True, 
    required=False,
    help="If True output will be saved as parquet file."
)

@click.option(
    '-ID', '--input_dir', 
    required=False, 
    type=click.Path(
        file_okay=False, 
        writable=True, 
        path_type=Path
    ), 
    default=None,
    help="Path to the data directory containing the Input folder. If omitted, the data directory inside the package directory is used."
)

@click.option(
    '-OD', '--output_dir', 
    required=False, 
    type=click.Path(
        file_okay=False, 
        writable=True, 
        path_type=Path
    ), 
    default=None,
    help="Path to the data directory containing the Output folder. If omitted, the data directory inside the package directory is used."
)

@click.option(
    '-BN', '--baci_file_name', 
    required=False, 
    type=click.Path(
        file_okay=False, 
        writable=True, 
        path_type=Path
    ), 
    default=None,
    help="Name of the BACI file. If omitted, the default name inside the package is used."
)

def run(save_file:bool, input_dir:Path, output_dir:Path, baci_file_name:Path):
    """Run the main script."""
    default_paths["SCENARIO_DIR"] = input_dir
    default_paths["OUTPUT_DIR"] = output_dir
    default_paths["baci_file_name"] = baci_file_name

    res = main(
        save_file=save_file,
        path_dict=default_paths,
    )
    print("\nBilateral trade restults sorted:")
    res = res.sort_values(by="Export_bilateral",ascending=False)
    print(res.head(10))