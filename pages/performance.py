from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output

from .home import get_sidebar

dash.register_page(
    __name__, path='/performance', title='Performance Monitor', name='Performance Monitor'
)


def get_dummy_perf_data():
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
    dense_scroes = np.round(np.random.uniform(300, 310, 30), 2)
    moe_scroes = np.round(np.random.uniform(200, 210, 30), 2)
    return dates, dense_scroes, moe_scroes


def layout():
    dates, dense_scroes, moe_scroes = get_dummy_perf_data()

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
                                        id='perf-dense-graph',
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
                                        id='perf-moe-graph',
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


@dash.callback(
    [Output('perf-dense-graph', 'figure'), Output('perf-moe-graph', 'figure')],
    [Input('date-range-perf', 'start_date'), Input('date-range-perf', 'end_date')],
)
def update_graphs(start_date, end_date):
    dates, dense_scores, moe_scores = get_dummy_perf_data()

    if start_date and end_date:
        # 转换日期字符串为datetime对象以进行比较
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # 过滤日期范围内的数据
        filtered_data = [
            (d, ds, ms)
            for d, ds, ms in zip(dates, dense_scores, moe_scores)
            if start_date <= datetime.strptime(d, '%Y-%m-%d') <= end_date
        ]
        if filtered_data:
            dates, dense_scores, moe_scores = zip(*filtered_data)

    # 更新Dense图表
    dense_figure = {
        'data': [
            go.Scatter(
                x=dates,
                y=dense_scores,
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
    }

    # 更新MoE图表
    moe_figure = {
        'data': [
            go.Scatter(
                x=dates,
                y=moe_scores,
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
    }

    return dense_figure, moe_figure
