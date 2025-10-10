# Imports and Pre-requisites
import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project="rwanda-climate-alerts")
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")
from src.geometry import districts, rwanda, rwanda_buffered

# Collect Datasets
def fetch_dataset(image_collection,
                  start_date="2005-01-01",
                  end_date="2025-07-31",
                  geometry=rwanda_buffered,
                  select=True, band=None):
    filtered_image_collection = ee.ImageCollection(image_collection) \
                                .filterDate(start_date, end_date) \
                                .filterBounds(geometry) \
                                .map(lambda img: img.clip(geometry))

    if select:
        filtered_image_collection = filtered_image_collection.select(band)

    return filtered_image_collection

def fetch_all():
    # CHIRPS Daily Rainfall (mm/day)
    chirps = fetch_dataset("UCSB-CHG/CHIRPS/DAILY",
                           select=False)

    # ERA5 Land Monthly Temperature
    era5_temp = fetch_dataset("ECMWF/ERA5_LAND/MONTHLY_AGGR",
                              select=True,
                              band="temperature_2m")

    # Soil Moisture (ERA5 Land)
    soil_moist = fetch_dataset("ECMWF/ERA5_LAND/MONTHLY_AGGR",
                               select=True,
                               band="volumetric_soil_water_layer_1")

    # MODIS NDVI (monthly, 250 m)
    ndvi = fetch_dataset("MODIS/061/MOD13A1",
                         select=True,
                         band="NDVI")

    # DEM (SRTM ~30m resolution)
    dem = ee.Image("USGS/SRTMGL1_003").clip(rwanda_buffered)

    # Calculate slope (degrees)
    slope = ee.Terrain.slope(dem)

    return chirps, era5_temp, soil_moist, ndvi, dem, slope


# def main():
#     chrips = fetch_dataset("UCSB-CHG/CHIRPS/DAILY")
#     chirps_2, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
#
#     print(type(chrips))
#     print(type(chirps_2))
#     print(type(era5_temp))
#     print(type(era5_temp))
#     print(type(ndvi))
#     print(type(dem))
#     print(type(slope))
#
# if __name__ == "__main__":
#     main()