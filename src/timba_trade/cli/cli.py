import click
import pandas as pd

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
    required=True,
    help="If True output will be saved as parquet file."
)

def bitrade(save_file:bool):
    """Download ISIMIP data for a model."""
    res = main(
        timba_data=None, 
        save_file=save_file,
    )
