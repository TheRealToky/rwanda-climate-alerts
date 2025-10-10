from config import EE_PROJECT
import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project=EE_PROJECT)
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

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


def get_dataset_info(district, dataset_name, dataset_info):
    dataset = dataset_info[dataset_name]

    plot_params = {
        "district": district,
        "list_of_bands": dataset["list of bands"],
        "title": dataset["title"] + district,
        "xlabel": dataset["xlabel"],
        "ylabel": dataset["ylabel"],
        "ylim_min": dataset["ylim_min"],
        "ylim_max": dataset["ylim_max"]
    }

    return plot_params


def plot_dataset_test(dataframe, dataset_name, ax, dataset_parameters=None):
    if dataset_name == "era5_temp":
        if dataset_parameters:
            dataframe["temperature_2m"] = dataframe["temperature_2m"].apply(t_kelvin_to_celsius)
        else:
            dataframe["agg"] = dataframe["agg"].apply(t_kelvin_to_celsius)

    if dataset_parameters:
        district = f"{dataset_parameters["district"]} (trend)"
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # e.g., "Jun 2025"
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        ax.set_title(dataset_parameters["title"], fontsize=16)
        ax.set_xlabel(dataset_parameters["xlabel"], fontsize=14)
        ax.set_ylabel(dataset_parameters["ylabel"], fontsize=14)
        ax.set_ylim(dataset_parameters["ylim_min"], dataset_parameters["ylim_max"])
        ax.grid(lw=0.5, ls='--', alpha=0.7)

        ax.scatter(dataframe["datetime"], dataframe[dataset_parameters["list_of_bands"]],
                   color='gray', linewidth=1, alpha=0.1, label=district)
    else:
        x = dataframe["datetime"]
        y = dataframe["agg"]
        ax.scatter(x, y, s=100, color='red', linewidth=1, alpha=0.5, label="Mean")
        ax.plot(x, y, color='gray', linestyle='--', linewidth=1, label='Graph')

    ax.legend(fontsize=14, loc='upper right')


def get_daily_average(dataframe, dataset_info):
    dataframe = dataframe.drop("time", axis=1)
    df_combined = dataframe.groupby("datetime").agg(
        agg = (dataset_info["list of bands"][0], "mean"),
    ).reset_index()
    return df_combined
