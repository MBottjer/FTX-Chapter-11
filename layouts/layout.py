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
                dbc.NavItem(dbc.NavLink("Venture Portfolio", href="/new-page", style={"max-width": "160px",
                                                                                      "text-overflow": "ellipsis",
                                                                                      "white-space": "nowrap",
                                                                                      "overflow": "hidden",
                                                                                      "margin-right": "20px",
                                                                                      "vertical-align": "middle"}),
                            style={"margin-top": "5px"}),
                dbc.NavLink(
                    html.Img(src='/assets/arceau.svg', className="align-self-center ml-auto", style={"height": "14px"}),
                    href="https://www.arceau.com/",
                    target="_blank",
                ),
            ], color="dark", dark=True),
            html.Div([
                html.H3([html.P("Chapter 11")]),
                html.P(
                    "On the 11th November 2022, FTX, the world’s third largest cryptocurrency exchange filed for Chapter"
                    " 11 bankruptcy protection in the United States. At Arceau, we have "
                    "been closely monitoring the proceedings and have compiled an interactive report on the identified "
                    "assets which predominantly consist of cash, crypto, property and venture invesments."
                ),
                html.P(
                    "From the latest amended customer schedules, we estimate the total value of customer claims to be "
                    "$10,917,696,560 for FTX International and $277,324,083 for FTX US. Combining Alameda creditors, "
                    "compiling the list of venture assets and monitoring the estate's latest financial reports "
                    "we present possible recoveries. Note, restructurings are subject to uncertainty and we welcome any "
                    "and all feedback (feel free to message us on twitter @mbottjer and @LouisOrigny)."
                ),
                html.Br(),
                html.H3([html.P("FTX Assets - Silo Overview ($ in mm)")]),
                html.P("Below, we look at the assets and liabilities of all four silos. We use prices as of 11/11/2022 "
                       "9am PST. Key takeaways include:"),
                html.Ul([
                    html.Li("FTX's assets are predominantly dominated by a claim against Alameda Ltd. and secondly by "
                            "Category B crypto assets which include: SRM, MAPS, OXY etc."),
                    html.Li("WRS' topco holds a cash balance of $599M, has a significant claim against Alameda Ltd. and "
                            "the exchange holds solely Category A crypto assets."),
                    html.Li("Alameda has over $2B in liquid assets and a significant portion of the venture book."),
                ]),
                dbc.Row(silo_cols),
                html.Br(),
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
