# Import libraries
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
import os
from shapely.geometry import Polygon, MultiPolygon
from pyproj import Transformer

# Add a helper function to format numbers with commas
def format_number(num):
    return "{:,}".format(num)

# Load the shapefile
# TODO: Load shapefile into script.

# Normalize county names to lowercase
gdf['NAME'] = gdf['NAME'].str.lower()

# Add a capitalized county names column for display
gdf['NAME_DISPLAY'] = gdf['NAME'].str.title()

# Load the CSV file
# TODO: Load file with locations of border crossing and major cities

# Load the feather file
# TODO: Load pixel counts file from CroplandCROS application

# county names to lowercase
df_crops['County'] = df_crops['County'].str.lower()

# Create a mapping of state FIPS codes to state names
state_fips_codes = {
    '48': 'Texas',
    '06': 'California',
    '04': 'Arizona',
    '35': 'New Mexico',
    '40': 'Oklahoma',
    '22': 'Louisiana',
    '05': 'Arkansas'
}

gdf['STATE_NAME'] = gdf['STATEFP'].map(state_fips_codes)

# Filter counties for the specified states
filtered_gdf = gdf[gdf['STATE_NAME'].isin(state_fips_codes.values())]

# Function to create a buffer ring
def create_ring(lat, lon, inner_radius_km, outer_radius_km, num_points=360):
    angles = np.linspace(0, 2 * np.pi, num_points)
    inner_coords = [(lon + (inner_radius_km / 111) * np.cos(a), lat + (inner_radius_km / 111) * np.sin(a)) for a in angles]
    outer_coords = [(lon + (outer_radius_km / 111) * np.cos(a), lat + (outer_radius_km / 111) * np.sin(a)) for a in angles]
    return inner_coords + outer_coords[::-1] + [inner_coords[0]]

# Function to read crop pixels from TIF and VAT DBF files
def read_crop_pixels(state_name, county_name, selected_crop):
    # TODO: Input directory for TIF files
    tif_path = os.path.expanduser(f'YOUR_DIRECTORY_NAME')
    # TODO: Input directory for VAT files
    vat_path = os.path.expanduser(f'YOUR_DIRECTORY_NAME')

    if not os.path.exists(tif_path) or not os.path.exists(vat_path):
        return None, None, None

    with rasterio.open(tif_path) as src:
        transform = src.transform
        img = src.read(1)

    vat_df = gpd.read_file(vat_path)

    # Filter the VAT DataFrame for the selected crop type
    vat_df = vat_df[vat_df['Class_Name'] == selected_crop]

    return img, transform, vat_df

# Function to convert Web Mercator to geographic coordinates
def convert_to_geographic(coords):
    transformer = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)
    geographic_coords = [transformer.transform(coord[0], coord[1]) for coord in coords]
    return geographic_coords

# Function to validate geographic coordinates
def validate_coordinates(coords):
    for lon, lat in coords:
        if not (-125 <= lon <= -65) or not (25 <= lat <= 50):
            return False
    return True

# Function to calculate zoom level based on distance
def calculate_zoom_level(distance):
    if distance <= 20:
        return 11
    elif distance <= 50:
        return 9
    elif distance <= 100:
        return 8
    elif distance <= 200:
        return 7
    elif distance <= 400:
        return 6
    elif distance <= 800:
        return 5
    elif distance <= 1600:
        return 4
    else:
        return 2

# Create the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI], suppress_callback_exceptions=True)
app.config.suppress_callback_exceptions = True
app._dev_tools["dev_tools_ui"] = False  # disable the debug icon
app._dev_tools["dev_tools_props_check"] = False  # disable the property check toolbar

# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# Content style
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Define the sidebar layout
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
            options=[{'label': f"{row['NAME_DISPLAY']}, {row['STATE_NAME']}", 'value': row['GEOID']} for i, row in filtered_gdf.iterrows()],
            placeholder="Select a county",
            style={'width': '100%'}
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Define the main content layout with tabs
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
                                html.Li("Choose a crop type from the 'Choose crop type' dropdown. This will then show the amount of the crop by county."),
                                html.Li("Select a border crossing or city from the 'Select a Location' dropdown."),
                                html.Li("Adjust the travel distance using the 'Distance of Travel (minutes)' slider."),
                                html.Li("Select a county by clicking any of them or from the 'Select a County' dropdown."),
                                html.Li("Switch between the 'Map' and 'County Details' tabs to view the relevant information."),
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
    style=CONTENT_STYLE,
)

# Define the layout of the app
app.layout = html.Div([sidebar, content])

