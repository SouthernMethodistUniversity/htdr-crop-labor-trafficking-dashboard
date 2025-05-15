import os

from osgeo import gdal
import json
from simpledbf import Dbf5
import geopy.distance
import pyproj
from pyproj import CRS, Transformer
import math
import pandas as pd
from PIL.TiffTags import TAGS
from PIL import Image

class DataViewing:
    def __init__(self):
        self.data = None


    def open_file(self,file):
        with open(file, 'r') as f:
            self.data = json.load(f)

    def convert_3857_to_4326(self,coord1,coord2):
        #print(coord1,coord2)
        # Create transformer objects for each CRS
        transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326")

        # Example coordinates in EPSG:3857
        #x = 1234567.89
        #y = 9876543.21

        # Transform coordinates
        lon, lat = transformer.transform(coord1, coord2)
        return lon, lat



    #
    # def distance(self,coord1, coord2):
    #
    #     """Calculate distance between two coordinates in meters."""
    #
    #     # Define the CRS for EPSG:3857
    #     crs_4326 = CRS.from_epsg(4326)
    #
    #     # Create a transformer object to convert coordinates
    #     transformer = Transformer.from_crs(crs_4326, crs_4326, always_xy=True)
    #
    #     # Transform coordinates to EPSG:3857
    #     x1, y1 = transformer.transform(coord1[0], coord1[1])
    #     x2, y2 = transformer.transform(coord2[0], coord2[1])

        # Calculate Euclidean distance
#        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def getDistance(self,coord_1,coord_2):
        '''coord_1/2 are tuples with the lat long, DISTANCE MUST BE IN EPSG:4326'''

        #print(geopy.distance.geodesic(coord_1, coord_2).miles)
        return geopy.distance.geodesic(coord_1, coord_2).miles


    def find_areas(self,cropType:str,regionSize,startingPosition,maxDistance):

        validAreas = []
        #print(self.data.keys())
        if cropType not in self.data.keys():
            #print(-1)
            return "CROP TYPE DNE"

        areas = self.data[cropType]
        for area in areas:
            lat, long, = self.convert_3857_to_4326(area["center_coordinate"][0], area["center_coordinate"][1])
            distance = self.getDistance(startingPosition,(lat,long))
            print(distance)
            if distance <= maxDistance and area["size_pixels"] >= regionSize:
                validAreas.append(area)

        return validAreas



    def example(self):
        val = self.data["1"]
        lat,long,  = self.convert_3857_to_4326(val[0]["center_coordinate"][0], val[0]["center_coordinate"][1])
        print(lat, long)
        lat_2,long_2 = self.convert_3857_to_4326(val[1]["center_coordinate"][0], val[1]["center_coordinate"][1])
        print(lat_2, long_2)
        #dis = self.distance(val[0]["center_coordinate"], val[1]["center_coordinate"])
        #print(dis)
        dis = self.getDistance((lat,long), (lat_2,long_2))
        print(dis)

    def getCropLayers(self):
        #with open('./filepaths.txt', 'r') as file:
        #    lines = file.readlines()
        #image = Image.open("../CountyGEOTIFF/Arizona/Apache/clipped.TIF")

        # Path to the VAT DBF file
        #dbf_path = "../CountyGEOTIFF/Arizona/Apache/clipped.TIF.vat.dbf"
        results_df = pd.DataFrame()
        for path, directories, files in os.walk("../CountyGEOTIFF"):
            for file in files:
                if os.path.splitext(file)[-1] == '.dbf':
                    dbf = Dbf5(path+"/"+file)
                    df = dbf.to_dataframe()
                    df = df.drop('Count', axis=1)

                    results_df = pd.concat([results_df, df]).drop_duplicates('Class_Name').reset_index(drop=True)
                    #print(os.path.join(path, file))
                    #f = open("filepaths.txt", "a")
                    #f.write(os.path.join(path, file)+"\n")
                    #f.close()

        # Load the DBF file into a pandas DataFrame
        #dbf = Dbf5(dbf_path)
        #df = dbf.to_dataframe()

        # Display the data
        print(results_df)
        results_df.to_csv('out.csv', index=False)

if __name__ == '__main__':
    dv = DataViewing()
    #dv.getCropLayers()
    #exit()
    file = "../USE_THIS/HPC_output/Arizona_Greenlee.json"

    dv.open_file(file)
    #dv.example()
    validAreas = dv.find_areas("1",10,(26.403928,-99.018981),750)
    print(len(validAreas))


