from dash import dash, Output, Input, exceptions, dcc, html, State
from data_processing.data import load_data, get_close_price
from components.visualizations import create_visualizations, create_exchange_graph, calculate_recovery_rate, \
    create_exchange_crypto_pie_chart, CATEGORY_B_ASSETS
from layouts.layout import create_layout
import pandas as pd

dataframes = load_data()
dataframes_json = {k: v.to_dict(orient='split') for k, v in dataframes.items()}  # Convert to JSON serializable format
visualizations = create_visualizations(dataframes)

app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter&display=swap', 'https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server
app.layout = html.Div([
    dcc.Store(id='data-store', data=dataframes_json), # Store data in dcc.Store
    dcc.Store(id='recovery-rate-store', data={}),
    dcc.Store(id='hidden-div-checkboxes', storage_type='session'),
    create_layout(visualizations)  # Call your create_visualizations function here
])
# app.config.suppress_callback_exceptions = True

def zero_out_sam_coins(data):
    sam_coins = ["Crypto - Category B"] + CATEGORY_B_ASSETS

    for key in data:
        if 'index' in data[key] and 'data' in data[key]:
            indices = data[key]['index']
            for coin in sam_coins:
                if coin in indices:
                    index = indices.index(coin)
                    data[key]['data'][index] = [0]*len(data[key]['data'][index])
    return data

def add_cash_to_stablecoin(data, exchange, columns, target_column='Located Assets', recovery_rate=1.0):
    cash_df = data["cash_df"]

    # Get the indices of the columns
    column_indices = [cash_df['columns'].index(column) for column in columns]

    # Sum up all values in the specified columns
    total_cash = sum(sum(row[i] for i in column_indices) for row in cash_df['data'])

    # Get the index of Cash / Stablecoin in ftx_intl_crypto_df
    cash_stablecoin_index = data[exchange]['index'].index('Cash / Stablecoin')

    # Get the column index of 'Located Assets'
    target_column_index = data[exchange]['columns'].index(target_column)

    # Add total_cash to Cash / Stablecoin values in the 'Located Assets' column in ftx_intl_crypto_df
    data[exchange]['data'][cash_stablecoin_index][target_column_index] += round(total_cash*recovery_rate)

    return data

def add_alameda_crypto_assets(data, recovery_rate=1.0):
    # Get the indices of 'Stablecoin', 'BTC', 'SOL & APT', 'All Other - Category A' in alameda_df
    indices_alameda = ['Stablecoin', 'BTC', 'SOL', 'APT', 'All Other - Category A']
    indices_alameda = [data['alameda_df']['index'].index(x) for x in indices_alameda]

    # Get the index of 'Located Assets' in alameda_df
    located_assets_index = data['alameda_df']['columns'].index('Located Assets')

    # Get 'Located Assets' values for the selected indices
    values_alameda = [data['alameda_df']['data'][i][located_assets_index] for i in indices_alameda]

    # Add 'Stablecoin' value from alameda_df to 'Cash / Stablecoin' in ftx_international_crypto_df
    cash_stablecoin_index = data['ftx_intl_crypto_df']['index'].index('Cash / Stablecoin')
    cash_stablecoin_data_index = data['ftx_intl_crypto_df']['columns'].index('Located Assets')
    data['ftx_intl_crypto_df']['data'][cash_stablecoin_index][cash_stablecoin_data_index] += round(values_alameda[0]*recovery_rate)

    # Add crypto assets value from alameda_df to 'Crypto - Category A' in ftx_international_crypto_df
    cash_stablecoin_index = data['ftx_intl_crypto_df']['index'].index('Crypto - Category A')
    cash_stablecoin_data_index = data['ftx_intl_crypto_df']['columns'].index('Located Assets')
    for value in values_alameda[1:]:
        data['ftx_intl_crypto_df']['data'][cash_stablecoin_index][cash_stablecoin_data_index] += round(value*recovery_rate)

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

