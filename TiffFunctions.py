from idlelib.debugobj import myrepr
import bs4
import numpy as np
from PIL import Image
#import xml
import geopandas as gpd
import fiona

import dbf

class TiffFunctions:
    def __init__(self):
        pass

    def readFile(self,file):
        im = Image.open(file)
        im = im.convert('RGB')

        self.imarr = np.array(im)
        #print(imarr.shape)

        print("Shape: " + str(self.imarr.shape))
        print("DIMS: "+str(self.imarr.ndim))

    def getPixles(self):
        self.imarr[0][1] = [255,255,255]

        #self.imarr[self.imarr[0][0]==0] = 255

        #for RGB in self.imarr:
        #    print(rgb)



        unique, counts = np.unique(self.imarr,axis=1, return_counts=True)
        #print(unique, counts)
        for row, c in zip(unique, counts):
            print(row, c)
        #print(dict(zip(unique, counts)))

    def getUniques(self):
        reshaped = self.imarr.reshape(self.imarr.shape[0]*self.imarr.shape[1], 3)
        vals, counts = np.unique(reshaped, axis=0, return_counts=True)

        dict = {tuple(v): c for v, c in zip(vals, counts)}
        print(dict)
    def showImage(self):
        Image.fromarray(self.imarr).show()

    def open_county_shape_file(self):
        shape = fiona.open("tl_2023_us_county/tl_2023_us_county.shp")
        print(shape.schema)

class openDBF():
    def __init__(self,file):
        self.file = file

    def openFile(self):
        table = dbf.Table(self.file)
        print(table)

    def openWithGeoPandas(self):
        vat_df = gpd.read_file(self.file)
        print(vat_df)




if __name__ == '__main__':
    myTF = TiffFunctions()

    myTF.open_county_shape_file()
    exit()


    #convertToArray("Texas", "Lubbock")
    state = "Texas"
    county = "Harris"
    file = "CountyGEOTIFF/" + state + "/" + county + "/clipped.TIF"
    myTF.readFile(file)
    myTF.showImage()
    #myTF.getPixles()

    #myTF.getUniques()
    dbfFile = "CountyGEOTIFF/" + state + "/" + county + "/clipped.TIF.vat.dbf"
    db = openDBF(dbfFile)
    #db.openFile()
    db.openWithGeoPandas()


    #xmlFile = "CountyGEOTIFF/" + state + "/" + county +"/clipped.TIF.aux.xml"
    xmlFile = "CountyGEOTIFF/" + state + "/" + county +"/clipped.TIF.xml"
    with open(xmlFile, 'r') as f:
        data = f.read()
        Bs_data = bs4.BeautifulSoup(data, "xml")
        print(Bs_data)
#https://www.qgis.org