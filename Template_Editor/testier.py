# app.py

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[
            html.Div([
                html.H3('Content of Tab 1')
            ])
        ], className='my-custom-tab')
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)