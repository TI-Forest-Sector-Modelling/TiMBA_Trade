import webbrowser
from threading import Timer

import pandas as pd
import plotly.express as px

from dash import Dash, Input, Output, dcc, html


class Dashboard:
    PORT = 8051
    HOST = "localhost"

    REST_OF_WORLD = "Rest of world"
    REST_OF_WORLD_COLOR = "#B0B0B0"

    GRAPH_CONFIG = {
        "displayModeBar": False,
        "responsive": True,
    }

    GRAPH_STYLE = {
        "height": "100%",
        "width": "100%",
    }

    GRAPH_WRAPPER_STYLE = {
        "minWidth": 0,
        "minHeight": 0,
        "width": "100%",
        "height": "100%",
        "overflow": "hidden",
    }

    def __init__(self, df_share, df_growth, top=9):
        self.df_share = df_share.copy()
        self.df_growth = df_growth.copy()
        self.top = top

        self._prepare_data()

        self.app = Dash(__name__)

        self._create_layout()
        self._create_callbacks()

    def _prepare_data(self):
        string_columns = {
            "Reporter",
            "Partner",
            "Commodity",
        }

        for df in (self.df_share, self.df_growth):
            columns = string_columns.intersection(df.columns)

            for column in columns:
                df[column] = df[column].astype(str)

        self.period_columns = [
            column
            for column in self.df_growth.columns
            if str(column).isdigit()
        ]

    @staticmethod
    def _pair_key(country1, country2):
        """Return order-independent country-pair key."""

        return " ↔ ".join(
            sorted((str(country1), str(country2)))
        )

    @staticmethod
    def _display_pair(country1, country2):
        return f"{country1} → {country2}"

    def _add_pair_columns(self, df):
        df = df.copy()

        df["CountryPair"] = (
            df["Reporter"].astype(str)
            + " → "
            + df["Partner"].astype(str)
        )

        df["ColorPair"] = [
            self._pair_key(reporter, partner)
            for reporter, partner in zip(
                df["Reporter"],
                df["Partner"],
            )
        ]

        return df
    
    def _build_display_color_map(self, *dataframes):
        pair_keys = set()

        for df in dataframes:
            if df.empty or "ColorPair" not in df.columns:
                continue

            pair_keys.update(
                df["ColorPair"]
                .dropna()
                .astype(str)
            )

        pair_keys.discard(self.REST_OF_WORLD)

        palette = px.colors.qualitative.Alphabet

        color_map = {
            pair: palette[index % len(palette)]
            for index, pair in enumerate(sorted(pair_keys))
        }

        color_map[self.REST_OF_WORLD] = (
            self.REST_OF_WORLD_COLOR
        )

        return color_map
    
    @staticmethod
    def _apply_filter(df, column, value):
        """Apply one optional filter."""

        if value is not None:
            df = df[df[column] == str(value)]

        return df

    def _filter_data(
        self,
        df,
        reporter=None,
        commodity=None,
    ):
        """Apply reporter and commodity filters."""

        if reporter is not None:
            df = df[df["Reporter"] == str(reporter)]

        if commodity is not None:
            df = df[df["Commodity"] == str(commodity)]

        return df
    
    @staticmethod
    def _make_filter_dropdown(
        dropdown_id,
        label,
        options,
    ):
        return html.Div(
            [
                html.Label(
                    label,
                    style={
                        "fontWeight": "bold",
                        "fontFamily": "Calibri",
                    },
                ),

                dcc.Dropdown(
                    id=dropdown_id,
                    options=[
                        {
                            "label": value,
                            "value": value,
                        }
                        for value in options
                    ],
                    placeholder=f"Select {label.lower()}",
                    clearable=True,
                ),
            ],
            style={
                "width": "48%",
            },
        )

    def _create_layout(self):

        reporter_options = sorted(
            self.df_share["Reporter"]
            .dropna()
            .unique()
        )

        commodity_options = sorted(
            self.df_share["Commodity"]
            .dropna()
            .unique()
        )

        filters = html.Div(
            [
                self._make_filter_dropdown(
                    "reporter-filter",
                    "Reporter",
                    reporter_options,
                ),

                self._make_filter_dropdown(
                    "commodity-filter",
                    "Commodity",
                    commodity_options,
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "width": "100%",
                "flex": "0 0 auto",
            },
        )

        header = html.Div(
            [
                html.H1(
                    "Dashboard for TiMBA Trade Module",
                    style={
                        "textAlign": "center",
                        "fontFamily": "Calibri, Arial, sans-serif",
                        "fontSize": "28px",
                        "margin": "0 0 10px 0",
                    },
                ),
                filters,
            ],
            style={
                "flex": "0 0 auto",
            },
        )

        graph_grid = html.Div(
            [
                self._make_graph_container(
                    "share-pie",
                    column=1,
                ),

                self._make_graph_container(
                    "growth-bar",
                    column=2,
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": (
                    "minmax(0, 1fr) "
                    "minmax(0, 1fr)"
                ),
                "gridTemplateRows": "minmax(0, 1fr)",
                "gap": "10px",
                "flex": "1 1 auto",
                "minWidth": 0,
                "minHeight": 0,
                "width": "100%",
            },
        )

        dashboard = html.Div(
            [
                header,
                graph_grid,
            ],
            style={
                "width": "95vw",
                "height": "95vh",
                "margin": "auto",
                "padding": "15px",
                "border": "1px solid #B0B0B0",
                "borderRadius": "8px",
                "boxSizing": "border-box",
                "display": "flex",
                "flexDirection": "column",
                "overflow": "hidden",
                "backgroundColor": "white",
            },
        )

        self.app.layout = html.Div(
            dashboard,
            style={
                "width": "100vw",
                "height": "100vh",
                "display": "flex",
                "margin": "0",
                "padding": "0",
                "boxSizing": "border-box",
                "overflow": "hidden",
                "fontFamily": "Calibri, Arial, sans-serif",
                "backgroundColor": "#F5F5F5",
            },
        )

    def _make_graph_container(self, graph_id, column):
        return html.Div(
            dcc.Graph(
                id=graph_id,
                style=self.GRAPH_STYLE,
                config=self.GRAPH_CONFIG,
            ),
            style={
                **self.GRAPH_WRAPPER_STYLE,
                "gridColumn": str(column),
                "gridRow": "1",
            },
        )

    def _grouped_share(
        self,
        reporter=None,
        commodity=None,
    ):

        filtered = self._filter_data(
            self.df_share,
            reporter=reporter,
            commodity=commodity,
        )

        if filtered.empty:
            return pd.DataFrame(
                columns=[
                    "Reporter",
                    "Partner",
                    "Export_only_share",
                    "CountryPair",
                    "ColorPair",
                ]
            )

        grouped = (
            filtered
            .groupby(
                ["Reporter", "Partner"],
                as_index=False,
            )["Export_only_share"]
            .mean()
            .sort_values(
                "Export_only_share",
                ascending=False,
            )
        )

        return self._add_pair_columns(grouped)
    
    def _create_pie(
        self,
        grouped,
        top,
        color_map,
    ):

        pie_data = top[
            [
                "CountryPair",
                "ColorPair",
                "Export_only_share",
            ]
        ].copy()

        rest = (
            grouped["Export_only_share"].sum()
            - top["Export_only_share"].sum()
        )

        if rest > 0:
            pie_data = pd.concat(
                [
                    pie_data,
                    pd.DataFrame(
                        {
                            "CountryPair": [
                                self.REST_OF_WORLD
                            ],
                            "ColorPair": [
                                self.REST_OF_WORLD
                            ],
                            "Export_only_share": [
                                rest
                            ],
                        }
                    ),
                ],
                ignore_index=True,
            )

        fig = px.pie(
            pie_data,
            names="CountryPair",
            values="Export_only_share",
            color="ColorPair",
            color_discrete_map=color_map,
            title="Export bilateral from BACI for 2023",
        )

        fig.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Share: %{value:.4f}<br>"
                "Percent: %{percent}"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            font_family="Calibri",
            margin={
                "l": 10,
                "r": 10,
                "t": 50,
                "b": 10,
            },
            autosize=True,
        )

        return fig

    def _bar_plot_data_generator(
        self,
        top,
        reporter=None,
        commodity=None,
    ):
        df = self._filter_data(
            self.df_growth,
            reporter=reporter,
            commodity=commodity,
        )

        if df.empty:
            return (
                pd.DataFrame(
                    columns=[
                        "CountryPair",
                        "ColorPair",
                        "Period",
                        "Value",
                    ]
                ),
                [],
            )

        pairs = top[
            ["Reporter", "Partner"]
        ].drop_duplicates()

        pair_index = pd.MultiIndex.from_frame(
            pairs.astype(str)
        )

        df_index = pd.MultiIndex.from_frame(
            df[
                ["Reporter", "Partner"]
            ].astype(str)
        )

        is_top = df_index.isin(pair_index)

        df_top = df.loc[is_top].copy()
        df_rest = df.loc[~is_top].copy()

        if not df_top.empty:
            df_top = (
                df_top
                .groupby(
                    ["Reporter", "Partner"],
                    as_index=False,
                )[self.period_columns]
                .mean()
            )

            df_top = self._add_pair_columns(df_top)

            df_long = df_top.melt(
                id_vars=[
                    "CountryPair",
                    "ColorPair",
                ],
                value_vars=self.period_columns,
                var_name="Period",
                value_name="Value",
            )

        else:
            df_long = pd.DataFrame(
                columns=[
                    "CountryPair",
                    "ColorPair",
                    "Period",
                    "Value",
                ]
            )

        pair_order = top["CountryPair"].tolist()

        if not df_rest.empty:
            rest_values = (
                df_rest[self.period_columns]
                .mean()
            )

            rest_long = pd.DataFrame(
                {
                    "CountryPair": self.REST_OF_WORLD,
                    "ColorPair": self.REST_OF_WORLD,
                    "Period": self.period_columns,
                    "Value": rest_values.values,
                }
            )

            df_long = pd.concat(
                [
                    df_long,
                    rest_long,
                ],
                ignore_index=True,
            )

            pair_order.append(
                self.REST_OF_WORLD
            )

        if not df_long.empty:
            df_long["Period"] = (
                df_long["Period"].astype(int)
            )

            df_long["CountryPair"] = pd.Categorical(
                df_long["CountryPair"],
                categories=pair_order,
                ordered=True,
            )

        return df_long, pair_order

    def _create_bar(
        self,
        df_long,
        pair_order,
        color_map,
    ):

        color_order = [
            (
                self.REST_OF_WORLD
                if pair == self.REST_OF_WORLD
                else self._pair_key(
                    *pair.split(" → ")
                )
            )
            for pair in pair_order
        ]

        fig = px.bar(
            df_long,
            x="Period",
            y="Value",
            color="ColorPair",
            color_discrete_map=color_map,
            barmode="group",
            category_orders={
                "ColorPair": color_order,
            },
            title=f"Export development from TiMBA in the top {self.top} country pairs",
            template="plotly_white",
        )

        fig.update_yaxes(
            tickformat=".1%",
            title="Export development from TiMBA (%)",
        )

        fig.update_xaxes(
            dtick=1,
            title="Period",
        )

        fig.update_traces(
            customdata=df_long[
                ["CountryPair"]
            ].astype(str),
            hovertemplate=(
                "Period: %{x}<br>"
                "Country pair: %{customdata[0]}<br>"
                "Value: %{y:.2%}"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            font_family="Calibri",
            title={
                "font": {
                    "size": 18,
                }
            },
            margin={
                "l": 45,
                "r": 10,
                "t": 50,
                "b": 70,
            },
            xaxis_title="Period",
            yaxis_title="Export development",
            legend_title="Country pair",
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.30,
                "xanchor": "center",
                "x": 0.5,
                "font": {
                    "size": 14,
                },
            },
            bargap=0.10,
            bargroupgap=0.03,
            autosize=True,
        )

        return fig

    def _create_callbacks(self):

        @self.app.callback(
            Output("share-pie", "figure"),
            Output("growth-bar", "figure"),
            Input("reporter-filter", "value"),
            Input("commodity-filter", "value"),
        )
        def update_dashboard(
            reporter,
            commodity,
        ):
            grouped_export = self._grouped_share(
                reporter=reporter,
                commodity=commodity,
            )

            top_export = (
                grouped_export
                .head(self.top)
                .copy()
            )

            color_map = (
                self._build_display_color_map(
                    top_export
                )
            )

            export_pie = self._create_pie(
                grouped_export,
                top_export,
                color_map,
            )

            df_long, pair_order = (
                self._bar_plot_data_generator(
                    top_export,
                    reporter=reporter,
                    commodity=commodity,
                )
            )

            export_bar = self._create_bar(
                df_long,
                pair_order,
                color_map,
            )

            return export_pie, export_bar

    def open_browser(self):
          webbrowser.open_new(
            f"http://{self.HOST}:{self.PORT}"
        )

    def run(self):
        Timer(
            1,
            self.open_browser,
        ).start()

        self.app.run(
            host=self.HOST,
            debug=False,
            dev_tools_ui=False,
            dev_tools_hot_reload=False,
            port=self.PORT,
        )
