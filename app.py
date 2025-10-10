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
from src.plot import *
from src.fetch_datasets import fetch_all
# from src.geometry import districts

import ee
try:
    ee.Authenticate()
except Exception as e:
    print(f"Error authenticating Earth Engine: {e}. Please ensure you have Earth Engine access.")

try:
    ee.Initialize(project="rwanda-climate-alerts")
    # ee.Initialize()
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please ensure you are authenticated.")


# ---- Load your data ----
district_df = pd.read_csv("data/district_boundaries/csv/District_Boundaries.csv")
district_list = np.sort(district_df["district"].unique())
chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
dataset_list = tuple(dataset_dict.keys())

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
    html.H3("🌍 Climate Risk Dashboard", style={"textAlign": "center", "marginBottom": "30px"}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Map Layers"),
                dbc.CardBody([
                    dcc.Checklist(
                        id="layer-checklist",
                        options=[
                            {"label": "Flood Risk", "value": "flood"},
                            {"label": "Drought Risk", "value": "drought"},
                            {"label": "Landslide Risk", "value": "landslide"},
                            {"label": "District Boundaries", "value": "districts"},
                        ],
                        value=["districts"],
                        inline=True,
                        style={"width": "100%", "textAlign": "center"},
                    ),
                    dl.Map(
                        id="map",
                        center=[-1.94, 30.06],
                        zoom=8,
                        children=[
                            dl.TileLayer(
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                attribution="© OpenStreetMap contributors",
                            ),
                            html.Div(id="dynamic-layers")
                        ],
                        style={"width": "100%", "height": "450px", "marginTop": "10px"},
                    )
                ])
            ], style={"marginBottom": "20px"})
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("District Data"),
                dbc.CardBody([
                    html.H5("Select district", style={"marginBottom": "10px"}),
                    dcc.Dropdown(
                        options=[{"label": d, "value": d} for d in district_list],
                        value=district_list[0],
                        id="district-dropdown",
                        style={"marginBottom": "15px"}
                    ),
                    dcc.Dropdown(
                        options=[
                            {"label": "Rainfall", "value": "chirps"},
                            {"label": "Temperature", "value": "era5_temp"},
                            {"label": "Soil Moisture", "value": "soil_moist"},
                            {"label": "Vegetation health", "value": "ndvi"},
                        ],
                        value="chirps",
                        id="dataset-dropdown",
                        style={"marginBottom": "15px"}
                    ),
                    html.Img(id="risk-plot", style={"width": "100%", "marginTop": "10px", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"})
                ])
            ])
        ], width=6)
    ]),
    dbc.Container([
        html.Footer(
            "© 2025 Rwanda Climate Alerts | Powered by Earth Engine & Dash",
            style={"textAlign": "center", "marginTop": "40px", "color": "#888"}
        )
    ], fluid=True)
], fluid=True)


# ---- Callbacks ----
@app.callback(
    Output("risk-plot", "src"),
    Input("district-dropdown", "value"),
    Input("dataset-dropdown", "value")
)
def update_plot(selected_district, selected_dataset):
    district_time_series = get_time_series(
                            dataset_dict[selected_dataset]["dataset"],
                            selected_district,
                            "2024-01-01",
                            "2024-12-31",
                            1000)

    district_baseline = get_time_series(
                            dataset_dict[selected_dataset]["dataset"],
                            selected_district,
                            "2005-01-01",
                            "2020-12-31",
                            1000)

    df = ee_array_to_df(district_time_series, dataset_dict[selected_dataset]["list of bands"])
    daily_average_df = get_daily_average(df, dataset_dict[selected_dataset])
    baseline_df = ee_array_to_df(district_baseline, dataset_dict[selected_dataset])

    # Plot with matplotlib
    fig, ax = plt.subplots(figsize=(14, 6))
    dataset_info = get_dataset_info(selected_district, selected_dataset, dataset_dict)

    plot_dataset_test(df, selected_dataset, ax, dataset_info)
    plot_dataset_test(daily_average_df, selected_dataset, ax)
    plot_dataset_test(baseline_df, selected_dataset, ax)

    plt.tight_layout()

    # Convert to base64 for display in Dash
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return "data:image/png;base64," + encoded


# ---- Callback ----
@app.callback(
    Output("dynamic-layers", "children"),
    Input("layer-checklist", "value")
)
def update_layer(selected_layers):
    order = ["landslide", "drought", "flood", "districts"]

    layers = []
    for layer_name in order:
        if layer_name in selected_layers:
            tile_url = get_image_url(layer_name)
            layers.append(dl.TileLayer(url=tile_url, opacity=0.8))
    return layers

if __name__ == "__main__":
    app.run(
        debug=True
        # dev_tools_props_check=True,
        # dev_tools_hot_reload=True,
        # dev_tools_ui=True,
        # dev_tools_silence_routes_logging=False
    )