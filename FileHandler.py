import geopandas as gpd
import pandas as pd

class FileHandler:


    @staticmethod
    def loadFiles():
        # Load the shapefile
        shapefile_path = 'tl_2023_us_county/tl_2023_us_county.shp'
        gdf = gpd.read_file(shapefile_path)

        # Normalize county names to lowercase
        gdf['NAME'] = gdf['NAME'].str.lower()

        # Add a capitalized county names column for display
        gdf['NAME_DISPLAY'] = gdf['NAME'].str.title()

        # Load the CSV file
        csv_file_path = 'southfinal2.csv'
        df_locations = pd.read_csv(csv_file_path)

        # Load the feather file
        feather_file_path = 'combined_pixel_counts.feather'
        df_crops = pd.read_feather(feather_file_path)

        # county names to lowercase
        df_crops['County'] = df_crops['County'].str.lower()

        # Create a mapping of state FIPS codes to state names
        state_fips_codes = {
            '48': 'Texas',
            '06': 'California',
            '04': 'Arizona',
            '35': 'New Mexico',
            '40': 'Oklahoma',
            '22': 'Louisiana',
            '05': 'Arkansas'
        }

        gdf['STATE_NAME'] = gdf['STATEFP'].map(state_fips_codes)

        # Filter counties for the specified states
        filtered_gdf = gdf[gdf['STATE_NAME'].isin(state_fips_codes.values())]

        return filtered_gdf,df_crops,df_locations