import math
import random
import webbrowser
from pydoc import Helper

import numpy as np

from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import csv
import pandas as pd


from DashBoardNew.HelperFunctions import HelperFunctions
from DashBoardNew.StyleGuide import StyleGuide


import plotly.express as px
import plotly.graph_objects as go
import json

app = Dash()
items = []

CONTENT_STYLE = StyleGuide.get_content_style()
SIDEBAR_STYLE = StyleGuide.get_sidebar_style()
content = StyleGuide.get_main_content_style()
helperFuncs = HelperFunctions()



with open('./bands.csv', newline='') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        items.append(row)
        #items.append(dbc.DropdownMenuItem(row[1]))

locations = []
with open('../southfinal2.csv', newline='') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        locations.append(row)

start_cols = ["port_name","state","latitude","longitude"]
start_pos_df = pd.DataFrame(locations, columns=start_cols)


columns = ["Value","Crop"]
df = pd.DataFrame.from_records(items, columns=columns)

farmSizes = ["Small 60-200","Medium 201-400","Large 401-2000","Very Large 2001+"]
sidebar = StyleGuide.get_sidebar_content(df,start_pos_df,farmSizes)
#content = StyleGuide.get_content_style()
app.layout = html.Div([sidebar,content])

@app.callback(
    Output('map-graph','figure',allow_duplicate=True),
    Output(component_id='output', component_property='children'),
    [Input('button', 'n_clicks')],
    [Input(component_id='start_position', component_property='value')],
    [Input(component_id='crop_type', component_property='value')],
    [Input(component_id='region_size', component_property='value')],
    [Input(component_id='max_distance', component_property='value')],
    prevent_initial_call=True
    #state=[State(component_id='my-id', component_property='value')]
              )
def search_valid_areas(n_clicks,start_position,crop_type,region_size,max_distance):
    if n_clicks is None:
        raise PreventUpdate

    print("Triggered")
    print(start_position)
    print(crop_type)
    #print(locations)

    #https://www.google.com/maps/place/26°25'18.0%22N+98°55'28.9%22W/@26.0703656,-104.0382773,1391998m/data=!3m1!1e3!4m4!3m3!8m2!3d26.4216627!4d-98.9246993?entry=ttu&g_ep=EgoyMDI1MDIyNS4wIKXMDSoASAFQAw%3D%3D



    startPosTuple = helperFuncs.getLocGivenCity(start_position,locations)
    startPosTuple = float(startPosTuple[0]),float(startPosTuple[1])
    print("startPosTuple: ",startPosTuple)
    #stat_pos_43 = helperFuncs.convert_3857_to_4326(startPosTuple[0], startPosTuple[1])

    start_rads = helperFuncs.convert_4326_point_to_rads(startPosTuple[0]),helperFuncs.convert_4326_point_to_rads(startPosTuple[1])
    print("start_rads: ",start_rads)

    start_deg = helperFuncs.convert_point_to_dec(start_rads[0]),helperFuncs.convert_point_to_dec(start_rads[1])
    print("start_deg: ",start_deg)
    #helperFuncs.findCropOptions(cropType=crop_type,regionSize=region_size,startPostion=startPosTuple,maxDistance=max_distance)


    #y,x  = helperFuncs.find_crop_options(cropType=crop_type,regionSize=region_size,startPostion=start_rads,maxDistance=max_distance)
    ###
    #fig.add_trace(go.Scattermapbox(lat=x, lon=y, mode='markers',marker=dict(size=10, color='red')))
    ###
    #retDict = helperFuncs.find_crop_options(cropType=crop_type,regionSize=region_size,startPostion=start_rads,maxDistance=max_distance)
    x_vals,y_vals = helperFuncs.find_crop_options(cropType=crop_type,regionSize=region_size,startPostion=start_rads,maxDistance=max_distance)
    ##Setting up the graphs

    # 26.42576550896004,-99.1074166610202
    with open('./US_Counties/geojson-counties-fips.json') as f:
        counties = json.load(f)

    fig = px.choropleth_map(geojson=counties,
                            color_continuous_scale="Viridis",
                            range_color=(0, 12),
                            map_style="carto-positron", #center={"lat": 37.0902, "lon": -95.7129},
                             center={"lat": startPosTuple[0], "lon": startPosTuple[1]},
                            opacity=0.5,

                            )

    #print(retDict.keys())
    #print(retDict)
    fig.add_trace(go.Scattermapbox(lat=[startPosTuple[0]],lon=[startPosTuple[1]], mode='markers',marker=dict(size=20,color=f'RGBA(255,0,0,1)'),name=start_position))

    #sortedKeys = sorted(retDict.keys())
    #gradient = np.diff(sortedKeys).tolist()
    """num = len(sortedKeys)
    if num > 25:
        num = 25
        gradient = 255/25
    else:
        gradient = 255/num
    currVal = 0
    curElem = 0"""




        #fig.add_trace(go.Scattermapbox(lat=retDict[key]["y"], lon=retDict[key]["x"], mode='markers',
        #                                   marker=dict(size=10, color=f'RGBA(1,0,{c_val},1)',
        #                                               ),
        #                                   name=name))


    #print(len(retDict.keys()))

    #for v in sortedKeys:
        #print(v)
        #fig.add_trace(go.Scattermapbox(lat=retDict[v][1], lon=retDict[v][0], mode='markers',
