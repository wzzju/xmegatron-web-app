import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

from utils import get_or_connect_es, search_data

from .common import create_scatter_figure, create_sidebar, create_time_card

dash.register_page(
    __name__, path='/performance', title='Performance Monitor', name='Performance Monitor'
)


def layout():
    es = get_or_connect_es()
    dense_date, moe_date, dense_meta, moe_meta, _, _, dense_perf, moe_perf = search_data(es=es)

    banner = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.H2("性能监控", className="text-center text-white mb-4"),
                            html.P(
                                "监控XPytorch及其周边代码仓每个合入commit对XMegatron模型训练性能的影响",
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
                [create_time_card("date-range-perf")],
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
                                        figure=create_scatter_figure(
                                            dense_date,
                                            dense_perf,
                                            name='Llama3',
                                            color='#2ecc71',
                                            text=dense_meta,
                                            y_range=[285, 315],
                                        ),
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
                                        figure=create_scatter_figure(
                                            moe_date,
                                            moe_perf,
                                            name='DeepSeek-V3',
                                            color='#3498db',
                                            text=moe_meta,
                                            y_range=[180, 220],
                                        ),
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
        create_sidebar(__name__),
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
    dense_date, moe_date, dense_meta, moe_meta, dense_perf, moe_perf = [], [], [], [], [], []

    if start_date and end_date:
        es = get_or_connect_es()
        dense_date, moe_date, dense_meta, moe_meta, _, _, dense_perf, moe_perf = search_data(
            start_date=start_date, end_date=end_date, es=es
        )

    # 更新Dense图表
    dense_figure = create_scatter_figure(
        dense_date, dense_perf, name='Llama3', color='#2ecc71', text=dense_meta, y_range=[285, 315]
    )

    # 更新MoE图表
    moe_figure = create_scatter_figure(
        moe_date, moe_perf, name='DeepSeek-V3', color='#3498db', text=moe_meta, y_range=[180, 220]
    )

    return dense_figure, moe_figure
