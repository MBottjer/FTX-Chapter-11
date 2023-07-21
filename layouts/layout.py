from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(visualizations):
    silo_cols = [dbc.Col(graph, width=4) for graph in visualizations.get("silo_graphs")]
    exchange_cols = [dbc.Col(graph, width=3) for graph in visualizations.get("exchange_graphs")]

    layout = html.Div(className='gradient-background', children=[  # <--- Add this className
        html.Div([
            dbc.Navbar([
                dbc.NavbarBrand(dbc.NavLink(html.Img(src='/assets/ftx-logo.png', style={'height': '50px', 'width': 'auto'}), href="#")),
            ], color="dark", dark=True),
            html.Div([
                html.H3([html.P("Exchange Overview ($ in mm)")]),
                dbc.Row([
                    *exchange_cols,
                        html.Div(id='checkboxes-container', children=[
                            dcc.Checklist(
                                id='exchange-overview-checkbox',
                                options=[
                                    {'label': 'Subordinate Sam Coins', 'value': 'ZERO_SAM'},
                                    {'label': 'Subcon: Alameda + Dotcom + Ventures', 'value': 'SUBCON'},
                                    {'label': 'Subordinate Alameda', 'value': 'ALAMEDA_SUB'},
                                ],
                                value=[]  # Default checked items
                            ),
                    ]),
                ]),
                html.H3([html.P("Silo Overview ($ in mm)")]),
                dbc.Row(silo_cols),
            ], style={'marginTop': '20px'}),  # adjust as needed
        ]),
    ], style={'fontFamily': 'Roboto', 'padding': '0px'})  # added padding: 0px

    return layout