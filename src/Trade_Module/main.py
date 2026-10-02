from src.Trade_Module.logic.CalculationManager import CalcManager
from src.Trade_Module.core.OutputManager import OutputManager
from src.Trade_Module.core.DashboardManager import Dashboard
from src.Trade_Module.core.ProcessManager import ProcessManager

from src.Trade_Module.paramters.hscodes import timba_commodity_list, timba_comcode
from src.Trade_Module.utils.helper import hs_to_fao_dict
from src.Trade_Module.utils.logger import setup_logging
from src.Trade_Module.logic.RAS import RAS

import logging
import pandas as pd

setup_logging()
logger = logging.getLogger(__name__)


def prepare_baci_data(baci_data, commodity_list):
    hs_to_fao_map = hs_to_fao_dict(commodity_list)

    data = baci_data.copy()
    data["TiMBA"] = data["HSCode"].map(hs_to_fao_map)

    return (
        data[data["Year"] == 2023]
        .dropna(subset=["TiMBA"])
        .reset_index(drop=True)
    )


def aggregate_trade_quantity(baci_data):
    return (
        baci_data
        .groupby(
            ["Year", "Reporter_Code", "Partner_Code", "TiMBA"]
        )["Quantity"]
        .sum()
        .reset_index()
    )


def create_counterflow(trade_data):
    return trade_data.rename(
        columns={
            "Reporter_Code": "Partner_Code",
            "Partner_Code": "Reporter_Code",
            "Quantity": "Import",
        }
    )


def create_bilateral_trade(trade_data):
    counterflow = create_counterflow(trade_data)

    result = trade_data.merge(
        counterflow,
        on=["Year", "Reporter_Code", "Partner_Code", "TiMBA"],
        how="outer",
    )

    result = result.rename(columns={"Quantity": "Export"})

    return (
        result
        .groupby(
            ["Year", "Reporter_Code", "Partner_Code", "TiMBA"]
        )[["Export", "Import"]]
        .sum()
        .reset_index()
    )


def calculate_exporter_totals(bilateral_trade):
    return (
        bilateral_trade
        .groupby(
            ["Year", "Reporter_Code", "TiMBA"]
        )[["Export", "Import"]]
        .sum()
        .reset_index()
    )


def calculate_importer_totals(bilateral_trade):
    importer_totals = calculate_exporter_totals(bilateral_trade)

    return importer_totals.rename(
        columns={"Reporter_Code": "Partner_Code"}
    )


def merge_trade_totals(bilateral_trade):
    exporter_totals = calculate_exporter_totals(bilateral_trade)

    total = bilateral_trade.merge(
        right=exporter_totals,
        how="outer",
        on=[
            "Year",
            "Reporter_Code",
            "TiMBA",
        ],
        suffixes=(
            "_bilateral",
            "_total_exporter",
        ),
    )

    importer_totals = calculate_importer_totals(bilateral_trade)

    total = total.merge(
        right=importer_totals,
        how="outer",
        on=[
            "Year",
            "Partner_Code",
            "TiMBA",
        ],
        suffixes=("", "_total_importer"),
    )

    return total


def prepare_bilateral_trade_shares(
    bilateral_trade,
    commodity_code_mapping,
):
    total = merge_trade_totals(bilateral_trade)

    total = total[
        [
            "Year",
            "Reporter_Code",
            "Partner_Code",
            "TiMBA",
            "Export_bilateral",
            "Import_bilateral",
            "Export_total_exporter",
            "Import_total_exporter",
            "Export",
            "Import",
        ]
    ].rename(
        columns={
            "Reporter_Code": "Reporter",
            "Partner_Code": "Partner",
            "Export": "Export_total_importer",
            "Import": "Import_total_importer",
            "TiMBA": "Commodity",
        }
    )

    total["Period"] = 0
    total["Commodity"] = total["Commodity"].map(commodity_code_mapping)

    return total


def calculate_growth_data(calc_manager):
    df = calc_manager.main().copy()

    df["P_share_growth"] = df["P_share_growth"] - 1

    price_change = create_period_pivot(
        df=df,
        value_column="P_share_growth",
    )

    return price_change


def create_period_pivot(df, value_column):
    return (
        df[
            [
                "Reporter",
                "Partner",
                "Commodity",
                "Period",
                value_column,
            ]
        ]
        .pivot_table(
            index=["Reporter", "Partner", "Commodity"],
            columns="Period",
            values=value_column,
            aggfunc="sum",
        )
        .reset_index()
    )


def save_multiple_results(output_manager,dict_to_save):
    for key, value in dict_to_save.items():
        output_manager.save_df(
            df=value,
            file_name=key,
        )


def run_dashboard(
    bilateral_trade_shares,
    price_change,
):
    dashboard = Dashboard(
        df_share=bilateral_trade_shares,
        df_growth=price_change,
        top=5,
    )

    dashboard.run()

def main():
    # calc_manager = CalcManager()
    # output_manager = OutputManager()
    pm = ProcessManager()

    pm.load_timba_process()

    # baci_data = prepare_baci_data(
    #     baci_data=load_baci_data(),
    #     commodity_list=timba_commodity_list,
    # )

    # trade_quantity = aggregate_trade_quantity(baci_data)

    # bilateral_trade = create_bilateral_trade(
    #     trade_data=trade_quantity,
    # )

    # bilateral_trade_shares = prepare_bilateral_trade_shares(
    #     bilateral_trade=bilateral_trade,
    #     commodity_code_mapping=timba_comcode,
    # )

    # price_change = calculate_growth_data(
    #     calc_manager=calc_manager,
    # )

    # df = calc_manager.main().copy()

    # bt_df=bilateral_trade_shares[["Reporter","Partner","Commodity","Period","Export_bilateral"]]#,"Trade_Volumn_Share","X_to_TV_bilateral"]]
    # bt_df["Export_bilateral"] = bt_df["Export_bilateral"] /1000
    # ft_df = df[["Reporter","Partner","Commodity","Period","X_q_o","M_q_p"]]

    # merge_keys = ["Reporter","Partner", "Commodity", "Period"]

    # ras_df = ft_df.merge(
    #     bt_df,
    #     on=merge_keys,
    #     how="left"
    # )

    # ras_df=ras_df[ras_df.Period==0]
    
    # # print(bt_df)
    # print(df)
    # # print(ras_df)
    # # print(ras_df.describe())

    # # dict_to_save = {
    # #     "price_change":price_change,
    # #     "total_change":total_change,
    # #     "biTrade_shares":bilateral_trade_shares,
    # #     "ras_df":ras_df
    # # }

    # # save_multiple_results(
    # #     output_manager=output_manager,
    # #     dict_to_save=dict_to_save,
    # # )

    # # run_dashboard(
    # #     bilateral_trade_shares=bilateral_trade_shares,
    # #     price_change=price_change,
    # # )

    # ras_df = ras_df[ras_df['Commodity'] != 89]
    # ras_df = ras_df[ras_df['Commodity'] != 90]
    # ras_df = ras_df[ras_df['Commodity'] != 93]
    
    # ras_result = RAS().fit(ras_df)

    # ras_result = ras_result[["Reporter", "Partner",  "Commodity",  "Period",  "Export_bilateral"]]
    # print(ras_result)


if __name__ == "__main__":
    main()
