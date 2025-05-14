import json
import pickle
import geopy.distance
import pyproj
from ast import literal_eval
import math
import numpy as np



class HelperFunctions:
    def __init__(self):
        pass

    """wwd"""
    def findCropOptions(self,cropType:str,regionSize:int,startPostion:tuple,maxDistance:int):
        '''pass in the crop type as listed on the dashboard'''
        cropType = cropType.replace("/","_")

        fileStr = "../USE_THIS/MergedData/"+cropType+".json"

        data = None
        with open(fileStr) as f:
            data = json.load(f)

        coordinates = data.keys()
        #print(coordinates)
        validAreas = []

        for c in coordinates:
            key = c
            c = literal_eval(c)
            #print(type(c))
            lat, long = self.convert_3857_to_4326(float(c[0]), float(c[1]))


            #print(startPostion)
            distance = self.getDistance(startPostion, (lat, long))
            #print(distance)
            if distance <= maxDistance and data[key] >= regionSize:
                validAreas.append(c)
        #print("validAreas: ",validAreas)



    def convert_3857_to_4326(self,coord1,coord2):
        #print(coord1,coord2)
        # Create transformer objects for each CRS
        transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326")

        # Example coordinates in EPSG:3857
        #x = 1234567.89
        #y = 9876543.21

        # Transform coordinates
        lon, lat = transformer.transform(coord1, coord2)
        return lat, lon

    def getDistance(self,coord_1,coord_2):
        '''coord_1/2 are tuples with the lat long, DISTANCE MUST BE IN EPSG:4326'''

        #print(geopy.distance.geodesic(coord_1, coord_2).miles)
        return geopy.distance.geodesic(coord_1, coord_2).miles


    def getLocGivenCity(self,city,locList):
        for i in locList:
            if i[0] == city:
                return (i[2],i[3])


    def find_crop_options(self,cropType:str,regionSize:str,startPostion:tuple,maxDistance:float):
        #file = "./tempData/temp.pickle"
        #file = "./tempData/"+cropType+".pickle"
        #file = "./tempData_old/temp.pickle"
        #file = "./tempData/Corn.pickle"


        cropFile = "../USE_THIS/MergedData/"+cropType+".json"
        file = "./tempData/"+cropType+".pickle"
        cropData = None
        print("crop_file"+file)
        with open(file, "rb") as f:
            cropData = pickle.load(f)

        keys = cropData.keys()
       # print("MAX_D",maxDistance)
        #print("R_SIZE: ",regionSize)
        #print(len(keys))
        #exit()

        x_vals = []
        y_vals = []

        retData = {}

        maxDistance = maxDistance / 3959.000
        #print(maxDistance)
        #sizeList = self.smallerThanN(keys,regionSize)
        #print(keys)
        minSize = 0
        maxSize = 0
        if( regionSize == "Small 60-200"):
            minSize = 300
            maxSize = 1500
        elif( regionSize == "Medium 201-400"):
            minSize = 1500
            maxSize = 2000
        elif( regionSize == "Large 401-2000"):
            minSize = 2000
            maxSize = 1000
        elif( regionSize == "Very Large 2001+"):
            minSize = 1000
            maxSize = max(list(keys))

        to_grab = []
        for rsize in keys:
            if rsize <= maxSize and rsize >= minSize:
                tree = cropData[rsize]
                #vals = tree.query([startPostion[0],startPostion[1]],maxDistance)
                #print(startPostion)


                vals = tree.query_radius([[startPostion[1],startPostion[0]]],maxDistance)
                #print("vals")
                #print(vals)
                #print("--")
                #print("?",tree.get_arrays()[2])
                #print(tree.valid_metrics)
                #print(vals)
                #print("---------")
                #print(vals[0])
                #print("---------")
                #print(vals)
                ##print(vals[0])
                #exit()
                if vals[0].size != 0:
                    #self.selectItem(vals[0][0])
                    #print(vals[0].size)
                    #print(vals[0])
                    #exit()
                    #for val in vals[0]:
                    #    x,y = self.selectItem(val)
                    #    x_vals.append(x)
                    #    y_vals.append(y)


                    #x,y = self.selectItems(vals[0],rsize)
                    #print(vals[0],rsize)
                    #exit()
                    to_grab.append((vals[0],rsize))

                    #print(x)
                    #return x, y
                    #retData[rsize] = {"x":x, "y":y}
                #print("---------")


        #return x_vals,y_vals
        #retData = self.selectAllItems(to_grab)
        #return retData
        x_vals,y_vals = self.selectAllItems(to_grab,cropType)
        return x_vals,y_vals

    def selectItem(self,pos):
        fname = "./CropFilesNew/corn.json"
        with open(fname) as f:
            data = json.load(f)

        crops = data["1"]
        #print(crops[pos])
        #print(math.degrees(crops[pos][0]), ",", math.degrees(crops[pos][1]))
        return math.degrees(crops[pos][0]),math.degrees(crops[pos][1])
        #print(self.convert_point_to_dec())

    def selectItems(self, posList,regionSize):
        fname = "./CropFilesNew/corn.json"
        with open(fname) as f:
            data = json.load(f)

       #print(regionSize)
        crops = data[str(regionSize)]
        #crops = data["1"]
        x_val = []
        y_val = []

        for pos in posList:
            x,y = math.degrees(crops[pos][0]),math.degrees(crops[pos][1])
            x_val.append(x)
            y_val.append(y)

        #print(len(x_val))
        return x_val,y_val

    def selectAllItems(self,selectList,cropType):
 
        fname = "./CropFilesNew/corn.json"
        fname = "./CropFilesNew/"+cropType+".json"

        with open(fname) as f:
            data = json.load(f)

        # print(regionSize)
        ret_data = {}
        x_vals = []
        y_vals = []
        #print(selectList)
        #exit()
        print("SELECT LIST")
        print(selectList)
        #exit()

        for crop_data in selectList:
            #print(crop_data)
            #print("CROP_DATA")
            #print(crop_data)
            #exit()
            try:
                points = data[str(crop_data[1])]#crops of a specific size
            except Exception as e:
                break
            #print(points)
            #exit()
            #x_vals = []
            #y_vals = []
            print("POINTS")
            print(points)

            for point in crop_data[0]:
                #print(points[point])
                res = map(math.degrees,points[point])
                #print(list(res))
                points_ = list(res)
                #print(points_)
                #exit()
                x_vals.append(points_[0])
                y_vals.append(points_[1])
                #x_vals.append(points[point][0])
                #y_vals.append(points[point][1])

            #x, y = zip(*points) # converts [[x,y],[x,y],[x,y]] to [[x,x,x],[y,y,y]]
            #ret_data[str(crop_data[1])] = [x_vals,y_vals]

        #return ret_data
        return x_vals,y_vals

        # for pos in posList:
        #    x, y = math.degrees(crops[pos][0]), math.degrees(crops[pos][1])
        #    x_val.append(x)
        #    y_val.append(y)

    # print(len(x_val))
    # return x_val, y_val
    def convert_4326_point_to_rads(self,point):
        return np.radians(point)

    def convert_point_to_dec(self,point):
        return np.degrees(point)

    def smallerThanN(self, intList, intN):
        return [x for x in intList if x < intN]

#10 miles -> 0.002525890376

