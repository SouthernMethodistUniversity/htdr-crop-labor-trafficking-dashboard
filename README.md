# HTDR Crop Labor Trafficking Dashboard

This repo contains the python code for an agricultural dashboard aimed at combating human trafficking by better equiping law enforcement with the information needed to perform their duties. This app leverages data from the US Department of Agriculture and their computer vision model, CroplandCROS, in coordination with geospatial data to help identify potential locations for sites of labor trafficking based upon anecdotes from victims.

## Documentation

The new DashBoard can be found in DashBoardNew

The crop data is split into 2 folders, 1 containing pickle files and 1 containing json files
    - Each crop has one of each, for example Corn.json and Corn.pickle

The Json files contain the farm size as a key and a list of locations (lists--> [x,y]) as the values
    - for example {1:[[x,y],[x1,y1]],5:[[x2,y2],[x3,y3]]}
The pickle files store ball trees relating for each key in the json file,
    - {1:BallTree1,5:BallTree2}

The ball trees are searched and return an index where to find the value in the json files, allowing for quick lookup

How it works:
    For a given input (crop and region min/max)
        Grab the crop ball tree file, search it make a dictionary of the results
            dict is as follows key->regionSize value->list of indicis --> {1:[2,4,6],5:[1,3,5]}
        Open the crop file and for each index grab the values at the correct indicis, these will be geo-coordinates plot the coordinates on the map

Current issues,
    Area not working properly, 50 miles getting things as far as ~150 miles?
        - possibly due to ball tree not using haversine
    Sometimes the index returned by the ball tree is not found in the json file
        - currently try/except and skipping over it
        - could be due to error mentioned above, could be due to indexing wrong/broken json file

GENERAL ORDER OF FILE CREATION (This is to roughly walk through the files that can be found and how they were created, any error in any of these processes could have resulted in the current errors)
(There are many test files floating around this project but are not mentioned here, I am leaving them to show my general thought process and testing)

1) HPC_output (Location -> Location) Arizona_Greenlee.tiff --> Arizona_Greenlee.json --CallFIle.sh was run on HPC, this called HPC_SCRIPT.py and used filepaths.txt as the argument for where to find the files--
    -> JSON files created from the tiff images to make searching easier
    -> produced lots of un-necessary output (for each grouping of coordinates)
        {"1": [{"color": 1, "center_coordinate": [-12179407.315596767, 3978111.8859456438], "region_id": 1, "size_pixels": 1, "size_geographic": 900.0}

2) MergedData (Location -> Crop) Arizona_Greenlee.json --> Corn.json --created by MERGE_DATA.py--
    -> Took all of the location files and converted them to be crop files, making for easier search across borders
    -> stored coordinates as the key, and the size as the value {"(-11237267.52272119, 4188693.3948359336)": 2,}

3) CropFilesNew (Crop -> Crop) Corn.json->Corn.json --Created By DataSorting.py--
    -> refactored the files so the size is the key and the list of coordinates is the value {"1": [[-1.673743397350865, 0.5385640047822902], [-1.674270196947675, 0.538467095750694],...}

4) tempData ~this is a misleading name, we are using this data in 'prod' --Created By DataSorting.py--
    -> Created the pickle files holding the BallTrees, the files are actually json files
    -> the key is the region size and the value is the ball tree, which is supposed to use haversine as the distance metric
