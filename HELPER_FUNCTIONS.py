import numpy as np
import os
import rasterio
import geopandas as gpd
from pyproj import Transformer

class HELPER_FUNCTIONS:

    # Add a helper function to format numbers with commas
    @staticmethod
    def format_number(num):
        return "{:,}".format(num)



    @staticmethod
    # Function to create a buffer ring
    def create_ring(lat, lon, inner_radius_km, outer_radius_km, num_points=360):
        '''RETURNS COORDINATES FOR RING'''
        angles = np.linspace(0, 2 * np.pi, num_points)
        inner_coords = [(lon + (inner_radius_km / 111) * np.cos(a), lat + (inner_radius_km / 111) * np.sin(a)) for a in
                        angles]
        outer_coords = [(lon + (outer_radius_km / 111) * np.cos(a), lat + (outer_radius_km / 111) * np.sin(a)) for a in
                        angles]
        return inner_coords + outer_coords[::-1] + [inner_coords[0]]



    # Function to read crop pixels from TIF and VAT DBF files
    @staticmethod
    def read_crop_pixels(state_name, county_name, selected_crop):
        '''Function to read crop pixels from TIF and VAT DBF files'''
        tif_path = os.path.expanduser(f'CountyGEOTIFF/{state_name}/{county_name}/clipped.TIF')
        vat_path = os.path.expanduser(f'CountyGEOTIFF/{state_name}/{county_name}/clipped.TIF.vat.dbf')

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
    @staticmethod
    def convert_to_geographic(coords):
        '''Function to convert Web Mercator to geographic coordinates'''
        transformer = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)
        geographic_coords = [transformer.transform(coord[0], coord[1]) for coord in coords]
        return geographic_coords

    # Function to validate geographic coordinates
    @staticmethod
    def validate_coordinates(coords):
        '''Function to validate geographic coordinates'''
        for lon, lat in coords:
            if not (-125 <= lon <= -65) or not (25 <= lat <= 50):
                return False
        return True

    # Function to calculate zoom level based on distance
    @staticmethod
    def calculate_zoom_level(distance):
        '''Function to calculate zoom level based on distance'''
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

