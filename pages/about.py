import json

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from .home import get_sidebar

dash.register_page(__name__, path='/about', title='About', name='About')

with open('pages/text.json') as f:
    about = json.load(f)['about']


def layout():
    banner = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Img(src='static/logo.jpg', alt='logo', className="banner-image"),
                            html.Div(
                                [
                                    html.H1("About XMegatron"),
                                ],
                                className='overlay-text',
                            ),
                        ],
                        className='banner-container',
                    )
                ]
            ),
        ]
    )

    layout = [
        get_sidebar(__name__),
        html.Div(
            [
                dbc.Container(banner, fluid=True),
                dbc.Container(
                    dbc.Row(
                        dbc.Col(
                            dcc.Markdown(about, style={"textAlign": "justify"}),
                            md=10,
                            sm=24,
                            className='mt-4 ms-4',
                        )
                    ),
                    fluid='md',
                ),
            ],
            className='content',
        ),
    ]

    return layout