@app.callback(
    Output('map-graph', 'figure'),
    Output('farm-info', 'children'),
    [Input('crop-dropdown', 'value'),
     Input('border-crossing-dropdown', 'value'),
     Input('distance-slider', 'value')]
)
def update_map(selected_crop, selected_crossing, distance):
    # Filter the dataframe for the selected crop
    df_filtered = df_crops[df_crops['CropType'] == selected_crop]

    # Merge the crop data with the geodataframe
    merged_gdf = filtered_gdf.merge(df_filtered, left_on=['STATE_NAME', 'NAME'], right_on=['State', 'County'], how='left')

    # Determine the map center and zoom level
    if selected_crossing is not None:
        selected_location = df_locations.iloc[selected_crossing]
        center = {"lat": selected_location['latitude'], "lon": selected_location['longitude']}

        # Calculate buffer distances
        speed_kmh = 60
        straight_line_distance_km = (distance / 60) * speed_kmh
        zoom = calculate_zoom_level(straight_line_distance_km)

        # Define radii for buffer rings based on the given radius
        r_high_inner = 0.8 * straight_line_distance_km
        r_high_outer = 1.2 * straight_line_distance_km
        r_low_inner_1 = 0.6 * straight_line_distance_km
        r_low_outer_1 = 0.8 * straight_line_distance_km
        r_low_inner_2 = 1.2 * straight_line_distance_km
        r_low_outer_2 = 1.4 * straight_line_distance_km

        # Add buffer rings
        ring_coords_low_1 = create_ring(center['lat'], center['lon'], r_low_inner_1, r_low_outer_1)
        ring_coords_high = create_ring(center['lat'], center['lon'], r_high_inner, r_high_outer)
        ring_coords_low_2 = create_ring(center['lat'], center['lon'], r_low_inner_2, r_low_outer_2)

    else:
        center = {"lat": 31.9686, "lon": -99.9018}
        zoom = 4  # Default zoom level for the initial load

    # Create the updated figure with the heatmap
    fig = px.choropleth_mapbox(merged_gdf, geojson=merged_gdf.geometry, locations=merged_gdf.index,
                               color="PixelCount",
                               mapbox_style="carto-positron",
                               zoom=zoom, center=center,
                               opacity=0.5,
                               labels={'PixelCount': 'Pixel Count'},
                               hover_data={'NAME_DISPLAY': True, 'STATE_NAME': True, 'PixelCount': True})

    # Update hover template
    fig.update_traces(hovertemplate="<b>County: %{customdata[0]}</b><br>" +
                                    "State: %{customdata[1]}<br>" +
                                    "Pixel Count: %{customdata[2]:,}")

    # Add scatter plot for the locations from the CSV
    scatter = go.Scattermapbox(
        lat=df_locations['latitude'],
        lon=df_locations['longitude'],
        mode='markers',
        marker=dict(size=10, color='red'),
        text=[f"{row['port_name']}, {row['state']}" for _, row in df_locations.iterrows()],
        hoverinfo='text',  # Enable hover but no click
        name='Locations'
    )
    fig.add_trace(scatter)

    # Add buffer rings to the map
    if selected_crossing is not None:
        # Low probability region 1
        fig.add_trace(go.Scattermapbox(
            lon=[point[0] for point in ring_coords_low_1],
            lat=[point[1] for point in ring_coords_low_1],
            mode='lines',
            line=dict(width=2, color='lightblue'),
            fill='toself',
            fillcolor='rgba(173, 216, 230, 0.1)',  # Light blue with 10% opacity
            name='Low Probability Region 1',
            legendgroup='Buffer',
            hoverinfo='none'  # Disable hover for this trace
        ))

        # High probability region
        fig.add_trace(go.Scattermapbox(
            lon=[point[0] for point in ring_coords_high],
            lat=[point[1] for point in ring_coords_high],
            mode='lines',
            line=dict(width=2, color='steelblue'),
            fill='toself',
            fillcolor='rgba(70, 130, 180, 0.3)',  # Steel blue with 30% opacity
            name='High Probability Region',
            legendgroup='Buffer',
            hoverinfo='none'  # Disable hover for this trace
        ))

        # Low probability region 2
        fig.add_trace(go.Scattermapbox(
            lon=[point[0] for point in ring_coords_low_2],
            lat=[point[1] for point in ring_coords_low_2],
            mode='lines',
            line=dict(width=2, color='lightblue'),
            fill='toself',
            fillcolor='rgba(173, 216, 230, 0.1)',  # Light blue with 10% opacity
            name='Low Probability Region 2',
            legendgroup='Buffer',
            hoverinfo='none'  # Disable hover for this trace
        ))

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      legend=dict(
                          x=0.01,  # Position the legend to the left
                          y=0.99,  # Position the legend at the top
                          traceorder="normal",
                          font=dict(
                              family="sans-serif",
                              size=12,
                              color="black"
                          ),
                          bgcolor="White",
                          bordercolor="Black",
                          borderwidth=2
                      ))

    # Farm info
    farm_info = f"Buffer region represents a straight-line distance assuming 60 km/h (~37 mph)."
    
    return fig, farm_info