def subcon_non_crypto(data, silos, exchange, indices, recovery_rate=1.0):
    # Get the indices of 'Alameda' and 'Ventures' in assets_df
    column_indices_assets = [data['assets_df']['columns'].index(x) for x in silos]

    # For each index, get the values for 'Alameda' and 'Ventures', sum them up,
    # and add to ftx_intl_crypto_df
    for index in indices:
        # Get the index of the current index in assets_df
        index_assets = data['assets_df']['index'].index(index)

        # Get the values for 'Alameda' and 'Ventures'
        index_values = [data['assets_df']['data'][index_assets][i] for i in column_indices_assets]

        # Sum up the values
        index_values_sum = round(sum(index_values)*recovery_rate)

        # If the current index exists in ftx_intl_crypto_df, add the sum to it
        # Else, create a new entry for the current index
        if index in data[exchange]['index']:
            index_ftx = data[exchange]['index'].index(index)
            data[exchange]['data'][index_ftx][1] += index_values_sum
        else:
            data[exchange]['index'].append(index)
            data[exchange]['data'].append([0, index_values_sum, 0, 0, 0])

    return data

def subcon_alameda_dotcom_ventures(data):

    # Add Cash to FTX International Cash / Stablecoin column
    data = add_cash_to_stablecoin(data, 'ftx_intl_crypto_df', ["Alameda", "Ventures"])

    # Add Alameda assets to FTX International crypto DF
    data = add_alameda_crypto_assets(data)

    # Add Venture investments
    indices = ['Venture Investments', 'Liquid Securities', 'Clawbacks']
    data = subcon_non_crypto(data, ['Alameda', 'Ventures'], "ftx_intl_crypto_df", indices)

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

def calc_alameda_recovery(data):
    alameda_asset_index = data["assets_df"]['columns'].index('Alameda')
    alameda_liabs_index = data["liabilities_df"]['columns'].index('Alameda')
    total_alameda_assets = sum(row[alameda_asset_index] for row in data["assets_df"]['data'])
    total_alameda_liabs = sum(row[alameda_liabs_index] for row in data["liabilities_df"]['data'])
    alameda_recovery = total_alameda_assets / total_alameda_liabs
    return alameda_recovery

def claim_alameda(data):
    alameda_recovery_rate = calc_alameda_recovery(data)

    # Add Cash to FTX International Cash / Stablecoin column
    data = add_cash_to_stablecoin(data, 'ftx_intl_crypto_df', ["Alameda"], recovery_rate=alameda_recovery_rate)

    # Add Alameda assets to FTX International crypto DF
    data = add_alameda_crypto_assets(data, alameda_recovery_rate)

    # Add Venture investments
    indices = ['Venture Investments', 'Liquid Securities', 'Clawbacks']
    data = subcon_non_crypto(data, ["Alameda"], "ftx_intl_crypto_df", indices, alameda_recovery_rate)

    # Zero 'Estimated Receivables' in ftx_international_related_party_df
    est_receivables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index('Estimated Receivables')
    for row in data['ftx_international_related_party_df']['data']:
        row[est_receivables_index_in_related_party_df] = 0

    # Zero 'Estimated Payables' in ftx_international_related_party_df
    est_payables_index_in_related_party_df = data['ftx_international_related_party_df']['columns'].index(
        'Estimated Payables')
    for row in data['ftx_international_related_party_df']['data']:
        row[est_payables_index_in_related_party_df] = 0

    # Net 'Estimated Payables' in ftx_us_related_party_df
    est_payables_col_index_us = data['ftx_us_related_party_df']['columns'].index(
        'Estimated Payables')
    est_receivables_col_index_us = data['ftx_us_related_party_df']['columns'].index(
        'Estimated Receivables')
    est_payables_alameda_index_us = data['ftx_us_related_party_df']['index'].index(
        'Alameda Research LLC')
    data['ftx_us_related_party_df']['data'][est_payables_alameda_index_us][est_payables_col_index_us] = data['ftx_us_related_party_df']['data'][est_payables_alameda_index_us][est_payables_col_index_us] - \
                                                                                                            data['ftx_us_related_party_df']['data'][est_payables_alameda_index_us][est_receivables_col_index_us]
    data['ftx_us_related_party_df']['data'][est_payables_alameda_index_us][est_receivables_col_index_us] = 0

    return data

