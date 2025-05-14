import json
import os
import pickle
import sys
import geopy.distance
import numpy as np
import pyproj
from ast import literal_eval
import scipy.spatial.ckdtree
import sklearn

#from scipy.spatial import cKDTree
import scipy.spatial.distance as spdist
#from sklearn.neighbors import BallTree
#from sklearn.neighbors import BallTree
from sklearn.metrics import pairwise

from sklearn import metrics
from sklearn.neighbors import BallTree

from DashBoardNew.HelperFunctions import *
from pyproj import Proj, transform
print(sklearn.__version__)


#import sklearn.neighbors.BallTree as ball_tree
class DataSorting:
    #tree = KDTree()
    newDict = {}
    def __init__(self,filepath,newFileName):
        self.file = filepath
        self.newFileName = newFileName
        self.helperFuncs = HelperFunctions()

#TODO
# Drop some decimal places? find out time save
# Preconvert all cordinates
# put them in dict of lists? with the key being the right size

# have a driver function to call all funcs on each coord

    def convert_3857_to_4326(self, coord1, coord2):
        # print(coord1,coord2)
        # Create transformer objects for each CRS
        transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326")

        # Example coordinates in EPSG:3857
        # x = 1234567.89
        # y = 9876543.21

        # Transform coordinates
        long,lat  = transformer.transform(coord1, coord2)
        return lat, long

    def convert_to_4326(self, x, y):
        proj_3857 = Proj(init="epsg:3857")
        proj_4326 = Proj(init="epsg:4326")

        # Your given coordinates (assuming EPSG:3857)
        x, y = -10675364.691149253, 3614249.40022952

        # Convert to Lat/Lon
        lon, lat = transform(proj_3857, proj_4326, x, y)
        return (lat,lon)

    def getDistance(self,coord_1,coord_2):
        '''coord_1/2 are tuples with the lat long, DISTANCE MUST BE IN EPSG:4326'''

        #print(geopy.distance.geodesic(coord_1, coord_2).miles)
        return geopy.distance.geodesic(coord_1, coord_2).miles



    def driver(self):
        #tempDict = {}
        with open(self.file, "r") as f:
            cropData = json.load(f)

        keys = cropData.keys()

        tempDict = {}
        for c in keys:

            key = c
            coords = literal_eval(c)
            # print(type(c))
            #lat, long = self.convert_3857_to_4326(float(c[0]), float(c[1]))

            spaceSize = cropData[c]

            tempDict.setdefault(spaceSize, [])
            #print(c)
            #coords = self.convert_3857_to_4326(float(coords[0]), float(coords[1]))
            #c_4326 = self.helperFuncs.convert_3857_to_4326(coords[1],coords[0])
            #print(c_4326)
            #exit()
            #c_4326 = self.convert_to_4326(coords[0], coords[1])
            c_4326 = self.helperFuncs.convert_3857_to_4326(coords[0], coords[1])
            c_rads = self.helperFuncs.convert_4326_point_to_rads(c_4326[0]),self.helperFuncs.convert_4326_point_to_rads(c_4326[1])
            c_dec = self.helperFuncs.convert_point_to_dec(c_rads[0]),self.helperFuncs.convert_point_to_dec(c_rads[1])
            #use for testing
            #print("c_4326: ",c_4326)
            #print("c_rads: ",c_rads)
            #print("c_dec: ",c_dec)


            #exit()
            #print("c_rads: ",c_rads)
            #print("c_dex: ", c_dec)
            tempDict[spaceSize].append(c_rads)
            #exit()
            #print(tuple(np.radians(coordsFloat)))
            #self.newDict.setdefault(spaceSize,KDTree(balanced_tree=True))
            #self.newDict[spaceSize]
            #tempDict.setdefault(cropData[c], []).append((lat, long))

        #cropFileNew = "../CropFilesNew/corn.json"
        cropFileNew = "../CropFilesNew/"+self.newFileName+".json"
        with open(cropFileNew, "w+") as f:
            json.dump(tempDict, f)

        tDictKeys = tempDict.keys()
        for size in tDictKeys:
            #spatialTree = cKDTree(data=tempDict[size],balanced_tree=True)
            m = 'haversine'
            d= tempDict[size]
            #metrics.pairwise.haversine_distances
            ballTree = BallTree(d, metric="haversine")
            #ballTree = BallTree(tempDict, metric="haversine")

            self.newDict[size] = ballTree
        print(os.curdir)
        #newFile = "../tempData/temp.pickle"
        newFile = "../tempData/"+self.newFileName+".pickle"
        with open(newFile, "wb+") as f:
            pickle.dump(self.newDict, f,protocol=pickle.HIGHEST_PROTOCOL)

        return




    def load_into_kdTree(self):
        data = None
        with open(self.file, "rb") as f:
            data = pickle.load(f)

        print(data)

        data.query_radius([[startPostion[1],startPostion[0]]],maxDistance)



    def test(self):
        cropData = None
        with open(self.file, "rb") as f:
            cropData = json.load(f)
        keys = list(cropData.keys())
        #print(type(literal_eval(keys[0])))
        c = keys[0]
        #print(c)
        coords = literal_eval(c)
        print(type(coords))



if __name__ == "__main__":

    #path = "../../USE_THIS/MergedData/Corn.json"
    path = "../../DashBoardNew/tempData/Alfalfa.pickle"

    sorter = DataSorting(path,"")
    sorter.load_into_kdTree()
    exit()
    # sorter.test()
    # sorter.driver()
    #sorter.load_into_kdTree()
    #exit()

    directory = "../../USE_THIS/MergedData/"
    for filename in os.listdir(directory):
        file = directory + filename
        newFname = filename.replace(" ","_")
        newFname = newFname.replace(".json","")
        print(newFname)

        sorter = DataSorting(file,newFileName=newFname)
        sorter.driver()



    #sorter = DataSorting(path)
    #sorter.test()
    #sorter.driver()
    #sorter.load_into_kdTree()
    #dir = os.
    #for file in os.listdir(""):

