import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html

CATEGORY_A_ASSETS_INTL = ["Cash / Stablecoin", "BTC", "ETH", "SOL", "XRP", "BNB", "MATIC", "TRX", "All Other - Category A"]
CATEGORY_A_ASSETS_US = ["Cash / Stablecoin", "BTC", "ETH", "SOL", "DOGE", "MATIC", "LINK", "SHIB", "TRX", "UNI", "ALGO", "PAXG", "ETHW", "WBTC", "WETH", "All Other - Category A"]
CATEGORY_B_ASSETS = ["FTT", "MAPS", "SRM", "FIDA", "MEDIA", "All Other - Category B"]
ASSET_VALUE_COL = "Located Assets"

def create_dotcom_dict(ftx_intl_crypto_df: pd.DataFrame, ftx_intnl_related_party_df: pd.DataFrame) -> dict:
    ftx_dotcom_exchange = {
        "assets": {
            "Stablecoins": ftx_intl_crypto_df.loc["Cash / Stablecoin", ASSET_VALUE_COL],
            "BTC": ftx_intl_crypto_df.loc["BTC", ASSET_VALUE_COL],
            "ETH": ftx_intl_crypto_df.loc["ETH", ASSET_VALUE_COL],
            "SOL": ftx_intl_crypto_df.loc["SOL", ASSET_VALUE_COL],
            "XRP": ftx_intl_crypto_df.loc["XRP", ASSET_VALUE_COL],
            "BNB": ftx_intl_crypto_df.loc["BNB", ASSET_VALUE_COL],
            "MATIC": ftx_intl_crypto_df.loc["MATIC", ASSET_VALUE_COL],
            "TRX": ftx_intl_crypto_df.loc["TRX", ASSET_VALUE_COL],
            "All Other - Category A": ftx_intl_crypto_df.loc["All Other - Category A", ASSET_VALUE_COL],
            "FTT": ftx_intl_crypto_df.loc["FTT", ASSET_VALUE_COL],
            "MAPS": ftx_intl_crypto_df.loc["MAPS", ASSET_VALUE_COL],
            "SRM": ftx_intl_crypto_df.loc["SRM", ASSET_VALUE_COL],
            "FIDA": ftx_intl_crypto_df.loc["FIDA", ASSET_VALUE_COL],
            "MEDIA": ftx_intl_crypto_df.loc["MEDIA", ASSET_VALUE_COL],
            "All Other - Category B": ftx_intl_crypto_df.loc["All Other - Category B", ASSET_VALUE_COL],
            "Receivables": ftx_intnl_related_party_df["Estimated Receivables"].sum(),
        },
        "liabilities": {
            "Customer Payables - Category A": ftx_intl_crypto_df.loc[CATEGORY_A_ASSETS_INTL, "Customer Payables"].sum(),
            "Customer Payables - Category B": ftx_intl_crypto_df.loc[CATEGORY_B_ASSETS, "Customer Payables"].sum(),
            "Related Party Payables": ftx_intnl_related_party_df["Estimated Payables"].sum(),
        }
    }
    return ftx_dotcom_exchange

def create_us_exchange_dict(ftx_us_crypto_df: pd.DataFrame, ftx_us_related_party_df: pd.DataFrame) -> dict:

    ftx_us_exchange = {
        "assets": {
            "Stablecoins": ftx_us_crypto_df.loc["Cash / Stablecoin", ASSET_VALUE_COL],
            "BTC": ftx_us_crypto_df.loc["BTC", ASSET_VALUE_COL],
            "ETH": ftx_us_crypto_df.loc["ETH", ASSET_VALUE_COL],
            "SOL": ftx_us_crypto_df.loc["SOL", ASSET_VALUE_COL],
            "DOGE": ftx_us_crypto_df.loc["DOGE", ASSET_VALUE_COL],
            "MATIC": ftx_us_crypto_df.loc["MATIC", ASSET_VALUE_COL],
            "LINK": ftx_us_crypto_df.loc["LINK", ASSET_VALUE_COL],
            "SHIB": ftx_us_crypto_df.loc["SHIB", ASSET_VALUE_COL],
            "TRX": ftx_us_crypto_df.loc["TRX", ASSET_VALUE_COL],
            "UNI": ftx_us_crypto_df.loc["UNI", ASSET_VALUE_COL],
            "ALGO": ftx_us_crypto_df.loc["ALGO", ASSET_VALUE_COL],
            "PAXG": ftx_us_crypto_df.loc["PAXG", ASSET_VALUE_COL],
            "ETHW": ftx_us_crypto_df.loc["ETHW", ASSET_VALUE_COL],
            "WBTC": ftx_us_crypto_df.loc["WBTC", ASSET_VALUE_COL],
            "WETH": ftx_us_crypto_df.loc["WETH", ASSET_VALUE_COL],
            "All Other - Category A": ftx_us_crypto_df.loc["All Other - Category A", ASSET_VALUE_COL],
            "Receivables": ftx_us_related_party_df["Estimated Receivables"].sum(),
        },
        "liabilities": {
            "Customer Payables - Category A": ftx_us_crypto_df.loc[CATEGORY_A_ASSETS_US, "Customer Payables"].sum(),
            "Related Party Payables": ftx_us_related_party_df["Estimated Payables"].sum(),
        }
    }
    return ftx_us_exchange

