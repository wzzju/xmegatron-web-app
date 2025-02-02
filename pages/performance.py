from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pytz
from dash import dcc, html
from dash.dependencies import Input, Output

from elastic_utils import get_or_connect_es, search_data

from .home import get_sidebar

dash.register_page(
    __name__, path='/performance', title='Performance Monitor', name='Performance Monitor'
)


def layout():
    es = get_or_connect_es()
    dense_date, moe_date, dense_commit, moe_commit, _, _, dense_perf, moe_perf = search_data(es=es)

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
                                        id='date-range-perf',
                                        start_date=(
                                            datetime.now(pytz.timezone('Asia/Shanghai'))
                                            - timedelta(days=30)
                                        ).strftime("%a %b %-d %H:%M:%S %Y %z"),
                                        end_date=datetime.now(
                                            pytz.timezone('Asia/Shanghai')
                                        ).strftime("%a %b %-d %H:%M:%S %Y %z"),
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
                                        id='perf-dense-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dense_date,
                                                    y=dense_perf,
                                                    mode='lines+markers',
                                                    name='Llama3',
                                                    line=dict(color='#2ecc71'),
                                                    hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                                                    + "<b>Commit ID</b>: %{text}<br>"
                                                    + "<b>Date</b>: %{x}<br>"
                                                    + "<extra></extra>",
                                                    text=dense_commit,
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[285, 315]),
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
                                        id='perf-moe-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=moe_date,
                                                    y=moe_perf,
                                                    mode='lines+markers',
                                                    name='DeepSeek-V3',
                                                    line=dict(color='#3498db'),
                                                    hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                                                    + "<b>Commit ID</b>: %{text}<br>"
                                                    + "<b>Date</b>: %{x}<br>"
                                                    + "<extra></extra>",
                                                    text=moe_commit,
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[180, 220]),
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


@dash.callback(
    [Output('perf-dense-graph', 'figure'), Output('perf-moe-graph', 'figure')],
    [Input('date-range-perf', 'start_date'), Input('date-range-perf', 'end_date')],
)
def update_graphs(start_date, end_date):
    dense_date, moe_date, dense_commit, moe_commit, dense_perf, moe_perf = [], [], [], [], [], []

    if start_date and end_date:
        es = get_or_connect_es()
        dense_date, moe_date, dense_commit, moe_commit, _, _, dense_perf, moe_perf = search_data(
            start_date=start_date, end_date=end_date, es=es
        )

    # 更新Dense图表
    dense_figure = {
        'data': [
            go.Scatter(
                x=dense_date,
                y=dense_perf,
                mode='lines+markers',
                name='Llama3',
                line=dict(color='#2ecc71'),
                hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                + "<b>Commit ID</b>: %{text}<br>"
                + "<b>Date</b>: %{x}<br>"
                + "<extra></extra>",
                text=dense_commit,
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=[285, 315]),
        ),
    }

    # 更新MoE图表
    moe_figure = {
        'data': [
            go.Scatter(
                x=moe_date,
                y=moe_perf,
                mode='lines+markers',
                name='DeepSeek-V3',
                line=dict(color='#3498db'),
                hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                + "<b>Commit ID</b>: %{text}<br>"
                + "<b>Date</b>: %{x}<br>"
                + "<extra></extra>",
                text=moe_commit,
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=[180, 220]),
        ),
    }

    return dense_figure, moe_figure
