import streamlit as st
from src.risk_map import make_map
from src.plot import get_time_series, ee_array_to_df, plot_dataset, dataset_dict
from src.fetch_datasets import fetch_all

def main():
    chirps, era5_temp, soil_moist, ndvi, dem, slope = fetch_all()
    st.write('''
    Welcome to rwanda-climate-alerts!

    Feel free to look up maps and charts
    ''')

    risk_map = make_map()

    chirps_time_series = get_time_series(
                            chirps,
                            "Bugesera",
                            "2024-01-01",
                            "2024-12-31",
                            1000)
    chirps_df = ee_array_to_df(chirps_time_series, dataset_dict["chirps"]["list of bands"])
    chirps_fig, chirps_ax = plot_dataset(chirps_df, "chirps", dataset_dict)

    col1, col2 = st.columns(2)

    with col1:
        risk_map.to_streamlit()
    with col2:
        st.pyplot(chirps_fig)

if __name__ == '__main__':
    main()