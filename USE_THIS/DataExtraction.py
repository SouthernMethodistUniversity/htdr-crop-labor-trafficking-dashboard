import rasterio
import pandas as pd
import numpy as np
import os

import json
from pywikibot import output
from rasterio.rio.helpers import coords
from sklearn.cluster import KMeans, DBSCAN
from rasterio.transform import rowcol, xy
from shapely.geometry import box
from skimage.measure import label, regionprops
from scipy.ndimage import label

from pyproj import Transformer
from rasterio.plot import show
import matplotlib.pyplot as plt
import matplotlib.patches as patches


import numpy as np
from scipy.ndimage import label, center_of_mass
from rasterio import open as rio_open
from rasterio.transform import xy

class DataExtraction:
    def __init__(self):
        pass

    def getCropCoords(self,tiff_path):
        with rasterio.open(tiff_path) as src:
            # Read the first band (assuming single-band GeoTIFF, modify if multiband)
            data = src.read()  # Get pixel values
            transform = src.transform  # Affine transformation matrix
            width = src.width
            height = src.height

            # Prepare a list to store coordinates and pixel values
            pixel_info = []

            # Loop through each pixel in the raster
            #data = src.read()  # This will read all bands
            for row in range(height):
                for col in range(width):
                    x, y = rasterio.transform.xy(transform, row, col, offset='center')
                    pixel_values = [data[band, row, col] for band in range(data.shape[0])]
                    pixel_info.append({'x': x, 'y': y, **{f'band_{i + 1}': val for i, val in enumerate(pixel_values)}})

        # Convert the list to a DataFrame for easy saving or analysis
        df = pd.DataFrame(pixel_info)

        # Save to a CSV file
        output_csv_path = './OUTPUT/output_coordinates_and_values.csv'
        df.to_csv(output_csv_path, index=False)

    def get_valid_data_coords(self,tiff_path):
        with rasterio.open(tiff_path) as src:
            data = src.read(1)
            transform = src.transform
            width, height = src.width, src.height

            # List for storing coordinates and pixel values
            pixel_info = []

            # Loop over a larger range to capture valid data
            for row in range(height):
                for col in range(width):
                    value = data[row, col]
                    if value != 255:  # Only process non-255 values
                        x, y = rasterio.transform.xy(transform, row, col, offset='center')
                        pixel_info.append({'x': x, 'y': y, 'band_1': value})

            # Convert to DataFrame
            df = pd.DataFrame(pixel_info)

            # Print a sample for validation
            print(df.head(20))  # Print first 20 valid points

            # Save to CSV if needed
            output_csv_path = './OUTPUT/output_non255_coordinates.csv'
            df.to_csv(output_csv_path, index=False)

    def tiff_data_check(self,tiff_path):
        with rasterio.open(tiff_path) as src:
            # Print metadata to check for nodata and scale factors
            print("Metadata:", src.tags())
            print("NoData value:", src.nodata)

            crs = src.crs
            print("Coordinate Reference System (CRS):", crs)

            # Read the data and check for unique values
            data = src.read(1)  # Read the first band
            unique_values = np.unique(data)
            print("Unique pixel values:", unique_values)

            # If nodata exists, remove it from analysis
            if src.nodata is not None:
                data = data[data != src.nodata]
                unique_values_filtered = np.unique(data)
                print("Unique values without NoData:", unique_values_filtered)

    def inspect_data(self,tiff_path):
        with rasterio.open(tiff_path) as src:
            data = src.read(1)  # Read the first band

            # Check the entire array shape and summary statistics
            print("Data Shape:", data.shape)
            print("Unique Values in Data:", np.unique(data))

            # Show a small sample (10x10 block) to inspect raw values
            sample_block = data[:10, :10]
            print("Sample Block:\n", sample_block)

    def get_bands(self,file):
        with rasterio.open(file) as src:
            # Access the number of bands using the 'count' attribute
            num_bands = src.count

            print("Number of bands:", num_bands)

    def get_bounding_boxes_for_clusters(self,tiff_path, color_value):
        with rasterio.open(tiff_path) as src:
            data = src.read(1)  # Read as 8-bit data

            # Create a mask for pixels matching the specified color value
            mask = data == color_value

            # Label connected components in the mask
            labeled_array, num_features = label(mask, return_num=True, connectivity=2)

            bounding_boxes = []
            centers = []

            # Calculate bounding boxes and center points for each region
            for region in regionprops(labeled_array):
                min_row, min_col, max_row, max_col = region.bbox
                top_left = rasterio.transform.xy(src.transform, min_row, min_col, offset="ul")
                bottom_right = rasterio.transform.xy(src.transform, max_row, max_col, offset="lr")

                bounding_box = [(top_left[0], top_left[1]), (bottom_right[0], bottom_right[1])]
                center_coords = rasterio.transform.xy(src.transform, (min_row + max_row) // 2, (min_col + max_col) // 2)

                bounding_boxes.append(bounding_box)
                centers.append(center_coords)

        return bounding_boxes, centers

    def plot_bounding_boxes_on_image(self,tiff_path, bounding_boxes, centers, output_image_path):
        with rasterio.open(tiff_path) as src:
            fig, ax = plt.subplots(figsize=(10, 10))

            # Display the image
            show(src, ax=ax)

            # Plot bounding boxes and center points
            for bbox, center in zip(bounding_boxes, centers):
                minx, miny = bbox[0]
                maxx, maxy = bbox[1]
                rect = patches.Rectangle((minx, miny), maxx - minx, maxy - miny, linewidth=2, edgecolor='red',
                                         facecolor='none')
                ax.add_patch(rect)
                ax.plot(center[0], center[1], 'bo')

            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')

            # Save the figure as an 8-bit output image
            fig.savefig(output_image_path, dpi=300)
            plt.close(fig)





    def preform_Clustering(self):
        df = pd.read_csv('./OUTPUT/output_non255_coordinates.csv')
        # Set DBSCAN parameters
        eps = 30  # Distance threshold (adjust based on your data)
        min_samples = 2  # Minimum points to form a cluster

        # Group by color
        color_clusters = {}
        for color,group in df.groupby('band_1'):
            coords = group[["x", "y"]].values
            clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
            group["cluster"] = clustering.labels_
            color_clusters[color] = group

        clustered_data = pd.concat(color_clusters.values())
        print(clustered_data.head(20))
        clustered_data.to_csv('./OUTPUT/clustered_data.csv', index=False)

    def get_coordinates_for_color(self,image, color_value, transform):
        # Create a binary mask for the specific color
        color_mask = (image == color_value)

        # Label connected components in the mask
        labeled_array, num_features = label(color_mask)

        # Initialize list to store coordinates
        color_regions = []

        # For each labeled region, get the pixel coordinates and convert to geographic coordinates
        for region_id in range(1, num_features + 1):
            # Find pixel indices of the current region
            region_pixels = np.argwhere(labeled_array == region_id)

            # Convert pixel indices to geographic coordinates
            coords = [xy(transform, row, col) for row, col in region_pixels]
            color_regions.append(coords)

        return color_regions

    def extract_regions_with_centers(self,image, color_value, transform):
        # Create a binary mask for the specific color
        color_mask = (image == color_value)

        # Label connected components in the mask
        labeled_array, num_features = label(color_mask)

        # Store results in a list
        regions_info = []

        for region_id in range(1, num_features + 1):
            # Get the pixel coordinates of the center of the current region
            region_center = center_of_mass(color_mask, labeled_array, region_id)
            center_row, center_col = int(region_center[0]), int(region_center[1])

            # Convert the pixel center to geographic coordinates
            center_coord = xy(transform, center_row, center_col)

            # Save region information
            regions_info.append({
                'color': color_value,
                'center_coordinate': center_coord,
                'region_id': region_id
            })

        return regions_info

    def extract_regions_with_centers_and_size(self,image, color_value, transform, pixel_area):
        # Create a binary mask for the specific color
        color_mask = (image == color_value)

        # Label connected components in the mask
        labeled_array, num_features = label(color_mask)

        # Store results in a list
        regions_info = []

        for region_id in range(1, num_features + 1):
            # Get pixel coordinates of the center
            region_center = center_of_mass(color_mask, labeled_array, region_id)
            center_row, center_col = int(region_center[0]), int(region_center[1])

            # Convert pixel center to geographic coordinates
            center_coord = xy(transform, center_row, center_col)

            # Calculate the size of the region (number of pixels * pixel area)
            region_size_pixels = np.sum(labeled_array == region_id)
            region_size_geographic = region_size_pixels * pixel_area

            # Save region information
            regions_info.append({
                'color': color_value,
                'center_coordinate': center_coord,
                'region_id': region_id,
                'size_pixels': region_size_pixels,
                'size_geographic': region_size_geographic
            })

        return regions_info

    def make_txt_file(self):
       #gen =  os.walk("../CountyGEOTIFF")

        for path, directories, files in os.walk("../CountyGEOTIFF"):
            for file in files:
                if os.path.splitext(file)[1] == '.TIF':
                    print(os.path.join(path, file))
                    f = open("filepaths.txt", "a")
                    f.write(os.path.join(path, file)+"\n")
                    f.close()
                #print('found %s' % os.path.join(path, file))

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)



