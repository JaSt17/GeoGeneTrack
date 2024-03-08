
import streamlit as st
from h3 import h3
import folium
from streamlit_folium import st_folium
import pandas as pd
from vizualize import vizualize_hexagons
import os
from calc_distances import read_hex_dict
from geogentrack import calc_dist_matrix
from calc_distances import get_hexagons_below_threshold

st.title('GeoGenTrack')
time_bins = st.slider('Select a number of time bins', 1, 30, 15, 1)
resolutuion = st.slider('Select a resolution', 1, 13, 2, 1)
threshold = st.slider('Select a threshold', 0.6, 1.0, 0.73, 0.01)
if st.button('Run'):
    print("Running GeoGeneTrack")
    ibs_matrix=calc_dist_matrix(time_bins, resolutuion)
    path  = os.path.dirname(os.getcwd())
    hexagons_with_high_distance = get_hexagons_below_threshold(path,ibs_matrix, threshold)


    # Initialize an empty set to store hexagons IDs
    hexagons = set()

    # Use Streamlit's session state to track which time bin was selected
    if 'selected_time_bin' not in st.session_state:
        st.session_state.selected_time_bin = None

    for time_bin in hexagons_with_high_distance.keys():
        # get years from time_bin
        years = time_bin.split("-")
        new_years = []
        for year in years:
            if int(year) < 1950:
                year = 1950 - int(year)
                year = str(year) + " ad"
            else:
                year = int(year) - 1950
                year = str(year) + " bc"
            new_years.append(year)

        # When a button is clicked, update the session state with the selected time bin
        if st.sidebar.button(f"{new_years[0]} - {new_years[1]}"):
            st.session_state.selected_time_bin = time_bin

    # Check if a time bin has been selected
    if st.session_state.selected_time_bin:
        # Add hexagons for the selected time bin to the set
        hexagons.update(hexagons_below_threshold[st.session_state.selected_time_bin])

        # Assuming `vizualize_hexagons` is defined somewhere to generate a folium map
        if hexagons:
            folium_map = vizualize_hexagons(hexagons)
            st_folium(folium_map, width=1500)