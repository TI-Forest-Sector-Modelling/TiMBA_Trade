![TiMBA Trade Logo](https://github.com/TI-Forest-Sector-Modelling/TiMBA_Additional_Information/blob/main/images/timba_trade_assets/timba_trade_logo.png?raw=true)  

-----------------

# Bilateral Trade Module of TiMBA

This is an additional module for TiMBA that computes bilateral trade flows per commodity and balances them to the export and import totals. BACI trade data serves as the starting point for bilateral trade; the balancing is done with **RAS** (iterative proportional fitting).

## Workflow

1. **TiMBA** provides the total export and import targets of each country   and a growth factor for bilateral trade, based on price developments in both countries.
2. The **BACI** database provides the initial information on bilateral exports.
3. The **RAS** method scales rows and columns alternately until row sums = export targets and column sums = import targets.
4. This process is repeated **recursively**, with each period building on the previous result, until all TiMBA periods are processed.
5. The results are returned as a pandas DataFrame or, if the saving flag is activated, saved as a Parquet file.

## Notes

- Within the RAS process, an additional **RoW** (Rest of World) node is added to account for countries that are not represented in TiMBA.
- Countries with a target but no observed trade are moved to RoW.
- RoW absorbs any difference between total exports and total imports.
- RAS settings can be changed in `src/Trade_Module/config/user_config.yml`.

## Run

The module can be executed in two ways:

1. **Run the module directly** from the repository root:

   ```bash
   python -m src.timba_trade.main
   ```

## 2. Run the Module via the Command-Line Interface (CLI)

After installing the package, you can run the trade module directly from the command line:

```bash
trade_module run
```

The CLI supports the following optional arguments:

- `-S` / `--save_file`: Controls whether the output is saved as a Parquet file. Defaults to `True`.
- `-P` / `--folder_path`: Specifies the directory containing the input data. The output files and logs are also saved to this directory.

**Example:**

```bash
trade_module run -S True -P "C:\your_data_folder"
```

**Default behavior:**

- If `--save_file` is omitted, the output is automatically saved as a Parquet file.
- If `--folder_path` is omitted, the module uses its package directory as the default location for input data, output files, and logs.

**Note:** Replace `C:\your_data_folder` with the path to your actual data directory.

## Expected folder structure

The specified `folder_path` must contain the following files in the indicated directory structure:

```text
your_data_folder/
├── data/
│   └── input/
│       └── BACI_DATA_as_vector.parquet
│       └── timba_result.pkl
```


## Logging

The module writes a log file for debugging to `src/Trade_Module/data/output/logs` (`LOG_PATH`). The console shows `INFO`; the log file additionally contains `DEBUG` details.
