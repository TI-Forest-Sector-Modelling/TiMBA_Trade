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

2. **Use the command-line interface (CLI)** after installing the package:

   ```bash
   trade_module run
   ```
   
   The CLI provides one optional flag, `-S` / `--save_file`. When enabled, it saves the trade module's output as a Parquet file.
   
   For example:
   ```bash
   trade_module run -S True
   ```

   If the flag is omitted, the output is saved as a Parquet file.

## Logging

The module writes a log file for debugging to `src/Trade_Module/data/output/logs` (`LOG_PATH`). The console shows `INFO`; the log file additionally contains `DEBUG` details.
