import csv
import io
import json
import os
import time
from os import listdir

from osgeo_utils.gdal2tiles import filename

if __name__ == "__main__":
    class_values = {}

    # Load values to crop type ["NUMBER":"CROP_TYPE"]
    with open("../DataMapping/out.csv") as csvfile:
        reader = csv.DictReader(csvfile,delimiter=',')
        for row in reader:
            #print(row)
            class_values[row['Value']] = row['Class_Name']

    #print(class_values["1"])
    #exit()

    hpc_output_path = "./HPC_output"
    #print(listdir(hpc_output_path))

    for file in listdir(hpc_output_path):
        fName = hpc_output_path + "/" + file
        with open(fName,'r') as f:
            #load the file as json
            data = json.load(f)
            #print(len(data["1"]))
            #exit()
            #get each of the dictionaries containing a color
            for key in data.keys():
                #print(key)

                crop_type = class_values[key] #
                #exit()

                filename = crop_type.replace(" ", "_") #name of the new file holding a specific crop
                filename = crop_type.replace("/", "_")  # name of the new file holding a specific crop
                filePath = "./MergedData/"+ filename + ".json"

                jsonData = None

                if os.path.isfile(filePath) and os.access(filePath, os.R_OK):
                    # checks if file exists
                    #print("File exists and is readable")
                    pass
                else:
                    #print("Either file is missing or is not readable, creating file...")
                    #file = filePath+".json"
                    emptyDict = {}
                    with open(filePath, 'w+') as f_:
                        json.dump(emptyDict, f_)
                        #f_.write(json.dumps("{}"))
                        #f_.close()
                        #time.sleep(0.5)
                    #print("File Created At: "+filePath)


                with open(filePath,"r") as currFile:
                    #print("loaded from: "+filePath)
                    jsonData = json.load(currFile)

                areaList = data[key] #grab list of areas of a specific crop type
                #areaList is a list of dicts
                for area in areaList:
                    #area is a dict
                    key = tuple(area["center_coordinate"])
                    #tempAreaDict = {}
                    #tempAreaDict["size_pixels"] =  area["size_pixels"]
                    jsonData[str(key)] = area["size_pixels"]

                with open(filePath,"w") as outFile:
                    json.dump(jsonData, outFile)
#list search O(n)
#tree search

