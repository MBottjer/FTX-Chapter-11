from dash import dash, Output, Input, exceptions, dcc, html
from data_processing.data import load_data
from components.visualizations import create_visualizations, create_exchange_graph
from layouts.layout import create_layout
import pandas as pd

dataframes = load_data()
dataframes_json = {k: v.to_dict(orient='split') for k, v in dataframes.items()}  # Convert to JSON serializable format
visualizations = create_visualizations(dataframes)

app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Roboto&display=swap', 'https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = html.Div([
    dcc.Store(id='data-store', data=dataframes_json),  # Store data in dcc.Store
    create_layout(visualizations)  # Call your create_visualizations function here
])
# app.config.suppress_callback_exceptions = True

def zero_out_sam_coins(data):
    sam_coins = ["FTT", "MAPS", "SRM", "FIDA", "MEDIA", "All Other - Category B"]

    for key in data:
        if 'index' in data[key] and 'data' in data[key]:
            indices = data[key]['index']
            for coin in sam_coins:
                if coin in indices:
                    index = indices.index(coin)
                    data[key]['data'][index] = [0]*len(data[key]['data'][index])
    return data

def add_cash_to_stablecoin(data):
    cash_df = data["cash_df"]
    # Get the indices of Alameda and Ventures
    alameda_index = cash_df['columns'].index('Alameda')
    ventures_index = cash_df['columns'].index('Ventures')

    # Sum up all values in the Alameda and Ventures columns
    total_cash = sum(row[alameda_index] + row[ventures_index] for row in cash_df['data'])

    # Get the index of Cash / Stablecoin in ftx_intl_crypto_df
    cash_stablecoin_index = data['ftx_intl_crypto_df']['index'].index('Cash / Stablecoin')

    # Add total_cash to Cash / Stablecoin values in ftx_intl_crypto_df
    for i in range(len(data['ftx_intl_crypto_df']['data'][cash_stablecoin_index])):
        data['ftx_intl_crypto_df']['data'][cash_stablecoin_index][i] += total_cash

    return data

def add_alameda_crypto_assets(data):
    # Get the indices of 'Stablecoin', 'BTC', 'SOL & APT', 'All Other - Category A' in alameda_df
    indices_alameda = ['Stablecoin', 'BTC', 'SOL & APT', 'All Other - Category A']
    indices_alameda = [data['alameda_df']['index'].index(x) for x in indices_alameda]

    # Get the index of 'Located Assets' in alameda_df
    located_assets_index = data['alameda_df']['columns'].index('Located Assets')

    # Get 'Located Assets' values for the selected indices
    values_alameda = [data['alameda_df']['data'][i][located_assets_index] for i in indices_alameda]

    # Add 'Stablecoin' value from alameda_df to 'Cash / Stablecoin' in ftx_international_crypto_df
    cash_stablecoin_index = data['ftx_intl_crypto_df']['index'].index('Cash / Stablecoin')
    cash_stablecoin_data_index = data['ftx_intl_crypto_df']['columns'].index('Located Assets')
    data['ftx_intl_crypto_df']['data'][cash_stablecoin_index][cash_stablecoin_data_index] += values_alameda[0]

    # Add the selected indices and values to ftx_international_crypto_df
    for i in range(len(indices_alameda)):
        index_alameda = data['alameda_df']['index'][indices_alameda[i]]
        if index_alameda in data['ftx_intl_crypto_df']['index']:
            # If index exists, add the value to the corresponding row
            index_ftx = data['ftx_intl_crypto_df']['index'].index(index_alameda)
            data['ftx_intl_crypto_df']['data'][index_ftx][cash_stablecoin_data_index] += values_alameda[i]
        else:
            # If index does not exist, add a new row with the value
            data['ftx_intl_crypto_df']['index'].append(index_alameda)
            data['ftx_intl_crypto_df']['data'].append([0, values_alameda[i], 0, 0, 0])

    return data

def subcon_non_crypto(data):
    # List of indices to include
    indices = ['Venture Investments', 'Liquid Securities', 'Clawbacks']

    # Get the indices of 'Alameda' and 'Ventures' in assets_df
    column_indices_assets = [data['assets_df']['columns'].index(x) for x in ['Alameda', 'Ventures']]

    # For each index, get the values for 'Alameda' and 'Ventures', sum them up,
    # and add to ftx_intl_crypto_df
    for index in indices:
        # Get the index of the current index in assets_df
        index_assets = data['assets_df']['index'].index(index)

        # Get the values for 'Alameda' and 'Ventures'
        index_values = [data['assets_df']['data'][index_assets][i] for i in column_indices_assets]

        # Sum up the values
        index_values_sum = sum(index_values)

        # If the current index exists in ftx_intl_crypto_df, add the sum to it
        # Else, create a new entry for the current index
        if index in data['ftx_intl_crypto_df']['index']:
            index_ftx = data['ftx_intl_crypto_df']['index'].index(index)
            data['ftx_intl_crypto_df']['data'][index_ftx][1] += index_values_sum
        else:
            data['ftx_intl_crypto_df']['index'].append(index)
            data['ftx_intl_crypto_df']['data'].append([0, index_values_sum, 0, 0, 0])

    return data

