
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import pickle
from label_samples_time_hexa import label_samples
from vizualize import draw_time_bin_hexagons, draw_all_boarders_for_time_bin
from func import rename_time_bins, calc_dist_time_bin, normalize_distances

# Title
st.title('GeoGenTrack')

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
        st.session_state['matrix'] = pd.read_pickle('/home/jaro/Project/GeoGeneTrack/3_ibs_dist/ibs_dist.mibs.pkl')
        st.experimental_rerun()

# Once setup is done, show the map and time bin selection
if 'setup_done' in st.session_state and st.session_state['setup_done']:
        
    df = label_samples("/home/jaro/Project/GeoGeneTrack",st.session_state['time_bins'],st.session_state['resolution'])
    time_bins = rename_time_bins(df)
    time_bins = calc_dist_time_bin(df, st.session_state['matrix'])
    
    # dropdown to select time bins
    selected_time_bin = st.sidebar.selectbox("Time Bin", options=time_bins)
    timebin = time_bins[selected_time_bin]
    
    # checkbox for normalizing IBS values
    if st.sidebar.checkbox("Normalize IBS values", value=False):
        timebin = normalize_distances(timebin)
    
    # input for entering a threshold between 0 and 1
    threshold = st.sidebar.number_input('choose IBS threshold (0 - 1):', min_value=0.0, max_value=1.0, value=1.0, step=0.00001)

    m = draw_time_bin_hexagons(timebin, None)
    m = draw_all_boarders_for_time_bin(timebin, m, threshold)
 
    # Static map display
    folium_static(m)
    
    # Return to Home button
    st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    if st.sidebar.button('Return to Home', key='home'):
        clear_state()
        st.experimental_rerun()