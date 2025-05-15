"""import numpy as np
import pyproj
def convert_3857_to_4326(coord1, coord2):
    # print(coord1,coord2)
    # Create transformer objects for each CRS
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326")

    # Example coordinates in EPSG:3857
    # x = 1234567.89
    # y = 9876543.21

    # Transform coordinates
    lon, lat = transformer.transform(coord1, coord2)
    return lat, lon


def convert_point_to_rads(point):
    return np.radians(point)

def convert_point_to_dec(point):
    return np.degrees(point)

if __name__ == "__main__":
    start_pos = ("26.403928","-99.018981")

    #epsg_4326 = (convert_3857_to_4326(float(start_pos[0]), float(start_pos[1])))
    #print("epsg_4326: ", epsg_4326)

    rads = convert_point_to_rads(float(start_pos[0])), convert_point_to_rads(float(start_pos[1]))
    print("rads: ",rads)

    dec = convert_point_to_dec(rads[0]), convert_point_to_dec(rads[1])
    print("dec: ",dec)
"""
import json
import numpy as np
import pandas as pd
from boltons.statsutils import describe


def calculate_sum(n):
    if n==1:
        return 1
    else:
        return n+calculate_sum(n-1)

if __name__ == "__main__":
    val = [[-1.6771064483483582, 0.5291865177979665], [-1.6753011857011115, 0.509477506635627], [-1.59525655732813, 0.5924386207585409], [-1.5933375016540356, 0.5853043715799852], [-1.5854559323811017, 0.6144226728267558], [-1.6754927623576683, 0.5150680479743135], [-1.5967536787004082, 0.6218146100277807], [-1.6039955446530612, 0.6044820349376364], [-1.573137028933396, 0.6334442713533046], [-1.7903956716432368, 0.6026572130903505], [-1.5977716803295408, 0.6119155469581412], [-1.5859809449815847, 0.6067042197810678], [-1.5886525715082649, 0.6050107373949577], [-1.7207472356677826, 0.5039243503643014], [-1.575521028518131, 0.6197054448255016], [-1.7060747508803775, 0.46276845958545954], [-1.703313724794743, 0.5057425224188471]]
    x, y = zip(*val)
    print(x)
    #print(df)
    #print(df.describe())

    #print(df.tail(5))
"""
    print(df[-1])
    print(df[-2])
    print(df[-3])
    print(df[-4])"""


"""
count   2731.000000
mean    1924.290736
std     2080.749198
min        1.000000
25%      683.500000
50%     1394.000000
75%     2466.500000
max    37208.000000
"""