#
#                                                               marker=dict(size=10, color=f'RGBA(1,0,{1},1)',
#                                                                                  ),
#                                                                    name=v))
    """
        fig.add_trace(go.Scattermapbox(
            lat=retDict[v][1],
            lon=retDict[v][0],
            mode='markers',
            marker=dict(
                size=10,
                color="blue"
            ),
            name=v,
        ))
    """
    fig.add_trace(go.Scattermapbox(
        lat=y_vals,
        lon=x_vals,
        mode='markers',
        marker=dict(
            size=10,
            color="blue"
        ),
        name = region_size

    ))


    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    #config = {"displayModeBar": False}
    #fig.update_layout(config = config)

    return fig, 1


@app.callback(
Output('map-graph', 'figure',allow_duplicate=True),
        [Input('map-graph', 'clickData')],
    prevent_initial_call=True
)
def openMap(clickData):
    if clickData is None:
        raise PreventUpdate
    #print("HERE!_____")

    #print(clickData)
    pointData = clickData['points'][0]
    url = f"https://maps.google.com/?q={pointData['lat']},{pointData['lon']}"

    #url = clickData['points'][0]['customdata'][0]
    webbrowser.open_new_tab(url)
    return




def convert_to_deg(coord):
    num = 360 - (coord / math.pi) * 180
    #num1 = 360 - (coord0 / math.pi) * 180
    return num

if __name__ == '__main__':
    #Radians = 1,000 miles / 3,959 miles = approximately 0.25 radians.


    #10 miles -> 0.002525890376
    #each pixel is 0.2 acre
    # 1 acher is 43560 square feet, 208x208
    #0.2 acre = 8,712 square feet, 93.3x93.3

    #avg farm size 444 acers  --usda

    #small family farms average 231 acres; large family farms average 1,421 acres and the very large farm average acreage is 2,086.
    # ^ michigan state
    app.run(debug=True)

#small family pixel --> 1155
#large family family --> 7105
#very large --> 10430

#family farms make up 98%

"""
 df = pd.DataFrame(sortedKeys)
    #q = df.quantile([0.25, 0.5, 0.75])
    q = df.quantile([0, 0.25, 0.5, 0.75, 1])

    for key in sortedKeys:
        c_val = 0
        name = ""
        if key > q[0].values[0] and key <= q[0].values[1]:
            c_val = 63.75
            name = "q1"
        elif key > q[0].values[1] and key <= q[0].values[2]:
            c_val = 127.5
            name = "q2"
        elif key > q[0].values[2] and key <= q[0].values[3]:
            c_val = 191.25
            name = "q3"
        elif key > q[0].values[3] and key <= q[0].values[4]:
            c_val = 255
            name = "q4"

"""