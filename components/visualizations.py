import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html
import random

CATEGORY_A_ASSETS_INTL = ["Cash / Stablecoin", "BTC", "ETH", "SOL", "XRP", "BNB", "MATIC", "TRX", "All Other - Category A"]
CATEGORY_A_ASSETS_US = ["Cash / Stablecoin", "BTC", "ETH", "SOL", "DOGE", "MATIC", "LINK", "SHIB", "TRX", "UNI", "ALGO", "PAXG", "ETHW", "WBTC", "WETH", "All Other - Category A"]
CATEGORY_B_ASSETS = ["FTT", "MAPS", "SRM", "FIDA", "MEDIA", "All Other - Category B"]
ASSET_VALUE_COL = "Located Assets"

def create_exchange_dict(crypto_df: pd.DataFrame, related_party_df: pd.DataFrame) -> dict:
    # Extract the column name dynamically. Assume that the required column is the last one.

    # Identify Category A and B assets. Assume they are marked by "- Category A" and "- Category B" in index.
    category_a_assets = crypto_df.index[crypto_df.index.str.contains('- Category A')]
    category_b_assets = crypto_df.index[crypto_df.index.str.contains('- Category B')]

    assets_dict = {
        asset: crypto_df.loc[asset, ASSET_VALUE_COL] for asset in crypto_df.index
    }
    assets_dict["Receivables"] = related_party_df["Estimated Receivables"].sum()

    # Create the dictionary for liabilities
    liabilities_dict = {
        liability: crypto_df.loc[liability, "Customer Payables"] for liability in crypto_df.index
    }
    liabilities_dict["Related Party Payables"] = related_party_df["Estimated Payables"].sum()

    # Create the final exchange dictionary
    exchange = {
        "assets": assets_dict,
        "liabilities": liabilities_dict,
    }

    return exchange

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
            y_value = assets_df.loc[index, column]
            if y_value != 0 and not pd.isnull(y_value):
                fig.add_trace(
                    go.Bar(name=f'Assets: {index}', x=['Assets'], y=[y_value],
                           hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                           showlegend=True)
                )
        for index in liabilities_df.index:
            y_value = liabilities_df.loc[index, column]
            if y_value != 0 and not pd.isnull(y_value):
                fig.add_trace(
                    go.Bar(name=f'Liabilities: {index}', x=['Liabilities'], y=[y_value],
                           hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                           showlegend=True)
                )

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
            legend=dict(x=2, y=0.5),
            plot_bgcolor='rgb(29, 31, 43)',
            paper_bgcolor='rgb(29, 31, 43)',
            font_color='white',
        )

        silo_graph = dcc.Graph(id=f'{column}-graph', figure=fig)
        silo_graphs.append(html.Div(silo_graph, className="four columns", style={'margin-top': '10px'}))
    return silo_graphs

def create_exchange_graph(asset_df, related_party_df, exchange=""):
    if exchange == "US":
        exchange_name, exchange_id = "FTX.US", "ftx_us"
        # exchange = create_us_exchange_dict(asset_df, related_party_df)
    else:
        exchange_name, exchange_id = "FTX.COM", "ftx_dotcom"
        # exchange = create_dotcom_dict(asset_df, related_party_df)
    exchange = create_exchange_dict(asset_df, related_party_df)

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
    fig.update_layout(
        plot_bgcolor='rgb(29, 31, 43)',
        paper_bgcolor='rgb(29, 31, 43)',
        font_color='white',
    )
    return fig.to_dict()

def calculate_recovery_rate(asset_df, related_party_df):
    # Calculate the recovery rate
    exchange = create_exchange_dict(asset_df, related_party_df)
    total_assets = sum(exchange['assets'].values())
    total_liabilities = sum(exchange['liabilities'].values())
    recovery_rate = total_assets / total_liabilities * 100  # the recovery rate as a percentage

    return recovery_rate

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
    # exchange_graphs.append(html.Div(dcc.Graph(id='ftx_dotcom_exchange_overview_graph', figure=ftx_intl_fig), className="three columns", style={'marginRight': '140px'}))
    # exchange_graphs.append(html.Div(dcc.Graph(id='ftx_us_exchange_overview_graph', figure=ftx_us_fig), className="three columns", style={'marginRight': '140px'}))

    ftx_intl_recovery_rate = calculate_recovery_rate(ftx_intl_crypto_df, ftx_international_related_party_df)
    ftx_us_recovery_rate = calculate_recovery_rate(ftx_us_crypto_df, ftx_us_related_party_df)

    exchange_graphs.append(html.Div([
        dcc.Graph(id='ftx_dotcom_exchange_overview_graph', figure=ftx_intl_fig),
        html.H5(f'Recovery Rate: {ftx_intl_recovery_rate:.2f}%', id="ftx_dotcom_recovery_rate", style={"color": "rgb(14, 200, 64)"})
        # show recovery rate under the graph
    ], className="four columns", style={'marginRight': '240px'}))  # added width to div

    exchange_graphs.append(html.Div([
        dcc.Graph(id='ftx_us_exchange_overview_graph', figure=ftx_us_fig),
        html.H5(f'Recovery Rate: {ftx_us_recovery_rate:.2f}%', id="ftx_us_recovery_rate", style={"color": "rgb(14, 200, 64)"})
        # show recovery rate under the graph
    ], className="four columns"))  # added width to div

    visualizations = {
        "cash_graphs": cash_graphs,
        "silo_graphs": silo_graphs,
        "exchange_graphs": exchange_graphs,
    }

    return visualizations
