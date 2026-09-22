from src.Trade_Module.core.CalculationManager import CalcManager
from src.Trade_Module.core.OutputManager import OutputManager
from src.Trade_Module.core.DashboardManager import Dashboard
from src.Trade_Module.paramters.paths import INPUT_PATH
from src.Trade_Module.paramters.hscodes import timba_commodity_list, timba_comcode

import pandas as pd

cm = CalcManager()
om = OutputManager()

if __name__== "__main__":
    baci_data = pd.read_parquet(INPUT_PATH / "BACI_DATA_as_vector.parquet")

    def hs_to_fao_dict(list):
        hs_to_fao_map = {}
        for entry in list:
            for hs_code in entry["hs02_codes"]:
                hs_to_fao_map[hs_code] = entry["fao_code"]
        return dict(sorted(hs_to_fao_map.items()))

    map = hs_to_fao_dict(list=timba_commodity_list)
    baci_data["TiMBA"] = baci_data["HSCode"].map(map)
    baci_data=baci_data[baci_data.Year==2023].reset_index(drop=True)
    result = (
        baci_data
        .dropna(subset=["TiMBA"])
        .groupby(["Year", "Reporter_Code", "Partner_Code", "TiMBA"])["Quantity"]
        .sum()
        .reset_index()
    )

    counterflow = result.rename(columns={
        "Reporter_Code": "Partner_Code",
        "Partner_Code": "Reporter_Code",
        "Quantity": "Import"
    })

    result = result.merge(
        counterflow,
        on=["Year", "Reporter_Code", "Partner_Code", "TiMBA"],
        how="outer"
    )   

    result = result.rename(columns={"Quantity":"Export"})

    bilateral = (
        result
        .groupby(["Year", "Reporter_Code", "Partner_Code", "TiMBA"])[
            ["Export", "Import"]
        ]
        .sum()
        .reset_index()
    )

    # Summe über alle Partner
    reporter_total = (
        bilateral
        .groupby(["Year", "Reporter_Code", "TiMBA"])[["Export", "Import"]]
        .sum()
        .reset_index()
    )

    total = bilateral.merge(
        right=reporter_total,
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

    reporter_total = reporter_total.rename(columns={"Reporter_Code":"Partner_Code"})

    total2 = total.merge(
        right=reporter_total,
        how="outer",
        on=[
            "Year", 
            "Partner_Code", 
            "TiMBA",
        ],
        suffixes=("", "_total_importer"),
    )

    total2 = total2[[
        "Year", "Reporter_Code", "Partner_Code", "TiMBA",
        "Export_bilateral", "Import_bilateral",
        "Export_total_exporter", "Import_total_exporter",
        "Export","Import",
    ]]

    total2.rename(
        columns={
           "Reporter_Code":"Reporter",
           "Partner_Code":"Partner",
           "Export":"Export_total_importer",
           "Import":"Import_total_importer",
           "TiMBA": "Commodity"
        },
        inplace=True
    )

    total2["Period"] = 0

    total2["Commodity"] = total2["Commodity"].map(timba_comcode)

    total2["Export_only_share"] = total2["Export_bilateral"] / total2["Export_total_exporter"]

    biTrade_shares = total2[[
        "Reporter", "Partner", "Commodity", "Period",
        "Export_bilateral","Export_only_share"
    ]]

    df = cm.main()
    keys = ["Reporter", "Partner", "Commodity", "Period"]

    df["P_share_growth"] = df["P_share_growth"] - 1
    df["M_growth"] = df["M_growth"] - 1

    price_change = df[["Reporter","Partner","Commodity","Period","P_share_growth"]]
    price_change = price_change.pivot_table(
        index=["Reporter", "Partner", "Commodity"],
        columns="Period",
        values="P_share_growth",
        aggfunc="sum"
    ).reset_index()

    total_change = df[["Reporter","Partner","Commodity","Period","M_growth"]]
    total_change = total_change.pivot_table(
        index=["Reporter", "Partner", "Commodity"],
        columns="Period",
        values="M_growth",
        aggfunc="sum"
    ).reset_index()


    om.save_df(df=price_change,file_name="price_change")
    om.save_df(df=total_change,file_name="total_change")
    om.save_df(df=biTrade_shares,file_name="biTrade_shares")

    dashboard = Dashboard(
        df_share=biTrade_shares,
        df_growth=price_change,
        top=5
    )

    dashboard.run()

