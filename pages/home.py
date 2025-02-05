import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, clientside_callback, dcc, html

from utils import get_or_connect_es, search_data

from .common import create_scatter_figure, create_sidebar, create_time_card

dash.register_page(__name__, path='/', title='Accuracy Monitor', name='Accuracy Monitor')


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
                [create_time_card("date-range-acc")],
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
                                        figure=create_scatter_figure(
                                            dense_date,
                                            dense_acc,
                                            name='Llama3',
                                            color='#e74c3c',
                                            text=dense_meta,
                                            y_range=[0.5, 3],
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
                                    html.H5("前十步loss均值", className="card-title"),
                                    dcc.Graph(
                                        id='acc-moe-graph',
                                        figure=create_scatter_figure(
                                            moe_date,
                                            moe_acc,
                                            name='DeepSeek-V3',
                                            color='#9b59b6',
                                            text=moe_meta,
                                            y_range=[5, 8],
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
    dense_figure = create_scatter_figure(
        dense_date, dense_acc, name='Llama3', color='#e74c3c', text=dense_meta, y_range=[0.5, 3]
    )

    # 更新MoE图表
    moe_figure = create_scatter_figure(
        moe_date, moe_acc, name='DeepSeek-V3', color='#9b59b6', text=moe_meta, y_range=[5, 8]
    )

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
