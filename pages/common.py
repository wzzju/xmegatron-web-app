from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pytz
from dash import dcc, html

from elastic_utils import DATE_FMT, TIME_ZONE


def create_sidebar(active_item=None):
    return html.Nav(
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


def create_time_card(id):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("时间范围", className="card-title"),
                    dcc.DatePickerRange(
                        id=id,
                        start_date=(
                            datetime.now(pytz.timezone(TIME_ZONE)) - timedelta(days=30)
                        ).strftime(DATE_FMT),
                        end_date=datetime.now(pytz.timezone(TIME_ZONE)).strftime(DATE_FMT),
                        display_format='YYYY-MM-DD',
                    ),
                ]
            )
        ],
        className="mb-3",
    )


def create_scatter_figure(x, y, name, color, text, y_range):
    return {
        'data': [
            go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=name,
                line=dict(color=color),
                hovertemplate="<b>Value</b>: %{y:.2f}<br>"
                + "%{text}<br>"
                + "<b>Date</b>: %{x}<br>"
                + "<extra></extra>",
                text=text,
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(range=y_range),
        ),
    }
