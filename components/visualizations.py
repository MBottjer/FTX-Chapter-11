import pandas as pd
import plotly.graph_objects as go
from dash import dcc, dash_table
from dash import html
import plotly.express as px

CATEGORY_B_ASSETS = ["FTT", "MAPS", "SRM", "FIDA", "MEDIA", "OXY", "All Other - Category B"]
ASSET_VALUE_COL = "Located Assets"

def create_exchange_dict(crypto_df: pd.DataFrame, related_party_df: pd.DataFrame) -> dict:
    relevant_cols = ["Cash / Stablecoin", "Crypto - Category A", "Crypto - Category B"]
    assets_dict = {
        # asset: crypto_df.loc[asset, ASSET_VALUE_COL] for asset in crypto_df.index
        asset: crypto_df.loc[asset, ASSET_VALUE_COL] for asset in relevant_cols
    }
    assets_dict["Receivables"] = related_party_df["Estimated Receivables"].sum()

    # Create the dictionary for liabilities
    liabilities_dict = {
        liability: crypto_df.loc[liability, "Customer Payables"] for liability in relevant_cols
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
    else:
        exchange_name, exchange_id = "FTX.COM", "ftx_dotcom"
    exchange = create_exchange_dict(asset_df, related_party_df)

    unique_labels = set(exchange['assets'].keys()).union(set(exchange['liabilities'].keys()))
    colors = px.colors.qualitative.D3
    label_color_map = {label: colors[i % len(colors)] for i, label in enumerate(unique_labels)}

    fig = go.Figure()
    trace_indices = {}

    for category in ['assets', 'liabilities']:
        for item, value in exchange[category].items():
            if item not in trace_indices:
                fig.add_trace(
                    go.Bar(
                        name=item,
                        x=(category,),
                        y=(value,),
                        hovertemplate='<b>%{fullData.name}</b><br><i>Amount</i>: %{y}<extra></extra>',
                        marker_color=label_color_map[item],
                    )
                )
                trace_indices[item] = len(fig.data) - 1  # store the trace index
            else:
                fig.data[trace_indices[item]].x += (category,)
                fig.data[trace_indices[item]].y += (value,)

    fig.update_layout(
        barmode='stack',
        title=f'{exchange_name}',
        legend_title="Categories",
        autosize=False,
        width=500,
        height=500,
        margin=dict(l=20, r=200, b=100, t=100, pad=10),
        legend=dict(x=1.2, y=0.5),
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

def create_ventures_table(ventures_df: pd.DataFrame):
    ventures_df.reset_index(inplace=True)

    # Create the Dash table from the ventures DataFrame
    ventures_table = dash_table.DataTable(
        id='ventures-table',
        columns=[{'name': col, 'id': col} for col in ventures_df.columns],
        data=ventures_df.to_dict('records'),
        virtualization=True,  # Enable vertical scrolling instead of pagination
        filter_action='native',  # Enables the search functionality
        style_table={
            'overflowX': 'scroll',  # Enable horizontal scrolling
            'overflowY': 'scroll',  # Enable vertical scrolling
            'maxHeight': '500px',   # Set a maximum height for the table
            'maxWidth': '100%',    # Limit the width of the table to the width of the page
            'margin': '0 auto',    # Center the table horizontally within its container
            'backgroundColor': 'rgb(29, 31, 43)',  # Set the background color of the table
            'color': 'white',      # Set the font color to white
            'border': '1px solid #0A0E17',  # Set the border color
        },
        style_header={
            'backgroundColor': 'rgb(29, 31, 43)',  # Set the background color of the header
            'fontWeight': '900',  # Set the header font to bold
            'color': 'white',  # Set the font color of the header to white
            'border': '2px solid #0A0E17',  # Set the border color
        },
        style_cell={
            'backgroundColor': 'rgb(29, 31, 43)',  # Set the background color of the cells
            'color': 'white',  # Set the font color of the cells to white
            'whiteSpace': 'normal',  # Set the whiteSpace property to 'normal' to allow text wrapping
            'textAlign': 'left',  # Align the text to the left within cells
            'minWidth': '0px',  # Set the minimum width of the cells to allow auto-sizing
            'maxWidth': '180px',  # Set the maximum width of the cells to control wrapping
            'overflow': 'hidden',  # Hide any content that overflows the cell
            'textOverflow': 'ellipsis',  # Display ellipsis for text that overflows the cell
            'border': '1px solid #0A0E17',  # Set the border color
            'fontFamily': 'Inter',
            'textAlign': 'center',
        },
        style_data={
            'whiteSpace': 'normal',  # Set the whiteSpace property to 'normal' to allow text wrapping
            'height': 'auto',  # Set the height of the cells to fit content
        },
        style_filter={
            'color': 'white'
        },
        style_data_conditional=[
           {
               'if': {'column_id': col},
               'maxWidth': f"{max(ventures_df[col].astype(str).str.len().max(), len(col)) * 12}px"
           } for col in ventures_df.columns
       ] + [
           {
               'if': {'column_id': ventures_df.columns[0]},
               'maxWidth': '100px',  # Set a max width of 200px for the first column
               'textAlign': 'left',
           }
       ],
        page_action='none',  # Disable pagination
        fixed_rows={'headers': True},
    )

    # Set a maximum width for the table container
    table_container = html.Div(ventures_table)

    return table_container

def create_visualizations(dataframes):

    cash_df = dataframes.get("cash_df")
    assets_df = dataframes.get("assets_df")
    liabilities_df = dataframes.get("liabilities_df")
    ftx_intl_crypto_df = dataframes.get("ftx_intl_crypto_df")
    ftx_us_crypto_df = dataframes.get("ftx_us_crypto_df")
    ftx_international_related_party_df = dataframes.get("ftx_international_related_party_df")
    ftx_us_related_party_df = dataframes.get("ftx_us_related_party_df")
    ventures_df = dataframes.get("venture_df")

    exchange_graphs = []
    cash_graphs = create_cash_graphs(cash_df)
    silo_graphs = create_silo_graphs(assets_df, liabilities_df)
    ftx_intl_fig = create_exchange_graph(ftx_intl_crypto_df, ftx_international_related_party_df)
    ftx_us_fig = create_exchange_graph(ftx_us_crypto_df, ftx_us_related_party_df, "US")
    ventures_table = create_ventures_table(ventures_df)

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
        "ventures_table": ventures_table,
    }

    return visualizations
