import geopandas
import geopandas as gpd
from matplotlib import pyplot as plt
from numpy.ma.core import shape


class GeoPandasFuncs:
    def __init__(self):
        pass

    def readFile(self, filename):
        shp = geopandas.read_file(filename)
        #print(shp.head(2))

        dfNew = shp[shp['NAME'] =='Lubbock']
        print(dfNew)
        #shp.plot()
        #plt.show()
        dfNew.plot()
        plt.show()

if __name__ == "__main__":
    gpf = GeoPandasFuncs()
    filePath = "./tl_2023_us_county/tl_2023_us_county.shp"

    gpf.readFile(filePath)

