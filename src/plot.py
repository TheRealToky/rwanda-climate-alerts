import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

# try:
#     ee.Initialize(project="rwanda-climate-alerts")
# except Exception as e:
#     print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# from src.geometry import districts, rwanda, rwanda_buffered
from src.fetch_datasets import fetch_all

chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()

dataset_dict = {
    "chirps": {
        "dataset": chirps,
        "list of bands": ["precipitation"],
        "title": "Precipitation in ",
        "xlabel": "Date",
        "ylabel": "Precipitation [mm]",
        "ylim_min": -0,
        "ylim_max": 100
    },
    "era5_temp": {
        "dataset": era5_temp,
        "list of bands": ["temperature_2m"],
        "title": "Temperature in ",
        "xlabel": "Date",
        "ylabel": "Temperature [C]",
        "ylim_min": 10,
        "ylim_max": 30
    },
    "soil_moist": {
        "dataset": soil_moist,
        "list of bands": ["volumetric_soil_water_layer_1"],
        "title": "Soil moisture in ",
        "xlabel": "Date",
        "ylabel": "Moisture [?]",
        "ylim_min": -0,
        "ylim_max": 1
    },
    "ndvi": {
        "dataset": ndvi,
        "list of bands": ["NDVI"],
        "title": "NDVI in ",
        "xlabel": "Date",
        "ylabel": "NDVI [?]",
        "ylim_min": -0,
        "ylim_max": 10000
    }
}

# Fetch Time series
def get_time_series(image_collection, district_name, start_date, end_date, scale):
    district = ee.FeatureCollection("FAO/GAUL/2015/level2") \
                    .filter(ee.Filter.eq("ADM0_NAME", "Rwanda")) \
                    .filter(ee.Filter.eq("ADM2_NAME", district_name)) \
                    .geometry()

    district_time_series = image_collection \
                            .filterDate(start_date, end_date) \
                            .getRegion(district, scale=scale) \
                            .getInfo()

    # date_range = [start_date, end_date]

    return district_time_series


# Convert to pandas DataFrame
def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time','datetime',  *list_of_bands]]

    return df


def t_kelvin_to_celsius(t_kelvin):
    """Converts Kelvin units to degrees Celsius."""
    t_celsius =  t_kelvin - 273.15
    return t_celsius


def plot_dataset(dataframe, district, dataset_name, dataset_info):
    fig, ax = plt.subplots(figsize=(14, 6))

    dataset = dataset_info[dataset_name]

    list_of_bands = dataset["list of bands"]
    title = dataset["title"] + district
    xlabel = dataset["xlabel"]
    ylabel = dataset["ylabel"]
    ylim_min = dataset["ylim_min"]
    ylim_max = dataset["ylim_max"]

    if dataset_name == "era5_temp":
        dataframe["temperature_2m"] = dataframe["temperature_2m"].apply(t_kelvin_to_celsius)

    ax.scatter(dataframe["datetime"], dataframe[list_of_bands[0]],
               color='gray', linewidth=1, alpha=0.7, label=f"{district} (trend)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # e.g., "Jun 2025"
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # extreme = dataframe[dataframe['precipitation'] > 60]
    # ax.scatter(extreme['datetime'], extreme['precipitation'],
    #            color='orange', edgecolor='red', s=80, zorder=3, label='Extreme rain')

    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_ylim(ylim_min, ylim_max)
    ax.grid(lw=0.5, ls='--', alpha=0.7)
    ax.legend(fontsize=14, loc='lower right')

    return fig, ax

def main():
    district_time_series, date_range = get_time_series(
        dataset_dict["chirps"]["dataset"],
        "Bugesera",
        "2024-01-01",
        "2024-12-31",
        1000)

    df = ee_array_to_df(district_time_series, dataset_dict["chirps"]["list of bands"])

    # Plot with matplotlib
    fig, ax = plot_dataset(df, "Bugesera", "chirps", dataset_dict)
    plt.show()

if __name__ == '__main__':
    main()