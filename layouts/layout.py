from dash import html, dcc
import dash_bootstrap_components as dbc

# def create_layout(app, visualizations):
#     layout = html.Div([
#         html.Div(className='navbar', children=[
#             html.Img(src='/assets/ftx-logo.png', style={'height': '50px', 'width': 'auto'}),
#         ]),
#         html.Div(id='page-content'),
#         html.H3([html.P("Silo Overview ($ in mm)")]),
#         html.Div(visualizations.get("silo_graphs"), className="row"),
#         html.H3([html.P("Exchange Overview ($ in mm)")]),
#         html.Div([
#             *visualizations.get("exchange_graphs"),
#             html.Div(id='checkboxes-container', children=[
#                 dcc.Checklist(
#                     id='exchange-overview-checkbox',
#                     options=[
#                         {'label': 'Item 1', 'value': 'ITEM1'},
#                         {'label': 'Item 2', 'value': 'ITEM2'},
#                     ],
#                     value=['ITEM1', 'ITEM2']  # Default checked items
#                 ),
#             ])
#         ], className="row"),
#         ],
#     style={'font-family': 'Roboto'})
#
#     return layout

def create_layout(visualizations):
    silo_cols = [dbc.Col(graph, width=4) for graph in visualizations.get("silo_graphs")]
    exchange_cols = [dbc.Col(graph, width=3) for graph in visualizations.get("exchange_graphs")]

    layout = html.Div([
        dbc.Navbar([
            dbc.NavbarBrand(dbc.NavLink(html.Img(src='/assets/ftx-logo.png', style={'height': '50px', 'width': 'auto'}), href="#")),
        ], color="dark", dark=True),
        html.H3([html.P("Silo Overview ($ in mm)")]),
        dbc.Row(silo_cols),
        html.H3([html.P("Exchange Overview ($ in mm)")]),
        dbc.Row([
            *exchange_cols,
            dbc.Col([
                html.Div(id='checkboxes-container', children=[
                    dcc.Checklist(
                        id='exchange-overview-checkbox',
                        options=[
                            {'label': 'Zero Out Sam Coins', 'value': 'ITEM1'},
                            {'label': 'Remove Alameda Payables', 'value': 'ITEM2'},
                            {'label': 'Alameda + Dotcom + Ventures Pari Passu', 'value': 'ITEM3'},
                            {'label': 'Alameda Subordinated', 'value': 'ITEM4'},
                        ],
                        value=['ITEM1', 'ITEM2', 'ITEM3', 'ITEM4']  # Default checked items
                    ),
                ])
            ])
        ]),
    ],
    style={'font-family': 'Roboto'})

    return layout