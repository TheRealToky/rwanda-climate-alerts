# import geemap
import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project="rwanda-climate-alerts")
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")

from src.geometry import districts
from src.fetch_datasets import fetch_all

chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()

def aggregate_monthly(image_collection):
    monthly_result = image_collection.map(lambda img: img.set("month", img.date().format("YYYY-MM")))
    monthly_sum = monthly_result.reduce(ee.Reducer.sum())
    return monthly_result, monthly_sum


def calculate_baseline(image_collection):
    # Define baseline period (e.g., 2000–2015)
    baseline = image_collection.filterDate("2005-01-01", "2015-12-31")

    # Mean rainfall baseline
    baseline_mean = baseline.mean()

    # Recent period (e.g., 2020–2025)
    recent = image_collection.filterDate("2025-07-01", "2025-07-31").mean()

    # Rainfall anomaly (recent vs baseline)
    anomaly = recent.subtract(baseline_mean).divide(baseline_mean)

    return baseline, baseline_mean, anomaly


def normalize(img, region):
    min_dict = img.reduceRegion(
        reducer=ee.Reducer.min(),
        geometry=region,
        scale=1000,
        maxPixels=1e13,
        bestEffort=True
    ).values().get(0)
    max_dict = img.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=region,
        scale=1000,
        maxPixels=1e13,
        bestEffort=True
    ).values().get(0)

    min_value = ee.Number(min_dict)
    max_value = ee.Number(max_dict)

    return img.subtract(min_value).divide(max_value.subtract(min_value))


def aggregate_risk(risk_index):
    district_stats = risk_index.reduceRegions(
        collection=districts,
        reducer=ee.Reducer.mean(),
        scale=1000
    )
    return district_stats


def calculate_indexes():
    # monthly_chirps, monthly_chirps_sum = aggregate_monthly(chirps)
    # monthly_era5_temp, monthly_era5_temp_sum = aggregate_monthly(era5_temp)
    # monthly_soil_moist, monthly_soil_moist_sum = aggregate_monthly(soil_moist)
    # monthly_ndvi, monthly_ndvi_sum = aggregate_monthly(ndvi)


    rain_baseline, rain_baseline_mean, rain_anomaly = calculate_baseline(chirps)
    temp_baseline, temp_baseline_mean, temp_anomaly = calculate_baseline(era5_temp)
    soil_moist_baseline, soil_moist_baseline_mean, soil_moist_anomaly = calculate_baseline(soil_moist)
    # ndvi_baseline, ndvi_baseline_mean, ndvi_anomaly = calculate_baseline(ndvi)


    rain_norm = normalize(rain_anomaly, districts)
    temp_norm = normalize(temp_anomaly, districts)
    soil_moist_norm = normalize(soil_moist_anomaly, districts)
    # ndvi_norm = normalize(ndvi_anomaly, districts)

    # dem_norm = normalize(dem, districts)
    slope_norm = normalize(slope, districts)


    flood_risk_index = rain_norm.multiply(0.4) \
                        .add(temp_norm.multiply(0.3)) \
                        .add(slope_norm.multiply(0.2))
                        # .add(ndvi_norm.multiply(0.2)) \

    drought_risk_index = rain_norm.multiply(-1).add(1).multiply(0.4) \
                        .add(soil_moist_norm.multiply(-1).add(1).multiply(0.3)) \
                        .add(temp_norm.multiply(0.3))
                        # .add(ndvi_norm.multiply(-1).add(1).multiply(0.2)) \
    # NDVI is causing some trouble, still in the process of figuring it out

    landslide_risk_index = rain_norm.multiply(0.4) \
                            .add(soil_moist_norm.multiply(0.3)) \
                            .add(slope_norm.multiply(0.3))


    # flood_risk_stats = aggregate_risk(flood_risk_index)
    # drought_risk_stats = aggregate_risk(drought_risk_index)
    # landslide_risk_stats = aggregate_risk(landslide_risk_index)

    return flood_risk_index, drought_risk_index, landslide_risk_index


flood_risk, drought_risk, landslide_risk = calculate_indexes()
map_layers_dict = {
    "districts": districts,
    "flood": flood_risk,
    "drought": drought_risk,
    "landslide": landslide_risk,
}

def get_image_url(selected_layer):
    dataset = map_layers_dict[selected_layer]
    if selected_layer == "districts":
        fc = dataset
        # vis = {"color": "black"}
        vis = {"palette": ["black"]}
        image = ee.Image().paint(fc, 0, 1)
        map_id = ee.data.getMapId({"image": image.visualize(**vis)})
        tile_url = map_id["tile_fetcher"].url_format

    else:
        vis_params = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
        map_id_dict = ee.data.getMapId({'image': dataset.visualize(**vis_params)})
        tile_url = map_id_dict['tile_fetcher'].url_format

    return tile_url


# def main():
#     flood_risk_index, drought_risk_index, landslide_risk_index = calculate_indexes()
#     flood_index_url = get_image_url(flood_risk_index)
#     drought_index_url = get_image_url(drought_risk_index)
#     landslide_index_url = get_image_url(landslide_risk_index)
#
#     print("Flood Risk:", flood_index_url, type(flood_index_url,))
#     print("Drought Risk:", drought_index_url, type(drought_index_url,))
#     print("Landslide Risk:", landslide_index_url, type(landslide_index_url,))
#
# if __name__ == '__main__':
#     main()