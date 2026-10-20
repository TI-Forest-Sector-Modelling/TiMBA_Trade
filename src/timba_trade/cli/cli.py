import click
import pandas as pd
from pathlib import Path

from timba_trade.main import main


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
    '-P', '--folder_path', 'folder_path', 
    required=False, 
    type=click.Path(
        file_okay=False, 
        writable=True, 
        path_type=Path
    ), 
    default=None,
    help="Path to the data directory containing the Input and Output folders. If omitted, the data directory inside the package directory is used."
)

def run(save_file:bool, folder_path:Path):
    """Run the main script."""
    res = main(
        timba_data=None, 
        scen_name=None,
        save_file=save_file,
        folder_path=folder_path,
    )
