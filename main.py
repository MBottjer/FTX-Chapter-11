from dash import dash, Output, Input, exceptions, dcc, html
from data_processing.data import load_data
from components.visualizations import create_visualizations
from layouts.layout import create_layout

dataframes = load_data()
dataframes_json = {k: v.to_dict(orient='split') for k, v in dataframes.items()}  # Convert to JSON serializable format
visualizations = create_visualizations(dataframes)

app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Roboto&display=swap', 'https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = html.Div([
    dcc.Store(id='data-store', data=dataframes_json),  # Store data in dcc.Store
    create_layout(create_visualizations(dataframes))  # Call your create_visualizations function here
])

# @app.callback(
#     Output('ftx_dotcom_exchange-overview-graph', 'figure'),
#     Output('ftx_us_exchange-overview-graph', 'figure'),
#     Input('exchange-overview-checkbox', 'value')
# )
# def update_exchange_graphs(selected_items):
#     if not selected_items:
#         raise exceptions.PreventUpdate
#
#     ftx_dotcom_exchange_fig = get_exchange_graph('ftx_dotcom_exchange', selected_items)
#     ftx_us_exchange_fig = get_exchange_graph('ftx_us_exchange', selected_items)
#
#     return ftx_dotcom_exchange_fig, ftx_us_exchange_fig

if __name__ == '__main__':
    app.run_server(debug=True)