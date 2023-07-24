from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(visualizations):
    silo_cols = [dbc.Col(graph) for graph in visualizations.get("silo_graphs")]
    exchange_cols = [dbc.Col(graph) for graph in visualizations.get("exchange_graphs")]

    layout = html.Div(className='background', children=[
        html.Div([
            dbc.Navbar([
                dbc.NavbarBrand(
                    dbc.NavLink(html.Img(src='/assets/ftx-logo.png', height="32", className="align-self-center"),
                                href="#"),
                    className="mr-auto"
                ),
                html.A(html.Img(src='/assets/arceau.svg', height="32", className="align-self-center ml-auto"), href="https://www.arceau.com/", target="_blank"),
            ], color="dark", dark=True),
            html.Div([
                html.H3([html.P("Exchange Overview ($ in mm)")]),
                html.H3([html.P("FTX Assets - Silo Overview ($ in mm)")]),
                dbc.Row(silo_cols),
                html.H3([html.P("Exchange Recoveries ($ in mm)")]),
                html.Div([
                    html.Div([exchange_cols[0], exchange_cols[1]], style={'width': '1100px'}),
                    html.Div(
                        dcc.Checklist(
                            id='exchange-overview-checkbox',
                            options=[
                                {'label': 'Subordinate Sam Coins', 'value': 'ZERO_SAM'},
                                {'label': 'Subcon: Alameda + Dotcom + Ventures', 'value': 'SUBCON'},
                                {'label': 'Subcon: WRS', 'value': 'SUBCON_US'},
                            ],
                            value=[],
                            className="my-checklist",  # Add this
                        )
                    ),
                ], style={'display': 'flex', 'overflow': 'auto'}),  # use flex display and allow horizontal scrolling
            ], style={'padding': '10px'}),
        ]),
    ], style={'fontFamily': 'Inter', 'padding': '0px'})

    return layout





