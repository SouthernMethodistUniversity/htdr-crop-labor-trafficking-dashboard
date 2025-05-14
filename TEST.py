import numpy
import numpy as np
import rasterio as rs
#from fontTools.ttLib.tables.otConverters import UInt8
#from matplotlib import pyplot
#import matplotlib.pyplot as plt
from PIL import Image
import cv2
from matplotlib import cm


import tifffile as tf
from numpy import dtype


#file = "CountyGEOTIFF/Texas/Dallas/clipped.tfw"
def showImage(state,county):
    #file = "CountyGEOTIFF/Texas/Lubbock/clipped.TIF"
    file = "CountyGEOTIFF/"+state+"/"+county+"/clipped.TIF"
    raster = rs.open(file)
    array = raster.read()

    mask = raster.read_masks(1)
    masked = np.ma.array(array[0], mask=np.equal(mask, 0))

    #pyplot.imshow(masked)
    #pyplot.show()

def use_tifffile(state,county):
    file = "CountyGEOTIFF/" + state + "/" + county + "/clipped.TIF"

    arr = tf.imread(file)
    print(arr.shape)

    image = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    #newIm = Image.fromarray(arr)
    #newIm.show()

def convertToArray(state,county):
    #filepath
    file = "CountyGEOTIFF/"+ state+ "/"+county+ "/clipped.TIF"

    #read file and convert it to RGB
    im = Image.open(file)
    im = im.convert('RGB')

    #convert the image to a np array
    #imarr = np.array(im, dtype=np.uint8)
    imarr = np.array(im)
    print(imarr.shape)

    #print(imarr)
    #imarr = imarr[imarr==0] =

    print(imarr[0][0][0])



    img = Image.fromarray(imarr)
    img.show()



def convertToMatPlot(state,county):
    '''DOES NOT DO ANYTHING'''
    file = "CountyGEOTIFF/" + state + "/" + county + "/clipped.TIF"
    #img = plt.imread(file)

#use_tifffile("Texas","Lubbock")
convertToArray("Texas","Dallas")
#showImage("Texas","Lubbock")

#convertToMatPlot("Texas","Lubbock")
