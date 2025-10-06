# import geopandas as gpd
# import geemap.foliumap as geemap
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
import numpy as np
import pandas as pd

from dash import Dash, html, dcc, Input, Output
import dash_leaflet as dl
import dash_bootstrap_components as dbc

import io, base64

from src.risk_map import get_image_url
from src.plot import get_time_series, ee_array_to_df, plot_dataset, dataset_dict
from src.fetch_datasets import fetch_all
# from src.geometry import districts

import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project="rwanda-climate-alerts")
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")


# ---- Load your data ----
district_df = pd.read_csv("data/district_boundaries/csv/District_Boundaries.csv")
district_list = np.sort(district_df["district"].unique())
chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
# dataset_dict = {
#     "chirps": {
#         "dataset": chirps,
#         "list of bands": ["precipitation"],
#         "title": "Precipitation in ",
#         "xlabel": "Date",
#         "ylabel": "Precipitation [mm]",
#         "ylim_min": -0,
#         "ylim_max": 100
#     },
#     "era5_temp": {
#         "dataset": era5_temp,
#         "list of bands": ["temperature_2m"],
#         "title": "Temperature in ",
#         "xlabel": "Date",
#         "ylabel": "Temperature [C]",
#         "ylim_min": 10,
#         "ylim_max": 30
#     },
#     "soil_moist": {
#         "dataset": soil_moist,
#         "list of bands": ["volumetric_soil_water_layer_1"],
#         "title": "Soil moisture in ",
#         "xlabel": "Date",
#         "ylabel": "Moisture [?]",
#         "ylim_min": -0,
#         "ylim_max": 1
#     },
#     "ndvi": {
#         "dataset": ndvi,
#         "list of bands": ["NDVI"],
#         "title": "NDVI in ",
#         "xlabel": "Date",
#         "ylabel": "NDVI",
#         "ylim_min": -0,
#         "ylim_max": 10000
#     }
# }
dataset_list = tuple(dataset_dict.keys())

# flood_risk, drought_risk, landslide_risk = calculate_indexes()
# map_layers_dict = {
#     "districts": districts,
#     "flood": flood_risk,
#     "drought": drought_risk,
#     "landslide": landslide_risk,
# }

# ---- Build the map (geemap + EE) ----
# Map = make_map()
# Map.add_basemap("HYBRID")
#
# Save map as HTML so we can embed in Dash
# Map.save("map.html")
# output_html_file = "map.html"
# Map.to_html(filename=output_html_file, title="Risk Index Map", width="100%", height="500px")

# ---- Create Dash app ----
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H3("🌍 Climate Risk Dashboard", style={"textAlign": "center"}),
    dbc.Row([
        dbc.Col([
                dcc.Dropdown(
                    id="layer-select",
                    options=[
                        {"label": "District Boundaries", "value": "districts"},
                        {"label": "Flood Risk", "value": "flood"},
                        {"label": "Drought Risk", "value": "drought"},
                        {"label": "Landslide Risk", "value": "landslide"},
                    ],
                    value="districts",
                    clearable=False,
                    style={"width": "50%", "margin": "auto"}
                ),
                dl.Map(
                    id="map",
                    center=[-1.94, 30.06],
                    zoom=7,
                    children=[
                        dl.TileLayer(
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                            attribution="© OpenStreetMap contributors",
                        ),
                        dl.TileLayer(id="ee-layer")  # Placeholder for EE layers
                    ],
                    style={"width": "100%", "height": "600px", "margin": "auto", "marginTop": "10px"},
                )
        ], width=6),

        dbc.Col([
            html.H5("Select district"),
            dcc.Dropdown(
                options=[{"label": d, "value": d} for d in district_list],
                value=district_list[0],
                id="district-dropdown"
            ),
            dcc.Dropdown(
                # options=[{"label": d, "value": d} for d in dataset_list],
                options=[
                    {"label": "Rainfall", "value": "chirps"},
                    {"label": "Temperature", "value": "era5_temp"},
                    {"label": "Soil Moisture", "value": "soil_moist"},
                    {"label": "Flora health", "value": "ndvi"},
                ],
                value="chirps",
                id="dataset-dropdown"
            ),
            html.Img(id="risk-plot", style={"width": "100%", "marginTop": "10px"})
        ], width=6)
    ])
], fluid=True)


# ---- Callbacks ----
@app.callback(
    Output("risk-plot", "src"),
    Input("district-dropdown", "value"),
    Input("dataset-dropdown", "value")
)
def update_plot(selected_district, selected_dataset):
    # subset = df[df["district"]] == selected_district

    district_time_series = get_time_series(
                            dataset_dict[selected_dataset]["dataset"],
                            selected_district,
                            "2024-01-01",
                            "2024-12-31",
                            1000)

    df = ee_array_to_df(district_time_series, dataset_dict[selected_dataset]["list of bands"])

    # Plot with matplotlib
    fig, ax = plot_dataset(df, selected_district, selected_dataset, dataset_dict)
    plt.tight_layout()
    # fig, ax = plt.subplots(figsize=(6, 3))
    # ax.plot(subset["date"], subset["risk"], marker="o")
    # ax.set_title(f"Risk over time: {selected_district}")
    # ax.set_xlabel("Date")
    # ax.set_ylabel("Risk Index")

    # Convert to base64 for display in Dash
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return "data:image/png;base64," + encoded


# ---- Callback ----
@app.callback(
    Output("ee-layer", "url"),
    Input("layer-select", "value")
)
def update_layer(selected):
    return get_image_url(selected)


if __name__ == "__main__":
    app.run(
        debug=True
        # dev_tools_props_check=True,
        # dev_tools_hot_reload=True,
        # dev_tools_ui=True,
        # dev_tools_silence_routes_logging=False
    )