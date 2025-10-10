app.layout = dbc.Container([
    html.H3("🌍 Climate Risk Dashboard", style={"textAlign": "center"}),
    dbc.Row([
        dbc.Col([
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
                    style={"width": "50%", "margin": "auto", "textAlign": "center", "gap": "10px"},
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
                        # dl.TileLayer(id="ee-layer")  # Placeholder for EE layers
                        html.Div(id="dynamic-layers")
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