@app.callback(
    Output('county-dropdown', 'value'),
    Input('map-graph', 'clickData')
)
def update_county_dropdown(click_data):
    if click_data is not None and 'customdata' in click_data['points'][0]:
        customdata = click_data['points'][0]['customdata']
        county_name, state_name = customdata[0], customdata[1]
        geo_id = filtered_gdf[(filtered_gdf['NAME'] == county_name.lower()) & (filtered_gdf['STATE_NAME'] == state_name)]['GEOID'].values[0]
        return geo_id
    return None

@app.callback(
    Output('county-graph', 'figure'),
    [Input('county-dropdown', 'value'),
     Input('crop-dropdown', 'value')]
)
def update_county_graph(selected_county, selected_crop):
    if selected_county is None:
        return go.Figure()

    # Filter the gdf for the selected county
    county_gdf = filtered_gdf[filtered_gdf['GEOID'] == selected_county]

    if county_gdf.empty:
        return go.Figure()

    try:
        # Ensure the geometries are properly processed for map display
        county_outline = county_gdf.geometry.unary_union

        fig = go.Figure()

        if isinstance(county_outline, Polygon):
            x, y = county_outline.exterior.xy
            fig.add_trace(go.Scattermapbox(
                lon=list(x),
                lat=list(y),
                mode='lines',
                line=dict(width=2, color='blue'),
                name='County Outline'
            ))
        elif isinstance(county_outline, MultiPolygon):
            for poly in county_outline:
                x, y = poly.exterior.xy
                fig.add_trace(go.Scattermapbox(
                    lon=list(x),
                    lat=list(y),
                    mode='lines',
                    line=dict(width=2, color='blue'),
                    name='County Outline'
                ))

        # Calculate the centroid for the center of the map
        county_gdf = county_gdf.to_crs(epsg=3857)  # Convert to a projected CRS
        centroid = county_gdf.geometry.centroid.iloc[0]  # Extract the centroid
        centroid = gpd.GeoSeries([centroid], crs=county_gdf.crs).to_crs(epsg=4326).iloc[0]  # Convert back to geographic CRS

        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=10,  # Increased zoom level from 8 to 10
                center={"lat": centroid.y, "lon": centroid.x},
            ),
            height=600,  # Set a fixed height for the map
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        # Read and display crop pixels for the selected county and crop type
        state_name = county_gdf['STATE_NAME'].values[0]
        county_name = county_gdf['NAME'].values[0]

        img, transform, vat_df = read_crop_pixels(state_name, county_name, selected_crop)

        if img is not None and not vat_df.empty:
            crop_coords = []
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    if img[i, j] in vat_df['Value'].values:
                        x, y = rasterio.transform.xy(transform, i, j)
                        crop_coords.append((x, y))

            if crop_coords:
                # Convert to geographic coordinates
                geographic_coords = convert_to_geographic(crop_coords)
                valid_coords = validate_coordinates(geographic_coords)
                if not valid_coords:
                    print("Error: Coordinates are out of the expected range.")

                fig.add_trace(go.Scattermapbox(
                    lon=[coord[0] for coord in geographic_coords],
                    lat=[coord[1] for coord in geographic_coords],
                    mode='markers',
                    marker=dict(size=4, color='green', opacity=0.5),
                    hoverinfo='text',
                    text=[f"({coord[1]:.5f}, {coord[0]:.5f})" for coord in geographic_coords],
                    name='Crop Pixels'
                ))

    except Exception as e:
        fig = go.Figure()

    return fig

# New callback to switch tabs
@app.callback(
    Output('tabs', 'active_tab'),
    [Input('county-dropdown', 'value'),
     Input('map-graph', 'clickData')]
)
def switch_tab_on_selection(county_value, click_data):
    if click_data is not None and 'customdata' in click_data['points'][0]:
        # Check if the clicked point is a county shape
        if click_data['points'][0]['curveNumber'] == 0:
            return 'tab-county-details'
        else:
            return 'tab-map'
    if county_value:
        return 'tab-county-details'
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
