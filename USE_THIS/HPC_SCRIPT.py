import argparse
import sys

from scipy.ndimage import label, center_of_mass
import json
import numpy as np
from rasterio.transform import xy
from rasterio import open as rio_open
class HPC_SCRIPT:
    def extract_regions_with_centers_and_size(self, image, color_value, transform, pixel_area):
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


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)



def test_Call(filepath):
    path = "./OUTPUT/SAMPLE_DIR/"+filepath+".txt"
    with open(path, "w") as file:
        str_test = "THIS IS A TEST\n"+filepath+"\n"
        file.write(str_test)
#make file that contains all of the paths to the counties
if __name__ == "__main__":
    hpc_class = HPC_SCRIPT()


    #lineNum = 0
    lineNum = sys.argv[1]

    tiff_path = ""
    with open('./filepaths.txt', 'r') as file:
        lines = file.readlines()
        tiff_path = lines[int(lineNum)]  # reads the 3rd line in the doc
        #print(third_line)
    #print(type(tiff_path))


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

    all_regions_data = {}

    # Loop through each unique color and get connected regions' center coordinates and sizes
    for color in unique_colors:
        all_regions_data[str(color)] = hpc_class.extract_regions_with_centers_and_size(
            image_data, color, transform, pixel_area
        )

    # Display results for the first few colors
    #(all_regions_data)

    #given tiff_path
    #../CountyGEOTIFF/Oklahoma/Lincoln/clipped.TIF
    #file_path_split = split(tiff_path,".")
    #file_path_split.pop()#remove .TIF

    #filePathTxt = file_path_split[0]
    #filePathTxt=filePathTxt.replace("/","_")#remove file path delimeters
    #filePathTxt=filePathTxt.replace("..", "")

    file_path_split = tiff_path.split("/")
    #print(file_path_split)
    file_path_txt = file_path_split[2] + "_" + file_path_split[3]

    output_path = "./output/"+file_path_txt+".json"
    with open(output_path, 'w') as f:
        json.dump(all_regions_data,f,cls=NpEncoder)
