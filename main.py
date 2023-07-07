from dash import dash, Output, Input, exceptions
from data_processing.data import load_data
from components.visualizations import create_visualizations
from layouts.layout import create_layout

dataframes = load_data()
visualizations = create_visualizations(dataframes)

app = dash.Dash(__name__, external_stylesheets=['https://fonts.googleapis.com/css2?family=Roboto&display=swap', 'https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = create_layout(visualizations)

@app.callback(
    Output('ftx_dotcom_exchange-overview-graph', 'figure'),
    Output('ftx_us_exchange-overview-graph', 'figure'),
    Input('exchange-overview-checkbox', 'value')
)
def update_exchange_graphs(selected_items):
    if not selected_items:
        raise exceptions.PreventUpdate

    ftx_dotcom_exchange_fig = get_exchange_graph('ftx_dotcom_exchange', selected_items)
    ftx_us_exchange_fig = get_exchange_graph('ftx_us_exchange', selected_items)

    return ftx_dotcom_exchange_fig, ftx_us_exchange_fig

if __name__ == '__main__':
    app.run_server(debug=True)