import dash
from dash import html


def layout(page_background):
    return [
        html.Div([
            html.H1('Welcome to Py2MCNP Editor!'),
            html.P(
                "This is a project designed to produce Monte Carlo N-Particle transport code (MCNP) card decks "
                "using Python"),
        ], style={'backgroundColor': page_background, 'height': '100vh', 'marginLeft': '20px'})
    ]
