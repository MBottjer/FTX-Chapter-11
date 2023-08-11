from dash import html, dcc
import dash_bootstrap_components as dbc


def create_layout(visualizations):
    silo_cols = [dbc.Col(graph) for graph in visualizations.get("silo_graphs")]
    exchange_cols = [dbc.Col(graph) for graph in visualizations.get("exchange_graphs")]
    exchange_pie_chart_cols = [dbc.Col(graph) for graph in visualizations.get("exchange_pie_charts")]

    layout = html.Div(className='background', children=[
        html.Div([
            dbc.Navbar([
                dbc.NavbarBrand(
                    dbc.NavLink(html.Img(src='/assets/ftx-logo.png', height="32", className="align-self-center"),
                                href="#"),
                    className="mr-auto"
                ),
                dbc.NavLink(
                    html.Img(src='/assets/arceau.svg', className="align-self-center ml-auto", style={"height": "14px"}),
                    href="https://www.arceau.com/",
                    target="_blank",
                ),
            ], color="dark", dark=True),
            html.Div([
                html.H3([html.P("Chapter 11")]),
                html.P(
                    "On the 11th November 2022, FTX, the world’s third largest cryptocurrency exchange by trading volume"
                    " filed for Chapter 11 bankruptcy protection in the United States. At Arceau, we have "
                    "been closely monitoring the proceedings and have compiled an interactive report on the identified "
                    "assets which predominantly consist of cash, crypto, property and venture invesments."
                ),
                html.P(
                    "From the latest amended customer schedules, we estimate the total value of customer claims to be "
                    "$10.9B for FTX International and $277.3M for FTX US. Combining Alameda creditors, "
                    "compiling the list of venture assets and monitoring the estate's latest financial reports "
                    "we present possible recoveries."
                ),
                html.Br(),
                html.H3([html.P("FTX Assets - Silo Overview ($ in mm)")]),
                html.P("Below, we look at the assets and liabilities of all four silos. We use prices as of 11/11/2022 "
                       "9am PST. Category A Crypto Assets are tokens with (i) a market capitalization of at least $15M "
                       "and (ii) an average daily trading volume of at least $1M during the past 30 days, in each case "
                       "measured at February 2, 2023. Category B Assets are tokens that do not satisfy the test for "
                       "Category A Assets or which are largely held and/or controlled by the estate. Key takeaways "
                       "include:"),
                html.Ul([
                    html.Li("FTX's assets are predominantly dominated by a claim against Alameda Ltd. and secondly by "
                            "Category B crypto assets which include: SRM, MAPS, OXY etc."),
                    html.Li("WRS' topco holds a cash balance of $599M, has a significant claim against Alameda Ltd. and "
                            "the exchange holds solely Category A crypto assets."),
                    html.Li("Alameda has over $2B in liquid assets and a significant portion of the venture book."),
                ]),
                dbc.Row(silo_cols),
                html.Br(),
                html.H3([html.P("Venture Assets")]),
                html.P("We think FTX invested ~$5.1B into venture assets and funds across WRS, Alameda and Dotcom. "
                       "We have marked the value of these investments down to $1.7B. Below is a summary:"),
                html.Br(),
                html.Div(visualizations["ventures_table"]),
                html.Br(),
                html.H3([html.P("Exchange Recoveries ($ in mm)")]),
                html.Br(),
                html.P("Initially presented is the reported state of assets and liabilities for each exchange. "
                       "To understand potential recoveries, toggle the options under Recovery Toggles. "),
                html.Ul([
                    # html.Li("Receive Claims Against Alameda: assumes that FTX.COM receives its recoverable "
                    #         "value from Alameda as does FTX.US"),
                    html.Li("Subcon: Alameda + Dotcom + Ventures: representative of substantive consolidation across"
                            " the three silos, combining their assets and liabiltiies"),
                    html.Li("Subcon: WRS: collapses the WRS silo, making the cash available in the topco available to "
                            "the exchange"),
                    html.Li("Subordinate Sam Coins: assigns a value of 0 to crypto assets and liabilities deemed "
                            "Category B."),
                ]),
                html.Br(),
                html.Div([
                    html.Div([exchange_cols[0], exchange_cols[1]], style={'width': '1100px'}),
                    html.Div([
                        html.P("Recovery Toggles:"),
                        dcc.Checklist(
                            id='exchange-overview-checkbox',
                            options=[
                                # {'label': 'Receive Claims Against Alameda', 'value': 'CLAIM_ALAMEDA'},
                                {'label': 'Subcon: Alameda + Dotcom + Ventures', 'value': 'SUBCON'},
                                {'label': 'Subcon: WRS', 'value': 'SUBCON_US'},
                                {'label': 'Subordinate Sam Coins', 'value': 'ZERO_SAM'},
                            ],
                            value=[],
                            className="my-checklist",  # Add this
                        ),
                        html.Br(),
                        html.P("Latest Prices Toggles:"),
                        dcc.Checklist(
                            id='exchange-overview-checkbox-pricing',
                            options=[
                                {'label': "Crypto - Category A (Not Including 'All Other - Category A')", 'value': 'CATEGORY_A_UPDATE'},
                                {'label': 'Liquid Securities', 'value': 'LIQUID_SEC_UPDATE'},
                            ],
                            value=[],
                            className="my-checklist",  # Add this
                        ),
                    ], style={'marginTop': '45px', 'marginLeft': '30px'}),
                ], style={'display': 'flex', 'overflow': 'auto'}),  # use flex display and allow horizontal scrolling
                dbc.Row(html.Div([exchange_pie_chart_cols[0], exchange_pie_chart_cols[1]], style={'width': '1100px', 'marginTop': '10px'}),)
            ], style={'padding': '10px'}),
        ]),
    ], style={'fontFamily': 'Inter', 'padding': '0px'})

    return layout
