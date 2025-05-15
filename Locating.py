import csv
from math import asin, atan2, cos, degrees, radians, sin

import cv2
import rasterio
from rasterio.warp import transform_bounds
import numpy as np
from PIL import Image
import geopandas
import geopy.distance
from shapely.geometry import Point, Polygon
import folium

import rasterio
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



import time
class Locating:
    def __init__(self):
        pass

    def getNewLatLong(self,lat1, lon1, d, bearing, R=6371):
        """
            lat: initial latitude, in degrees
            lon: initial longitude, in degrees
            d: target distance from initial
            bearing: (true) heading in degrees
            R: optional radius of sphere, defaults to mean radius of earth

            Returns new lat/lon coordinate {d}km from initial, in degrees
            """
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        a = radians(bearing)
        lat2 = asin(sin(lat1) * cos(d / R) + cos(lat1) * sin(d / R) * cos(a))
        lon2 = lon1 + atan2(
            sin(a) * sin(d / R) * cos(lat1),
            cos(d / R) - sin(lat1) * sin(lat2)
        )
        return (degrees(lat2), degrees(lon2),)

    # Convert GeoTIFF to PNG and transform the bounds to WGS84
    def geotiff_to_png(self,geotiff_path, output_png_path):
        with rasterio.open(geotiff_path) as src:
            # Read the data from the first band
            image_data = src.read(1)
            # Normalize the pixel values to 0-255 for PNG
            image_data = ((image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data)) * 255).astype(
                np.uint8)
            # Create a PIL Image from the data
            image = Image.fromarray(image_data)
            # Save as PNG
            image.save(output_png_path)

            # Transform the bounds from the original CRS to WGS84 (Leaflet uses this)
            bounds = src.bounds
            wgs84_bounds = transform_bounds(src.crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)

            return wgs84_bounds  # Return the transformed bounds for Leaflet

    def pointInPolygon(self,polygon:Polygon,point:Point):
        return polygon.contains(point)


    def getDistance(self,coord_1,coord_2):
        '''coord_1/2 are tuples with the long lat'''
        print(geopy.distance.geodesic(coord_1, coord_2).miles)





    def openShape(self,filename):
        #openFileStart = time.perf_counter()
        self.shpFile = geopandas.read_file(filename)
        #openFileEnd = time.perf_counter()
        #total = openFileEnd - openFileStart
        #print("Open Shape Time: ",total)
        # GeoPandasFuncs file has a function to read the shp file with all counties


    def getLongLat(self,county,stateNum):
        #county = self.shpFIle.loc[0]
        #print(county)

        #print(self.shpFIle.shape)

        #start = time.perf_counter()
        #for i in range(self.shpFile.shape[0]):
            #print(self.shpFIle.loc[i,"NAME"])
            #pass

        #list comprehension
        row_data = self.shpFile[(self.shpFile['NAME'] == county) & (self.shpFile['STATEFP'] == stateNum )]
        #row_data = self.shpFile[self.shpFile['STATEFP'] == stateNum]
        #print(row_data)

        #getting INTPTLAT returns meta data. values strips it and returns a list, this gets the coord in the list
        lat = row_data['INTPTLAT'].values[0]
        #print(lat)
        long = row_data['INTPTLON'].values[0]

        return lat,long
        #print("Lat: ",lat,"-")
        #print("Long: ",long,"-")
        #end = time.perf_counter()
        #total = end - start
        #print("Loop Time: ",total)
        #for line in self.shpFIle:
        #    print(line)
            #print(line.loc[0,"Name"])

    def loadCrossings(self):
        data = {}
        with open('southfinal2.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:

                #only 2 overlap, laredo and el paso
                if row[0] not in data:
                    data[row[0]] = {"state":row[1],"lat":row[2],"long":row[3]}
                else:
                    pass
                    #print("KEY COLLISION: ",row[0])
        self.data = data
    def getCrossingLatLong(self,crossing):
        crossing = self.data[crossing]
        return crossing["lat"],crossing["long"]


        #self.crossingData = data
        #print(self.crossingDatal)

        #reader = csv.DictReader(open('southfinal2.csv'))
        #dictobj = next(reader)
        #print(dictobj)
        #while next(reader):
         #   dictObj





    # Function to get coordinates of the centroid from the raster file
    def get_raster_centroid_coords(self,tiff_file):
        with rasterio.open(tiff_file) as dataset:
            # Get the raster's affine transformation and dimensions
            transform = dataset.transform
            width = dataset.width
            height = dataset.height

            # Calculate the centroid (center) pixel coordinates
            centroid_x = width // 2
            centroid_y = height // 2

            # Convert pixel coordinates to geographic coordinates
            lon, lat = transform * (centroid_x, centroid_y)

            return lon, lat


    # Function to check if centroid falls within any geometry in the shapefile
    def find_county_for_point(self,shapefile, lon, lat):
        # Load the shapefile
        counties = gpd.read_file(shapefile)

        # Create a point geometry from the raster's centroid
        centroid_point = Point(lon, lat)

        # Ensure both the point and counties are in the same CRS
        counties = counties.to_crs(epsg=4326)  # Assuming WGS84 for simplicity

        # Find the county containing the centroid point
        containing_counties = counties[counties.contains(centroid_point)]

        if not containing_counties.empty:
            return containing_counties
        else:
            return None


    def tiff_to_geotiff(self,target_county:str,target_state:int,tiff_file,output_file_tiff):
        tiff_path = tiff_file
        # Load the TIFF file and get profile and metadata
        #tiff_path = 'path_to_your_raster.tiff'
        with rasterio.open(tiff_path) as src:
            raster_data = src.read(1)  # Read the first band
            transform = src.transform
            crs = src.crs
            profile = src.profile

        # Initialize an array to store unique values for each region
        # Using int32 to allow for unique integer region values
        #region_data = np.zeros(raster_data.shape, dtype=np.int32)
        region_data = np.zeros(raster_data.shape, dtype=np.uint8)

        for idx, row in self.shpFile.iterrows():
            county_name = row['NAME']  # Replace with the actual column name for counties
            state_number = row['STATEFP']  # Replace with the actual column name for state numbers

            # Check if the row matches the specified conditions
            if county_name == target_county and state_number == target_state:
                # Unique identifier for the matching region
                region_identifier = f"{county_name}_{state_number}"
                unique_value = idx + 1  # Or assign a custom value if needed

                # Print the identifier for debugging (optional)
                print(f"Processing region: {region_identifier}, assigned value: {unique_value}")

                # Create a mask for the current geometry
                shapes = [(row.geometry, unique_value)]
                mask = rasterio.features.geometry_mask(
                    shapes,
                    out_shape=raster_data.shape,
                    transform=transform,
                    invert=True,
                    all_touched=True
                )

                # Assign the unique value to the masked region in the output array
                region_data[mask] = unique_value

        #profile.update(dtype=rasterio.int32, count=1)
        #region_data = np.clip(region_data, 0, 255).astype(np.uint8)
        #profile.update(dtype=rasterio.uint8)
        profile.update(dtype=rasterio.uint8, count=1)

        # Write the result to a new GeoTIFF
        output_tiff_path = output_file_tiff
        with rasterio.open(output_tiff_path, 'w', **profile) as dst:
            dst.write(region_data, 1)
            dst.update_tags(transform=transform)



    def getBoundingBoxes(self,file):
        pass
        #contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cnt = contours[0]
        #x, y, w, h = cv2.boundingRect(cnt)




    '''USE THIS// NOT FINISHED'''
    def preprocessing(self,startingLoc:str,distances:list):
        max_distance = max(distances)
        stored_data={}
        lat_start, lon_start = self.getCrossingLatLong(startingLoc)
        for index,row in self.shpFile.iterrows():
            lon = row['INTPTLON']
            lat = row['INTPTLAT']

            distance = self.getDistance((lat,lon),(lat_start,lon_start))

            if distance <= max_distance:
                county = row['COUNTYFP']
                state = row['STATEFP']
                key = str(county)+"_"+str(state)
                myDict = {"crossing":startingLoc,"distance":distance,"lat":lat,"long":lon}
                #stored_data[key] = myDict



if __name__ == '__main__':
    loc = Locating()

    #file = "./CountyGEOTIFF/Texas/Harris/clipped.TIF"
    #output = "./outputDir/output.png"
    #vals = loc.geotiff_to_png(file, output)
    #print(vals)

    #opening files
    shpFilePath = "./tl_2023_us_county/tl_2023_us_county.shp"
    loc.openShape(shpFilePath)
    loc.loadCrossings()

    #lat,long = loc.getLongLat("Harris","48")

    #harris = (lat,long)
    #lat_paso,lon_paso = loc.getCrossingLatLong("El Paso")
    #elPaso = (lat_paso,lon_paso)


    #loc.getDistance(harris,elPaso)



    target="Harris"
    state = 48
    tiff_path = "./CountyGEOTIFF/Texas/Harris/clipped.TIF"
    output_path = "./outputDir/harris.tif"
    loc.tiff_to_geotiff(target,state,tiff_file=tiff_path,output_file_tiff=output_path)



    #lon, lat = loc.get_raster_centroid_coords("./CountyGEOTIFF/Texas/Harris/clipped.TIF")
    #print(f'Centroid Coordinates: Longitude: {lon}, Latitude: {lat}')