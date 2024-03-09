
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from label_samples_time_hexa import label_samples
from vizualize import draw_hexagons
from func import rename_time_bins

# Title
st.title('GeoGenTrack')
st.write("This is a tool to visualize the violations of the correlation between genomic and genetic distance.")

# Function to clear session state
def clear_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# Initial screen to select time bins and resolution
if 'setup_done' not in st.session_state:
    time_bins = st.slider('Select a number of time bins', 1, 30, 10, 1)
    resolution = st.slider('Select a resolution', 1, 8, 2, 1)
    if st.button('Run'):
        st.session_state['setup_done'] = True
        st.session_state['time_bins'] = time_bins
        st.session_state['resolution'] = resolution
        st.experimental_rerun()

# Once setup is done, show the map and time bin selection
if 'setup_done' in st.session_state and st.session_state['setup_done']:
    # Return to Home button
    if st.button('Return to Home', key='home'):
        clear_state()
        st.experimental_rerun()
        
    df = label_samples("/home/jaro/Project/GeoGeneTrack",st.session_state['time_bins'],st.session_state['resolution'])
    hexagons = df.iloc[:,-1].unique().tolist()
    time_bins = rename_time_bins(df)
    
    st.write("Select a time bin:")
    # Create a dropdown to select time bins
    selected_time_bin = st.selectbox("Time Bin", options=time_bins)
    
    # Create and display a folium map
    m = m = draw_hexagons(hexagons,zoom_start=str(st.session_state['resolution']))      
    
    # Static map display
    folium_static(m)