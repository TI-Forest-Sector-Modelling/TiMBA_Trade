from src.Trade_Module.core.CalculationManager import CalcManager
from src.Trade_Module.core.OutputManager import OutputManager
from src.Trade_Module.paramters.paths import INPUT_PATH
from src.Trade_Module.paramters.hscodes import timba_commodity_list

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
        how="left"
    )   

    result = result.rename(columns={"Quantity":"Export"})

    # Bilaterale Daten
    bilateral = (
        result
        .groupby(["Year", "Reporter_Code", "Partner_Code", "TiMBA"])[
            ["Export", "Import"]
        ]
        .sum()
        .reset_index()
    )
    print(bilateral)

    # Summe über alle Partner
    reporter_total = (
        bilateral
        .groupby(["Year", "Reporter_Code", "TiMBA"])[["Export", "Import"]]
        .sum()
        .reset_index()
    )
    print(reporter_total)

    # Partner als Kennzeichnung für die Gesamtzeile
    reporter_total["Partner_Code"] = "TOTAL"

    # Gleiche Spaltenreihenfolge
    reporter_total = reporter_total[
        ["Year", "Reporter_Code", "Partner_Code", "TiMBA", "Export", "Import"]
    ]

    # Bilaterale und Gesamtzeilen zusammenführen
    result_final = pd.concat(
        [result, reporter_total],
        ignore_index=True
    )

    print(result_final)
    om.save_df(
        df=result_final,
        file_name="bilateral_trade"
    )

    df = cm.main()
    print(df.describe())
    filename = "v009_DEU"
    df = df[df.Country.isin(["AUT","DEU"])]
    om.save_df(
        df=df,
        file_name=filename
    )
