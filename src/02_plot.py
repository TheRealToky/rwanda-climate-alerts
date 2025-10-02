import ee
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from geometry import districts, rwanda, rwanda_buffered
from fetch_datasets import fetch_all

chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()

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

    date_range = [start_date, end_date]

    return district_time_series, date_range


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
    """Converts MODIS LST units to degrees Celsius."""
    t_celsius =  t_kelvin - 273.15
    return t_celsius


def plot_dataset(dataset_info[dataset]):
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.scatter(dataframe['datetime'], dataframe[band],
               color='black', linewidth=1, alpha=0.7, label=label)
               # c='black', alpha=0.2, label='Bugesera (data)')

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


def make_plot(image_collection, district_name, start_date, end_date, scale):
    time_series, date_range = get_time_series(image_collection, district_name, start_date, end_date, scale)

    final_df = ee_array_to_df(time_series, list_of_bands)

    fig, ax = plot_dataset()

    return fig, ax

dataset_info = {
    "chirps": {
        "list of bands": ["precipitation"],
        "title": "Precipitation in ",
        "xlabel": "Date",
        "ylabel": "Precipitation [mm]",
        "ylim_min": -0,
        "ylim_max": 100
    }
}