if __name__ == '__main__':
    #transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")
    #val = transformer.transform(-10638624.74491964, 3523345.8322925605)
    #print(val)

    lineNum = 1

    with open('./filepaths.txt', 'r') as file:
        lines = file.readlines()
        third_line = lines[2]  # reads the 3rd line in the doc
        print(third_line)
    #print(os.getcwd())
    #dataExtraction = DataExtraction()
    #gen = dataExtraction.make_txt_file()


    #exit()
    #dataExtraction.tiff_data_check(tiff_path='../CountyGEOTIFF/Texas/Harris/clipped.TIF')
    #exit()
    #dataExtraction.inspect_data(tiff_path='../CountyGEOTIFF/Texas/Harris/clipped.TIF')
    #dataExtraction.get_valid_data_coords(tiff_path='../CountyGEOTIFF/Texas/Harris/clipped.TIF')
    #dataExtraction.get_bands(file='../CountyGEOTIFF/Texas/Harris/clipped.TIF')

    #result_df = dataExtraction.get_bounding_boxes(tiff_path='../CountyGEOTIFF/Texas/Harris/clipped.TIF')

    tiff_path = '../CountyGEOTIFF/Texas/Harris/clipped.TIF'
    #input_tiff_path = "path/to/your/8bit_input.tif"
    output_image_path = "./OUTPUT/img.png"
    #dataExtraction.preform_Clustering()
    # Specify the color value you want to find
    color_value = 142 # Change this to the desired 8-bit color value

    # Step 1: Find bounding boxes for specified color regions
    #bounding_boxes, centers = dataExtraction.get_bounding_boxes_for_clusters(tiff_path=tiff_path, color_value=color_value)

    # Step 2: Plot and save the output image with bounding boxes
    #dataExtraction.plot_bounding_boxes_on_image(tiff_path=tiff_path, bounding_boxes=bounding_boxes, centers=centers, output_image_path=output_image_path)

    #file_path = '/mnt/data/clipped.TIF'

    with rio_open(tiff_path) as src:
        # Read the image data (first band)
        image_data = src.read(1)
        transform = src.transform
        nodata = src.nodata

        # Calculate pixel area in geographic units (assuming square pixels)
        pixel_width = transform[0]
        pixel_height = -transform[4]
        pixel_area = pixel_width * pixel_height  # Area of each pixel

    # Identify unique colors (excluding the NoData value)
    unique_colors = np.unique(image_data[image_data != nodata])
    print(unique_colors)
    print(len(unique_colors))
    #exit()
    unique_colors = [1,2]
    all_regions_data = {}

    # Loop through each unique color and get connected regions' center coordinates and sizes
    for color in unique_colors:
        all_regions_data[color] = dataExtraction.extract_regions_with_centers_and_size(
            image_data, color, transform, pixel_area
        )

    # Display results for the first few colors
    #(all_regions_data)
    with open('./output/extract_regions_with_centers_test.json', 'w') as f:
        json.dump(all_regions_data,f,cls=NpEncoder)

    print("COMPLETE")







"""
    ##
    file_path = '../CountyGEOTIFF/Texas/Harris/clipped.TIF'
    with rio_open(file_path) as src:
        # Read the image data (first band)
        image_data = src.read(1)
        transform = src.transform
        nodata = src.nodata

    # Identify unique colors (excluding the NoData value)
    unique_colors = np.unique(image_data[image_data != nodata])
    print(unique_colors)
    unique_colors = [1,2]

    all_regions_centers = {}

    # Loop through each unique color and get connected regions' center coordinates
    for color in unique_colors:
        all_regions_centers[color] = dataExtraction.extract_regions_with_centers(image_data, color, transform)

    # Display results for the first few colors
    print(all_regions_centers)
    with open('./output/extract_regions_with_centers_test.json.json', 'w') as f:
        json.dump(all_regions_centers, f)


"""

