# This is the main file for the GeoGeneTrack web application.
# It is a Streamlit app that allows users to select a number of time bins and a spatial resolution.
# The app then displays a global map for each temporal interval, illustrating the identity by state (IBS) metrics among neighboring regions.

import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import pickle
import os
from label_samples_time_hexa import label_samples
from vizualize import draw_hexagons, draw_all_boarders_for_time_bin
from func import rename_time_bins, calc_dist_time_bin, normalize_distances, get_time_bin_hexagons, get_min_max_dist

# Function to clear session state
def clear_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
# Function to get resolution data as table to display it for the user
def get_resolution_data():
    data = {
    "Resolution": [0, 1, 2, 3, 4, 5],
    "Total number of cells": [122, 842, 5882, 41162, 288122, 2016842],
    "Average cell area (km2)": [4357449.41, 609788.44, 86801.78, 12393.43, 1770.34, 252.90],
    "Average edge length (Km)":  [1281.256011, 483.0568391, 182.5129565, 68.97922179, 26.07175968, 9.854090990]
    }
    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    return df

# Initial screen to select time bins and resolution
if 'setup_done' not in st.session_state:
    st.set_page_config(page_title="GeoGeneTrack", page_icon=":earth_americas:")
    # display the logo and title
    col1, col2 = st.columns([1, 2])
    with col2:
        st.image("img/GeoGenTrack_logo.png", width=100) 
    with col1:
        st.title('GeoGenTrack')
    
    # Button to get information about the tool
    if st.button("What is GeoGeneTrack:"):
        st.write("""
    This tool facilitates the monitoring of discrepancies between geographic and genomic distances within the Allen Ancient DNA Resource (AADR) dataset.
    It enables users to select a specific number of temporal intervals and a spatial resolution. Utilizing these parameters, the tool graphically represents all samples within their respective regions on a global map for each temporal interval.
    Additionally, it illustrates the identity by state (IBS) metrics among neighboring regions. This feature provides users with a rapid and comprehensive visualization of the IBS among geographically proximate areas for each designated temporal segment,
    thereby offering valuable insights into the spatial genomic diversity and its temporal dynamics within the dataset.
    
    IBS: The IBS is a measure of genetic dissimilarity between individuals. It is calculated based on the proportion of alleles shared between two individuals at a set of genetic loci.
    Simply, it measures how genetically similar or different two individuals are. A value of 1 indicates that two individuals are genetically identical, while a value of 0 indicates that two individuals are genetically dissimilar.
    In practice, one would never expect to observe values near 0,even completely unrelated individuals would be expected to share a very large proportion of the genome identical by state by chance alone.

    """)
    
    # Slider to choose the number of time bins and button to get information about it
    time_bins = st.slider('Select a number of time bins', 1, 30, 10, 1)
    if st.button("Information about time bins"):
        st.write("""
    The ancient samples' dates range from 1890 AD to 108500 BC.
    The data will get organized into time bins, each containing an equal number of samples for analysis.
    """)
    
    # Slider to choose the resolution and button to get information about it
    resolution = st.slider('Select a resolution', 0, 5, 2, 1)
    if st.button("Information about resolution"):
        st.table(get_resolution_data())

    # Checkbox to allow expanding the search area and button to get information about it
    allow_k_distance = st.checkbox('Expand Search Area', value=False)
    if st.button("Information about expanding search area"):
        st.write("""
    As the resolution increases, the size of each hexagon decreases, resulting in a reduced likelihood of adjacent hexagons being direct neighbors. 
    To ensure visibility of interactions (ibs) between closely situated hexagons, users are encouraged to utilize the "Expand Search Area" option.
    When activated, this feature systematically searches through hexagons at greater distances until a neighboring hexagon is identified.
    """)
    
    # Button to run the tool
    if st.button('Run'):
        st.text('Running GeoGeneTrack...')
        # Save the selected parameters to the session state
        st.session_state['setup_done'] = True
        st.session_state['time_bins'] = time_bins
        st.session_state['resolution'] = resolution
        st.session_state['allow_k_distance'] = allow_k_distance
        # read the IBS matrix from the file
        # get path to the ibs matrix
        path_to_matrix = os.getcwd()+"/3_ibs_dist/ibs_dist.mibs.pkl"
        st.session_state['matrix'] = pd.read_pickle(path_to_matrix)
        st.experimental_rerun()

# Once setup is done, show the map and time bin selection
if 'setup_done' in st.session_state and st.session_state['setup_done']:
    # Return to Home button
    if st.sidebar.button('Return to Home', key='home'):
        clear_state()
        st.experimental_rerun()
        
    # Load the data with the given number of time bin and hexagon resolution
    df = label_samples(os.getcwd(),st.session_state['time_bins'],st.session_state['resolution'])
    # rename the time bins to a more readable format
    time_bins = rename_time_bins(df)
    # get the hexagons for each time bin
    time_bins_hexagons = get_time_bin_hexagons(df)
    # calculate the average IBS values between neighboring hexagons for each time bin
    time_bins_dist = calc_dist_time_bin(df, st.session_state['matrix'], st.session_state['allow_k_distance'])
    
    # dropdown to select time bins
    selected_time_bin = st.sidebar.selectbox("Time Bin", options=time_bins)
    # get the hexagons and IBS values for the selected time bin
    hexagons = time_bins_hexagons[selected_time_bin]
    time_bin = time_bins_dist[selected_time_bin]
    
    # checkbox for normalizing IBS values
    if st.sidebar.checkbox("Normalize IBS values", value=False):
        # normalize the IBS values
        time_bin = normalize_distances(time_bin)
    
    # get min and max distance for the selected time bin for the threshold
    min_dist, max_dist = get_min_max_dist(time_bin)
    
    # Slider to choose the threshold for the IBS values
    threshold = st.sidebar.slider('choose threshold:', min_dist, max_dist, max_dist, 0.0001)
    
    # Button to get information about normalizing IBS values
    if st.sidebar.button("Why normalize IBS values?"):
        st.sidebar.write("""
    The majority of IBS values fall within the 0.72 to 0.8 range. Normalization is applied to adjust these values to a 0 to 1 scale within each time bin, enhancing the visibility of differences among the IBS values.

    IMPORTANT NOTE:
    - Normalization is calculated individually for each time bin.
    - The resulting values are dimensionless and serve solely to highlight variations among the IBS values.
    """)

    # draw all hexagons in the chosen time bin
    m = draw_hexagons(hexagons)
    # draw all average IBS values between neighboring hexagons for the chosen time bin
    m = draw_all_boarders_for_time_bin(time_bin, m, threshold=threshold)

    # Display the map in Streamlit
    folium_static(m, width=800, height=600) 