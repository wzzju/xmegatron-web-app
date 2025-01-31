from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, clientside_callback, dcc, html

dash.register_page(__name__, path='/', title='Performance Monitor', name='Performance Monitor')


def get_sidebar(active_item=None):
    nav = html.Nav(
        id="sidebar",
        className="active",
        children=[
            html.Div(
                className="custom-menu",
                children=[
                    html.Button(
                        [
                            html.I(className="fa fa-bars"),
                            html.Span("Toggle Menu", className="sr-only"),
                        ],
                        type="button",
                        id="sidebarCollapse",
                        className="btn btn-primary",
                    )
                ],
            ),
            html.Div(
                className="flex-column p-4 nav nav-pills",
                children=[
                    html.A(
                        [
                            html.Img(
                                src='static/nav.png', alt='', width=48, height=48, className='mx-2'
                            ),
                            html.Span("XMegatron", className='fs-4'),
                        ],
                        className='d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none',
                        href='/',
                    ),
                    html.Hr(),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Performance",
                            href="/",
                            className='text-white',
                            active=True if active_item == 'pages.home' else False,
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Accuracy",
                            href="/accuracy",
                            className='text-white',
                            active=True if active_item == 'pages.accuracy' else False,
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "About",
                            href="/about",
                            className='text-white',
                            active=True if active_item == 'pages.about' else False,
                        )
                    ),
                ],
            ),
        ],
    )
    return nav


def generate_sample_data():
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    dense_scroes = np.round(np.random.uniform(300, 310, 30), 2)
    moe_scroes = np.round(np.random.uniform(200, 210, 30), 2)
    return dates, dense_scroes, moe_scroes


def layout():
    dates, dense_scroes, moe_scroes = generate_sample_data()

    banner = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.H2("性能监控", className="text-center text-white mb-4"),
                            html.P(
                                "监控XMLIR代码仓每个合入commit对XMegatron模型训练性能的影响",
                                className="text-center text-white",
                            ),
                        ],
                        className="py-4",
                        style={"background-color": "#2c3e50"},
                    )
                ]
            )
        ]
    )

    filters = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("时间范围", className="card-title"),
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        start_date=dates[-1],
                                        end_date=dates[0],
                                        display_format='YYYY-MM-DD',
                                    ),
                                ]
                            )
                        ],
                        className="mb-3",
                    )
                ],
                width=12,
            )
        ]
    )

    tabs = dbc.Tabs(
        [
            dbc.Tab(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("训练吞吐", className="card-title"),
                                    dcc.Graph(
                                        id='performance-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dates,
                                                    y=dense_scroes,
                                                    mode='lines+markers',
                                                    name='Llama3',
                                                    line=dict(color='#2ecc71'),
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[260, 360]),
                                            ),
                                        },
                                    ),
                                ]
                            )
                        ],
                        className="mb-3",
                    )
                ],
                label="Dense",
                tab_id="tab-1",
                className="mt-3",
            ),
            dbc.Tab(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("训练吞吐", className="card-title"),
                                    dcc.Graph(
                                        id='correctness-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dates,
                                                    y=moe_scroes,
                                                    mode='lines+markers',
                                                    name='DeepSeek-V3',
                                                    line=dict(color='#3498db'),
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[160, 260]),
                                            ),
                                        },
                                    ),
                                ]
                            )
                        ]
                    )
                ],
                label="MoE",
                tab_id="tab-2",
                className="mt-3",
            ),
        ],
        active_tab="tab-1",
        className="mt-3",
    )

    layout = [
        get_sidebar(__name__),
        html.Div(
            [
                dbc.Container(banner, fluid=True, className="mb-4"),
                dbc.Container([filters, tabs], fluid="md"),
            ],
            className='content',
        ),
    ]

    return layout


clientside_callback(
    """
    function(yes, name){
        if (name === 'active') {
            return '';
        } else if (name === '') {
            return 'active';
        }
    }
    """,
    Output('sidebar', 'className'),
    Input('sidebarCollapse', 'n_clicks'),
    State('sidebar', 'className'),
)