def subcon_wrs(data):

    # Add Cash to FTX International Cash / Stablecoin column
    data = add_cash_to_stablecoin(data, "ftx_us_crypto_df", ["WRS"])

    # Add Assets
    indices = ['Related Party Receivables', 'Subsidiary Sales']
    data = subcon_non_crypto(data, ["WRS"], "ftx_us_crypto_df", indices)

    # est_payables_index_in_related_party_df = data['ftx_us_related_party_df']['columns'].index(
    #     'Estimated Payables')
    # for row in data['ftx_us_related_party_df']['data']:
    #     row[est_payables_index_in_related_party_df] = 0

    return data


def adjust_category_a(df):
    sum_indices = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'MATIC', 'TRX', 'All Other - Category A',
               'DOGE', 'LINK', 'SHIB', 'UNI', 'ALGO', 'PAXG', 'ETHW', 'WETH', 'APT']
    total_assets = 0
    for idx in sum_indices:
        try:
            index_pos = df['index'].index(idx)
            total_assets += df['data'][index_pos][1]  # Add the 'Located Assets' value
        except ValueError:
            continue  # Skip if the index doesn't exist in the dataframe

    try:
        category_a_idx = df['index'].index('Crypto - Category A')
        df['data'][category_a_idx][1] = total_assets  # Update the 'Located Assets' value for 'Crypto - Category A'
    except ValueError:
        print("Index 'Crypto - Category A' not found!")

def update_prices(df_as_dict, ticker, close_price):
    # Find the index of the current ticker in the dataframe's 'index' list
    try:
        ticker_idx = df_as_dict['index'].index(ticker)
    except ValueError:
        print(f"Ticker {ticker} not found!")
        return

    # Calculate the "Located Assets" value
    quantity = df_as_dict['data'][ticker_idx][6]  # The "Quantity" column is at index 6
    located_assets = round((close_price * quantity)/1000000.0)

    # Update the "Located Assets" column in the dictionary for the current ticker
    df_as_dict['data'][ticker_idx][1] = located_assets

def inject_last_close_crypto_prices(data):
    category_a_crypto = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'MATIC', 'TRX', 'DOGE', 'APT']
    for ticker in category_a_crypto:
        # Get the close price for the current ticker
        close_price = get_close_price(ticker, '1d')

        # Update prices in both dataframes
        update_prices(data["ftx_intl_crypto_df"], ticker, close_price)
        update_prices(data["ftx_us_crypto_df"], ticker, close_price)
        update_prices(data["alameda_df"], ticker, close_price)
    adjust_category_a(data["ftx_intl_crypto_df"])
    adjust_category_a(data["ftx_us_crypto_df"])
    return data

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

    ftx_intl_crypto_pie_chart = create_exchange_crypto_pie_chart(dotcom_crypto_df, "FTX.COM - Cash & Crypto")
    ftx_us_crypto_pie_chart = create_exchange_crypto_pie_chart(us_crypto_df, "FTX.US - Cash & Crypto")

    ftx_intl_recovery_rate = calculate_recovery_rate(dotcom_crypto_df, dotcom_related_party_df)
    ftx_us_recovery_rate = calculate_recovery_rate(us_crypto_df, us_related_party_df)
    recovery_rates = {
        'ftx_intl': ftx_intl_recovery_rate,
        'ftx_us': ftx_us_recovery_rate,
    }
    return ftx_dotcom_exchange_fig, ftx_us_exchange_fig, ftx_intl_crypto_pie_chart, ftx_us_crypto_pie_chart, recovery_rates


