from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html

from .home import get_sidebar

dash.register_page(__name__, path='/accuracy', title='Accuracy Monitor', name='Accuracy Monitor')


def generate_sample_data():
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    dense_scroes = [round(5 + (5 * (i % 4) / 3), 2) for i in range(30)]
    moe_scroes = [round(7 + (8 * (i % 3) / 2), 2) for i in range(30)]
    dense_scroes = np.round(np.random.uniform(30, 31, 30), 2)
    moe_scroes = np.round(np.random.uniform(51, 52, 30), 2)
    return dates, dense_scroes, moe_scroes


def layout():
    dates, dense_scroes, moe_scroes = generate_sample_data()

    banner = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.H2("精度监控", className="text-center text-white mb-4"),
                            html.P(
                                "监控XMLIR代码仓每个合入commit对XMegatron模型训练精度的影响",
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
                                        id='date-range-accuracy',
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
                                    html.H5("前十步loss均值", className="card-title"),
                                    dcc.Graph(
                                        id='accuracy-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dates,
                                                    y=dense_scroes,
                                                    mode='lines+markers',
                                                    name='Llama3',
                                                    line=dict(color='#e74c3c'),
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[28, 35]),
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
                                    html.H5("前十步loss均值", className="card-title"),
                                    dcc.Graph(
                                        id='precision-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dates,
                                                    y=moe_scroes,
                                                    mode='lines+markers',
                                                    name='DeepSeek-V3',
                                                    line=dict(color='#9b59b6'),
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[46, 56]),
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