def create_cash_graphs(cash_df: pd.DataFrame):
    cash_fig = go.Figure(data=[
        go.Bar(name=index, x=cash_df.columns, y=cash_df.loc[index], text=index) for index in cash_df.index
    ])
    return cash_fig.update_layout(barmode='stack')

def create_silo_graphs(assets_df: pd.DataFrame, liabilities_df: pd.DataFrame):
    silo_graphs = []

    for i, column in enumerate(assets_df.columns):
        fig = go.Figure()
        for index in assets_df.index:
            fig.add_trace(
                go.Bar(name=f'Assets: {index}', x=['Assets'], y=[assets_df.loc[index, column]],
                       hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                       showlegend=(i == len(assets_df.columns) - 1))
            )
        for index in liabilities_df.index:
            fig.add_trace(
                go.Bar(name=f'Liabilities: {index}', x=['Liabilities'], y=[liabilities_df.loc[index, column]],
                       hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                       showlegend=(i == len(assets_df.columns) - 1))
            )
        # fig.update_layout(barmode='stack', title_text=column, legend=dict(x=1.2, y=0.5))
        fig.update_layout(
            barmode='stack',
            title_text=column,
            autosize=False,
            width=500,
            height=500,
            margin=dict(
                l=10,  # left margin
                r=200,  # right margin: increase this to create more space for the legend
                b=100,  # bottom margin
                t=100,  # top margin
                pad=10
            ),
            legend=dict(x=2, y=0.5)
        )
        silo_graph = dcc.Graph(id=f'{column}-graph', figure=fig)
        silo_graphs.append(html.Div(silo_graph, className="three columns", style={'margin': '0px'}))
    return silo_graphs

def create_exchange_graph(asset_df, related_party_df, exchange=""):
    if exchange == "US":
        exchange_name = "FTX.US"
        exchange_id = "ftx_us"
        exchange = create_us_exchange_dict(asset_df, related_party_df)
    else:
        exchange_name = "FTX.COM"
        exchange_id = "ftx_dotcom"
        exchange = create_dotcom_dict(asset_df, related_party_df)

    # Create a new figure for the exchange
    fig = go.Figure()

    # Loop over asset and liability categories
    for category in ['assets', 'liabilities']:
        # Loop over the items in the category
        for item, value in exchange[category].items():
            # Add a bar to the figure for the item
            fig.add_trace(
                go.Bar(
                    name=item,
                    x=[category],
                    y=[value],
                    hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                )
            )

    # Update the layout to stack the bars and add a title
    fig.update_layout(
        barmode='stack',
        title=f'{exchange_name}',
        legend_title="Categories",
        autosize=False,
        width=500,
        height=500,
        margin=dict(
            l=20,  # left margin
            r=200,  # right margin: increase this to create more space for the legend
            b=100,  # bottom margin
            t=100,  # top margin
            pad=10
        ),
        legend=dict(x=1.2, y=0.5)
    )

    # Add the graph to the list of exchange graphs
    # exchange_graph = dcc.Graph(id=f'{exchange_id}_exchange_overview_graph', figure=fig)
    return fig.to_dict()

def create_visualizations(dataframes):

    cash_df = dataframes.get("cash_df")
    assets_df = dataframes.get("assets_df")
    liabilities_df = dataframes.get("liabilities_df")
    ftx_intl_crypto_df = dataframes.get("ftx_intl_crypto_df")
    ftx_us_crypto_df = dataframes.get("ftx_us_crypto_df")
    ftx_international_related_party_df = dataframes.get("ftx_international_related_party_df")
    ftx_us_related_party_df = dataframes.get("ftx_us_related_party_df")

    exchange_graphs = []
    cash_graphs = create_cash_graphs(cash_df)
    silo_graphs = create_silo_graphs(assets_df, liabilities_df)
    ftx_intl_fig = create_exchange_graph(ftx_intl_crypto_df, ftx_international_related_party_df)
    ftx_us_fig = create_exchange_graph(ftx_us_crypto_df, ftx_us_related_party_df, "US")
    exchange_graphs.append(html.Div(dcc.Graph(id='ftx_dotcom_exchange_overview_graph', figure=ftx_intl_fig), className="three columns", style={'marginRight': '140px'}))
    exchange_graphs.append(html.Div(dcc.Graph(id='ftx_us_exchange_overview_graph', figure=ftx_us_fig), className="three columns", style={'marginRight': '140px'}))

    visualizations = {
        "cash_graphs": cash_graphs,
        "silo_graphs": silo_graphs,
        "exchange_graphs": exchange_graphs,
    }

    return visualizations
