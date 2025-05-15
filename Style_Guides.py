from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
class Style_Guides:


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
    def get_content_style():
        CONTENT_STYLE = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
        }
        return CONTENT_STYLE

    @staticmethod
    def get_sidebar_layout(df_crops,df_locations,filtered_gdf):
        sidebar = html.Div(
            [
                html.H2("Controls", className="display-4"),
                html.Hr(),
                html.P(
                    "Choose crop type:", className="lead"
                ),
                dcc.Dropdown(
                    id='crop-dropdown',
                    options=[{'label': crop, 'value': crop} for crop in df_crops['CropType'].unique()],
                    value=df_crops['CropType'].unique()[0],
                    style={'width': '100%'}
                ),
                html.Hr(),
                html.P(
                    "Select a Location:", className="lead"
                ),
                dcc.Dropdown(
                    id='border-crossing-dropdown',
                    options=[{'label': row['port_name'], 'value': i} for i, row in df_locations.iterrows()],
                    placeholder="Select a border crossing",
                    style={'width': '100%'}
                ),
                html.Hr(),
                html.P(
                    "Distance of Travel (minutes):", className="lead"
                ),
                dcc.Slider(
                    id='distance-slider',
                    min=0,
                    max=240,
                    step=30,
                    value=60,
                    marks={i: f"{i}" for i in range(0, 241, 60)}  # Adjusted to show fewer marks
                ),
                html.Hr(),
                html.P(
                    "Select a county:", className="lead"
                ),
                dcc.Dropdown(
                    id='county-dropdown',
                    options=[{'label': f"{row['NAME_DISPLAY']}, {row['STATE_NAME']}", 'value': row['GEOID']} for i, row
                             in filtered_gdf.iterrows()],
                    placeholder="Select a county",
                    style={'width': '100%'}
                ),
            ],
            #style=SIDEBAR_STYLE,
            style=Style_Guides.get_sidebar_style(),
        )
        return sidebar


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
                                    dcc.Graph(id='map-graph'),  # Removed clickmode
                                    html.Div(id='farm-info', style={'padding': '2rem 1rem'})
                                ]
                            )
                        ]),
                        dbc.Tab(label='County Details', tab_id='tab-county-details', children=[
                            dcc.Loading(
                                id="loading-county-details",
                                type="default",
                                children=[
                                    dcc.Graph(id='county-graph', style={'height': '80vh'})
                                ]
                            )
                        ]),
                        dbc.Tab(label='Instructions', tab_id='tab-instructions', children=[
                            html.Div(
                                [
                                    html.H3("How to Use the Dashboard"),
                                    html.Ol([
                                        html.Li(
                                            "Choose a crop type from the 'Choose crop type' dropdown. This will then show the amount of the crop by county."),
                                        html.Li(
                                            "Select a border crossing or city from the 'Select a Location' dropdown."),
                                        html.Li(
                                            "Adjust the travel distance using the 'Distance of Travel (minutes)' slider."),
                                        html.Li(
                                            "Select a county by clicking any of them or from the 'Select a County' dropdown."),
                                        html.Li(
                                            "Switch between the 'Map' and 'County Details' tabs to view the relevant information."),
                                    ])
                                ],
                                style={'padding': '2rem 1rem'}
                            )
                        ]),
                    ],
                    id='tabs',
                    active_tab='tab-map'
                )
            ],
            #style=CONTENT_STYLE,
            style = Style_Guides.get_content_style(),
        )

        return content