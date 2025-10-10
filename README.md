# Rwanda Climate Alerts

Lightweight Dash dashboard for visualizing climate risk indices (flood, drought, landslide) for Rwanda using Google Earth Engine datasets.

## Features
- Interactive map (dash-leaflet) with selectable risk layers and district boundaries
- Time-series plots for districts (precipitation, temperature, soil moisture, vegetation health (NDVI))
- Simple legend overlay for risk color scale (1 = green low risk, 0 = red high risk)

## Repository structure (important files)
- `app.py` — Dash application entrypoint and layout
- `src/` — application modules
  - `fetch_datasets.py` — Earth Engine dataset loaders
  - `geometry.py` — EE geometries and district FeatureCollection
  - `risk_map.py` — build risk index layers & export tile URLs (incomplete / TODO)
  - `plot.py` — generate time-series plots (incomplete / TODO)
- `data/` — local datasets (CSV/shapefile exports)
- `assets/` — static CSS/JS for Dash (create this folder and add custom CSS)

## Requirements
- Python 3.8+
- Windows OS (development tested on Windows)
- Packages (install with pip):
  - dash, dash-bootstrap-components, dash-leaflet
  - pandas, numpy, matplotlib
  - earthengine-api
  - (optionally) geemap for local testing/visualization

Install quickly:
```bash
python -m pip install -r requirements.txt
```

## Google Earth Engine setup
1. Install Earth Engine API if not installed:
   ```bash
   python -m pip install earthengine-api
   ```
2. Authenticate (command-line recommended):
   ```bash
   earthengine authenticate
   ```
   Follow the printed URL and paste the token when prompted.

3. In code the project is initialized as:
   ```python
   ee.Initialize(project="rwanda-climate-alerts")
   ```
   Ensure your account has access to that project or change to your own EE project.

Note: Earth Engine objects live in the cloud. Local shapefiles must be uploaded as EE assets (or converted to CSV/GeoJSON and accessed locally) — `.getInfo()` only works on EE objects already in the cloud.

## Running the app
From repository root (Windows PowerShell / CMD):
```bash
python app.py
```
Open http://127.0.0.1:8050 in a browser.

## Styling (assets)
Dash auto-loads files in an `assets/` folder. Create `assets/custom.css` to override styles. Example snippet:
```css
/* assets/custom.css */
body { background:#f8fafc; font-family: "Segoe UI", Roboto, Arial; }
.card { border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,0.07); }
.card-header { background:#f0f2f6 !important; font-weight:600; }
```

## Data / Shapefiles
- The app currently expects district boundaries CSV at:
  `data/district_boundaries/csv/District_Boundaries.csv`
- If you have shapefiles and want them as EE FeatureCollections, upload them to Earth Engine assets and reference the asset path in `src/geometry.py` or `src/risk_map.py`.

## Development notes / TODOs
- Several functions in `src/risk_map.py`, `src/plot.py` and `src/fetch_datasets.py` are placeholders and need implementation:
  - risk index calculations, normalization, aggregation
  - image export / tile URL generation (for dash-leaflet)
  - time-series extraction and conversion to pandas DataFrame
- Callbacks in `app.py` are defined but not implemented — implement to return map layers (tile URLs/GeoJSON) and base64 image source for plots.
- Consider caching Earth Engine requests to avoid repeated heavy operations.

## Troubleshooting
- Earth Engine errors: re-run `earthengine authenticate` and ensure `ee.Initialize()` is called. For headless servers, follow the CLI instructions.
- If map tiles are blank: verify `get_image_url` returns a valid tile/XYZ URL or GeoJSON and that dash-leaflet layers are created correctly.
- For local testing of shapefiles: use `geopandas` to inspect before uploading to EE.

## License
Add a license of your choice (e.g., MIT). This repository does not include a license file by default.

## Contact / Next steps
- Implement missing functions in `src/` to produce working layers/plots.
- Upload any local spatial assets to Earth Engine if you want server-side processing and `.getInfo()` usage.
