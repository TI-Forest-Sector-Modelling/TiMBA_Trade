import pandas as pd
import plotly.express as px
from threading import Timer
import webbrowser

from dash import Dash, dcc, html, Input, Output


class Dashboard:

    def __init__(self, df_share, df_growth, top=9):
        self.df_share = df_share.copy()
        self.df_growth = df_growth.copy()
        self.top = top

        self.df_share["Commodity"] = self.df_share["Commodity"].astype(str)
        self.df_growth["Commodity"] = self.df_growth["Commodity"].astype(str)
        self.df_growth["Reporter"] = self.df_growth["Reporter"].astype(str)
        self.df_growth["Partner"] = self.df_growth["Partner"].astype(str)

        self.df_share = self.df_share[
            self.df_share["Export_only_share"].notna()
        ].copy()

        self.period_columns = [
            c for c in self.df_growth.columns if str(c).isdigit()
        ]

        self.app = Dash(__name__)

        self._create_layout()
        self._create_callbacks()

    # Layout

    def _create_layout(self):

        reporters = sorted(self.df_share["Reporter"].dropna().unique())
        commodities = sorted(
            self.df_share["Commodity"].dropna().unique(),
            key=lambda x: float(x)
        )

        self.app.layout = html.Div(
            [
                html.H1(
                    "Dashboard for TiMBA Trade Module",
                    style={"textAlign": "center", 
                           "marginBottom": "30px",
                           "fontFamily": "Calibri"
                    }
                ),

                # Filter
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Reporter", 
                                           style={
                                               #"fontWeight": "bold",
                                               "fontFamily": "Calibri"
                                            }),
                                dcc.Dropdown(
                                    id="reporter-filter",
                                    options=[{"label": x, "value": x} for x in reporters],
                                    placeholder="All Reporters",
                                    clearable=True
                                )
                            ],
                            style={"width": "45%", "display": "inline-block", "marginRight": "5%"}
                        ),

                        html.Div(
                            [
                                html.Label("Commodity", 
                                           style={
                                               #"fontWeight": "bold",
                                               "fontFamily": "Calibri"
                                            }),
                                dcc.Dropdown(
                                    id="commodity-filter",
                                    options=[{"label": x, "value": x} for x in commodities],
                                    placeholder="All Commodities",
                                    clearable=True
                                )
                            ],
                            style={"width": "45%", "display": "inline-block"}
                        )
                    ],
                    style={"marginBottom": "30px"}
                ),

                # Plots
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="share-pie")],
                            style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}
                        ),

                        html.Div(
                            [dcc.Graph(id="growth-bar")],
                            style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}
                        )
                    ]
                )
            ],
            style={"padding": "30px"}
        )

    # Data helpers

    def _filter_data(self, reporter=None, commodity=None):
        df = self.df_share

        if reporter is not None:
            df = df[df["Reporter"] == reporter]

        if commodity is not None:
            df = df[df["Commodity"] == commodity]

        return df

    def _grouped_share(self, reporter=None, commodity=None):
        df = self._filter_data(reporter=reporter, commodity=commodity)

        grouped = (
            df.groupby(["Reporter", "Partner"], as_index=False)["Export_only_share"]
            .mean()
            .sort_values("Export_only_share", ascending=False)
        )

        grouped["CountryPair"] = grouped["Reporter"] + " → " + grouped["Partner"]

        return grouped

    # Figures

    def _create_pie(self, grouped, top):

        rest = grouped["Export_only_share"].sum() - top["Export_only_share"].sum()

        pie_data = top[["CountryPair", "Export_only_share"]]

        if rest > 0:
            pie_data = pd.concat(
                [
                    pie_data,
                    pd.DataFrame(
                        {"CountryPair": ["Rest of world"], "Export_only_share": [rest]}
                    )
                ],
                ignore_index=True
            )

        fig = px.pie(
            pie_data,
            names="CountryPair",
            values="Export_only_share",
            title="Export-only share"
        )

        fig.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Share: %{value:.4f}<br>"
                "Percent: %{percent}"
                "<extra></extra>"
            )
        )

        return fig

    def _create_bar(self, top, reporter=None, commodity=None):

        df = self.df_growth

        if reporter is not None:
            df = df[df["Reporter"] == str(reporter)]

        if commodity is not None:
            df = df[df["Commodity"] == str(commodity)]

        pairs = top[["Reporter", "Partner"]].astype(str)

        merged = df.merge(
            pairs,
            on=["Reporter", "Partner"],
            how="left",
            indicator=True
        )

        df_top = merged[merged["_merge"] == "both"]
        df_rest = merged[merged["_merge"] == "left_only"]

        df_top = (
            df_top.groupby(["Reporter", "Partner"], as_index=False)[self.period_columns]
            .mean()
        )
        df_top["CountryPair"] = df_top["Reporter"] + " → " + df_top["Partner"]

        df_long = df_top.melt(
            id_vars=["CountryPair"],
            value_vars=self.period_columns,
            var_name="Period",
            value_name="Value"
        )

        pair_order = top["CountryPair"].tolist()

        if not df_rest.empty:
            rest_sums = df_rest[self.period_columns].mean()

            rest_long = pd.DataFrame(
                {
                    "CountryPair": "Rest of world",
                    "Period": self.period_columns,
                    "Value": rest_sums.values
                }
            )

            df_long = pd.concat([df_long, rest_long], ignore_index=True)
            pair_order = pair_order + ["Rest of world"]

        df_long["Period"] = df_long["Period"].astype(int)

        df_long["CountryPair"] = pd.Categorical(
            df_long["CountryPair"],
            categories=pair_order,
            ordered=True
        )

        fig = px.bar(
            df_long,
            x="Period",
            y="Value",
            color="CountryPair",
            barmode="group",
            category_orders={"CountryPair": pair_order},
            title=f"Export development of top {self.top} country pairs"
        )

        fig.update_yaxes(
            tickformat=".1%",
            title="Export development (%)"
        )

        fig.update_traces(
            hovertemplate=(
                "Period: %{x}<br>"
                "Country pair: %{fullData.name}<br>"
                "Value: %{y:.2%}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            xaxis_title="Period",
            yaxis_title="Export effect",
            legend_title="Country pair",
            bargap=0.15,
            bargroupgap=0.05
        )

        fig.update_xaxes(dtick=1)

        return fig

    # Callbacks

    def _create_callbacks(self):

        @self.app.callback(
            Output("share-pie", "figure"),
            Output("growth-bar", "figure"),
            Input("reporter-filter", "value"),
            Input("commodity-filter", "value")
        )
        def update_dashboard(reporter, commodity):

            grouped = self._grouped_share(reporter=reporter, commodity=commodity)
            top = grouped.head(self.top)

            pie = self._create_pie(grouped, top)
            bar = self._create_bar(top, reporter=reporter, commodity=commodity)

            return pie, bar

    def open_browser(self):
        webbrowser.open_new("http://localhost:8051")

    def run(self):
        Timer(1, self.open_browser).start()
        self.app.run(host='localhost', debug=False, dev_tools_ui=False, dev_tools_hot_reload=False, port=8051)