# Callback to manage checkbox selections
@app.callback(
    Output('exchange-overview-checkbox', 'value'),
    Output('hidden-div-checkboxes', 'data'),
    [
        Input('exchange-overview-checkbox', 'value'),
        Input('exchange-overview-checkbox-pricing', 'value')
    ],
    [State('hidden-div-checkboxes', 'data')]
)
def update_checkboxes(new_values, pricing_checkbox_value, old_values):
    # Detect whether a value has just been added
    added_values = list(set(new_values) - set(old_values if old_values else []))

    # If CLAIM_ALAMEDA is just selected, uncheck SUBCON and SUBCON_US
    if 'CLAIM_ALAMEDA' in added_values and ('SUBCON' in new_values or 'SUBCON_US' in new_values):
        new_values = [value for value in new_values if value not in ['SUBCON', 'SUBCON_US']]

    # If either SUBCON or SUBCON_US is just selected, uncheck CLAIM_ALAMEDA
    if ('SUBCON' in added_values or 'SUBCON_US' in added_values) and 'CLAIM_ALAMEDA' in new_values:
        new_values.remove('CLAIM_ALAMEDA')

    return new_values, new_values


@app.callback(
    Output('ftx_dotcom_exchange_overview_graph', 'figure'),
    Output('ftx_us_exchange_overview_graph', 'figure'),
    Output('ftx_intl_pie_chart', 'figure'),
    Output('ftx_us_pie_chart', 'figure'),
    Output('recovery-rate-store', 'data'),
    [
        Input('exchange-overview-checkbox', 'value'),
        Input('exchange-overview-checkbox-pricing', 'value')
    ],
    [Input('data-store', 'data')]
)
def update_exchange_graphs(selected_items, pricing_items, data):
    data_adj = data.copy()

    if 'CATEGORY_A_UPDATE' in pricing_items:
        # Adjust the 'data_adj' dictionary as needed
        data_adj = inject_last_close_crypto_prices(data_adj)

    if 'CLAIM_ALAMEDA' in selected_items:
        data_adj = claim_alameda(data_adj)
    if 'ZERO_SAM' in selected_items:
        data_adj = zero_out_sam_coins(data_adj)
    if 'SUBCON' in selected_items:
        data_adj = subcon_alameda_dotcom_ventures(data_adj)
    if 'SUBCON_US' in selected_items:
        data_adj = subcon_wrs(data_adj)

    return create_exchange_figs(data_adj)

@app.callback(
    Output('ftx_dotcom_recovery_rate', 'children'),
    Output('ftx_us_recovery_rate', 'children'),
    Input('recovery-rate-store', 'data'),
    State('exchange-overview-checkbox', 'value')  # Get the current state of checkbox
)
def update_recovery_rates(data, selected_items):
    if not data or data is None or (all(item not in selected_items for item in ['CLAIM_ALAMEDA', 'SUBCON', 'SUBCON_US']) and len(selected_items) <= 1):  # Add condition
        return "Recovery Rate: N/A%", "Recovery Rate: N/A%"

    ftx_intl_recovery_rate = "N/A"
    ftx_us_recovery_rate = "N/A"

    if 'SUBCON' in selected_items or 'CLAIM_ALAMEDA' in selected_items:
        rate = data.get('ftx_intl', "N/A")
        ftx_intl_recovery_rate = str(round(float(rate))) if rate != "N/A" else "N/A"
        rate = data.get('ftx_us', "N/A")
        ftx_us_recovery_rate = str(round(min(float(rate), 100))) if rate != "N/A" else "N/A"

    if 'SUBCON_US' in selected_items:
        rate = data.get('ftx_us', "N/A")
        ftx_us_recovery_rate = str(round(min(float(rate), 100))) if rate != "N/A" else "N/A"

    return f"Recovery Rate: {ftx_intl_recovery_rate}%", f"Recovery Rate: {ftx_us_recovery_rate}%"


if __name__ == '__main__':
    app.run_server(debug=True)
