from datetime import datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pytz
from dash import Input, Output, State, clientside_callback, dcc, html

from elastic_utils import get_or_connect_es, search_data

dash.register_page(__name__, path='/', title='Accuracy Monitor', name='Accuracy Monitor')


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
                            "Accuracy",
                            href="/",
                            className='text-white',
                            active=True if active_item == 'pages.home' else False,
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Performance",
                            href="/performance",
                            className='text-white',
                            active=True if active_item == 'pages.performance' else False,
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


def layout():
    es = get_or_connect_es()
    dense_date, moe_date, dense_meta, moe_meta, dense_acc, moe_acc, _, _ = search_data(es=es)

    banner = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.H2("精度监控", className="text-center text-white mb-4"),
                            html.P(
                                "监控XPytorch及其周边代码仓每个合入commit对XMegatron模型训练精度的影响",
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
                                        id='date-range-acc',
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
                                    html.H5("前十步loss均值", className="card-title"),
                                    dcc.Graph(
                                        id='acc-dense-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=dense_date,
                                                    y=dense_acc,
                                                    mode='lines+markers',
                                                    name='Llama3',
                                                    line=dict(color='#e74c3c'),
                                                    hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                                                    + "%{text}<br>"
                                                    + "<b>Date</b>: %{x}<br>"
                                                    + "<extra></extra>",
                                                    text=dense_meta,
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[0.5, 3]),
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
                                        id='acc-moe-graph',
                                        figure={
                                            'data': [
                                                go.Scatter(
                                                    x=moe_date,
                                                    y=moe_acc,
                                                    mode='lines+markers',
                                                    name='DeepSeek-V3',
                                                    line=dict(color='#9b59b6'),
                                                    hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                                                    + "%{text}<br>"
                                                    + "<b>Date</b>: %{x}<br>"
                                                    + "<extra></extra>",
                                                    text=moe_meta,
                                                )
                                            ],
                                            'layout': go.Layout(
                                                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                                hovermode='closest',
                                                plot_bgcolor='white',
                                                paper_bgcolor='white',
                                                yaxis=dict(range=[5, 8]),
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
    [Output('acc-dense-graph', 'figure'), Output('acc-moe-graph', 'figure')],
    [Input('date-range-acc', 'start_date'), Input('date-range-acc', 'end_date')],
)
def update_graphs(start_date, end_date):
    dense_date, moe_date, dense_meta, moe_meta, dense_acc, moe_acc = [], [], [], [], [], []

    if start_date and end_date:
        es = get_or_connect_es()
        dense_date, moe_date, dense_meta, moe_meta, dense_acc, moe_acc, _, _ = search_data(
            start_date=start_date, end_date=end_date, es=es
        )

    # 更新Dense图表
    dense_figure = {
        'data': [
            go.Scatter(
                x=dense_date,
                y=dense_acc,
                mode='lines+markers',
                name='Llama3',
                line=dict(color='#e74c3c'),
                hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                + "%{text}<br>"
                + "<b>Date</b>: %{x}<br>"
                + "<extra></extra>",
                text=dense_meta,
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=[0.5, 3]),
        ),
    }

    # 更新MoE图表
    moe_figure = {
        'data': [
            go.Scatter(
                x=moe_date,
                y=moe_acc,
                mode='lines+markers',
                name='DeepSeek-V3',
                line=dict(color='#9b59b6'),
                hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                + "%{text}<br>"
                + "<b>Date</b>: %{x}<br>"
                + "<extra></extra>",
                text=moe_meta,
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=[5, 8]),
        ),
    }

    return dense_figure, moe_figure


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
