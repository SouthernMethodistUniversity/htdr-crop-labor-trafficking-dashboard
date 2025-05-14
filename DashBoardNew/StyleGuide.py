from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

class StyleGuide:
    def __init__(self):
        pass

    @staticmethod
    def get_sidebar_style():
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "background-color": "#f8f9fa",
        }
        return SIDEBAR_STYLE

    @staticmethod
    def get_sidebar_content(df, start_pos_df,farmSizes):
        sidebar = html.Div([
            dbc.CardGroup([
                dbc.Label("Region Size in (acres)", size="md"),
                dcc.Dropdown(
                    farmSizes,
                    id="region_size",
                )
                #dbc.Input(
                #    id="region_size",
                #    placeholder="Region Size",
                #    type="number",
                    # className="form-control",
                #)
            ]),
            dbc.CardGroup([
                dbc.Label("Crop Type", size="md"),
                dcc.Dropdown(
                    df["Crop"],
                    id="crop_type",
                )
            ]),
            dbc.CardGroup([
                dbc.Label("Starting Position", size="md"),
                dcc.Dropdown(
                    start_pos_df["port_name"],
                    id="start_position",
                )
            ]),
            dbc.CardGroup([
                dbc.Label("Max Distance", size="md"),
                dbc.Input(
                    id="max_distance",
                    placeholder="Max Distance (miles)",
                    type="number",
                    # className="form-control",
                )
            ]),
            dbc.CardGroup([
                # dcc.Input(id='my-id', value='initial value', type="text"),
                html.Button('Click Me', id='button'),
            ]),
            dbc.CardGroup([
                dbc.Label(id="output"),
            ])


        ],
        style=StyleGuide.get_sidebar_style())
        return sidebar

    @staticmethod
    def get_content_style():
        CONTENT_STYLE = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
        }
        return CONTENT_STYLE

    @staticmethod
    def get_main_content_style():
        '''Define the main content layout with tabs'''
        content = html.Div(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(label='Map', tab_id='tab-map', children=[
                            dcc.Loading(
                                id="loading-map",
                                type="default",
                                children=[
                                    dcc.Graph(id='map-graph',
                                              figure={},
                                              config={
                                                  'scrollZoom': True
                                              }),  # Removed clickmode

                                    html.Div(id='farm-info', style={'padding': '2rem 1rem'})
                                ]
                            )
                        ])


                    ],
                    id='tabs',
                    active_tab='tab-map'
                )
            ],
            # style=CONTENT_STYLE,
            style=StyleGuide.get_content_style(),
        )

        return content