def subcon_alameda_dotcom_ventures(data):
    # Define the columns we're interested in
    cols_to_update = ['Located Assets', 'Total Assets', 'Surplus']

    # Extract Alameda and Ventures values
    assets_df_values = {column: dict(zip(data['assets_df']['index'], [item[data['assets_df']['columns'].index(column)] for item in data['assets_df']['data']])) for column in ['Alameda', 'Ventures']}

    # Add Cash to FTX International Cash / Stablecoin column
    data = add_cash_to_stablecoin(data)

    # Add Alameda assets to FTX International crypto DF
    data = add_alameda_crypto_assets(data)

    # Add Venture investments
    data = subcon_non_crypto(data)

    # Zero 'Estimated Receivables' in ftx_international_related_party_df
    est_receivables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index('Estimated Receivables')
    for row in data['ftx_international_related_party_df']['data']:
        row[est_receivables_index_in_related_party_df] = 0

    # Zero 'Estimated Payables' in ftx_international_related_party_df
    est_payables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index(
        'Estimated Payables')
    for row in data['ftx_international_related_party_df']['data']:
        row[est_payables_index_in_related_party_df] = 0

    return data

# def subcon_wrs(data):
#     # Define the columns we're interested in
#     cols_to_update = ['Located Assets', 'Total Assets', 'Surplus']
#
#     # Extract Alameda and Ventures values
#     assets_df_values = {column: dict(zip(data['assets_df']['index'], [item[data['assets_df']['columns'].index(column)] for item in data['assets_df']['data']])) for column in ['WRS']}
#
#     # Extract and update values in FTX International Crypto
#     ftx_us_crypto_index = data['ftx_us_crypto_df']['index']
#     ftx_us_crypto_values = {index: row for index, row in zip(ftx_us_crypto_index, data['ftx_us_crypto_df']['data'])}
#
#     # Find the indices for the columns we're interested in
#     indices_to_update = [data['ftx_us_crypto_df']['columns'].index(col) for col in cols_to_update]
#
#     # Update FTX International Crypto values for given indexes
#     for column, indexes_values in assets_df_values.items():
#         for index, value in indexes_values.items():
#             if index in ftx_intl_crypto_values:
#                 for i in indices_to_update:
#                     ftx_intl_crypto_values[index][i] += value
#             else:
#                 ftx_intl_crypto_values[index] = [0] * len(data['ftx_intl_crypto_df']['columns'])  # initialize with 0 values
#                 for i in indices_to_update:
#                     ftx_intl_crypto_values[index][i] = value
#
#     # Update values from alameda_df, excluding 'Stablecoin'
#     alameda_df_values = dict(zip(data['alameda_df']['index'], data['alameda_df']['data']))
#     for index, row in alameda_df_values.items():
#         if index == 'Stablecoin':
#             continue
#         if index in ftx_intl_crypto_values:
#             for i in indices_to_update:
#                 ftx_intl_crypto_values[index][i] += row[i]
#         else:
#             ftx_intl_crypto_values[index] = [0] * len(data['ftx_intl_crypto_df']['columns'])  # initialize with 0 values
#             for i in indices_to_update:
#                 ftx_intl_crypto_values[index][i] = row[i]
#
#     # Zero 'Estimated Receivables' in ftx_international_related_party_df
#     est_receivables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index('Estimated Receivables')
#     for row in data['ftx_international_related_party_df']['data']:
#         row[est_receivables_index_in_related_party_df] = 0
#
#     # Zero 'Estimated Payables' in ftx_international_related_party_df
#     est_payables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index(
#         'Estimated Payables')
#     for row in data['ftx_international_related_party_df']['data']:
#         row[est_payables_index_in_related_party_df] = 0
#
#     # Write back the updated values to data
#     data['ftx_intl_crypto_df']['index'] = list(ftx_intl_crypto_values.keys())
#     data['ftx_intl_crypto_df']['data'] = list(ftx_intl_crypto_values.values())
#
#     return data

def create_exchange_figs(new_data):
    dotcom_crypto_df = pd.DataFrame(data=new_data["ftx_intl_crypto_df"]["data"],
                                    index=new_data["ftx_intl_crypto_df"]["index"],
                                    columns=new_data["ftx_intl_crypto_df"]["columns"])
    dotcom_related_party_df = pd.DataFrame(data=new_data["ftx_international_related_party_df"]["data"],
                                           index=new_data["ftx_international_related_party_df"]["index"],
                                           columns=new_data["ftx_international_related_party_df"]["columns"])
    ftx_dotcom_exchange_fig = create_exchange_graph(dotcom_crypto_df, dotcom_related_party_df)
    us_crypto_df = pd.DataFrame(data=new_data["ftx_us_crypto_df"]["data"],
                                index=new_data["ftx_us_crypto_df"]["index"],
                                columns=new_data["ftx_us_crypto_df"]["columns"])
    us_related_party_df = pd.DataFrame(data=new_data["ftx_us_related_party_df"]["data"],
                                       index=new_data["ftx_us_related_party_df"]["index"],
                                       columns=new_data["ftx_us_related_party_df"]["columns"])
    ftx_us_exchange_fig = create_exchange_graph(us_crypto_df, us_related_party_df, "US")
    return ftx_dotcom_exchange_fig, ftx_us_exchange_fig

@app.callback(
    Output('ftx_dotcom_exchange_overview_graph', 'figure'),
    Output('ftx_us_exchange_overview_graph', 'figure'),
    Input('exchange-overview-checkbox', 'value'),
    Input('data-store', 'data')
)
def update_exchange_graphs(selected_items, data):
    data_adj = data.copy()
    if 'ZERO_SAM' in selected_items:
        data_adj = zero_out_sam_coins(data_adj)
    if 'SUBCON' in selected_items:
        data_adj = subcon_alameda_dotcom_ventures(data_adj)
    # if 'SUBCON_US' in selected_items:
    #     data_adj = subcon_wrs(data_adj)
    return create_exchange_figs(data_adj)

if __name__ == '__main__':
    app.run_server(debug=True)