
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd

st.title('GeoGenTrack')
time_bins = st.slider('Select a number of time bins', 1, 30, 15, 1)
resolutuion = st.slider('Select a resolution', 1, 13, 2, 1)
if st.button('Run'):
    print("Running GeoGeneTrack")