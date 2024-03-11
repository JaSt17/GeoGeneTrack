
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import pickle
from label_samples_time_hexa import label_samples
from vizualize import draw_hexagons, draw_all_boarders_for_time_bin
from func import rename_time_bins, calc_dist_time_bin, normalize_distances, get_time_bin_hexagons, get_min_max_dist

# Function to clear session state
def clear_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
def get_resoultion_data():
    data = {
    "Resoultion": [0, 1, 2, 3, 4, 5],
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
    col1, col2 = st.columns([1, 2])
    # In the first column, display the image with a desired width
    with col2:
        st.image("img/GeoGenTrack_logo.png", width=100)  # Adjust width as needed
    # In the second column, display the title
    with col1:
        st.title('GeoGenTrack')
        
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
        
    time_bins = st.slider('Select a number of time bins', 1, 30, 10, 1)
    if st.button("Information about time bins"):
        st.write("""
    The ancient samples' dates range from 1890 AD to 108500 BC.
    The data will get organized into time bins, each containing an equal number of samples for analysis.
    """)
        
    resolution = st.slider('Select a resolution', 0, 5, 2, 1)
    if st.button("Information about resolution"):
        st.table(get_resoultion_data())

    allow_k_distance = st.checkbox('Expand Search Area', value=False)
    if st.button("Information about expanding search area"):
        st.write("""
    As the resolution increases, the size of each hexagon decreases, resulting in a reduced likelihood of adjacent hexagons being direct neighbors. 
    To ensure visibility of interactions (ibs) between closely situated hexagons, users are encouraged to utilize the "Expand Search Area" option.
    When activated, this feature systematically searches through hexagons at greater distances until a neighboring hexagon is identified.
    """)
        
    if st.button('Run'):
        st.text('Running GeoGeneTrack...')
        st.session_state['setup_done'] = True
        st.session_state['time_bins'] = time_bins
        st.session_state['resolution'] = resolution
        st.session_state['allow_k_distance'] = allow_k_distance
        st.session_state['matrix'] = pd.read_pickle('/home/jaro/Project/GeoGeneTrack/3_ibs_dist/ibs_dist.mibs.pkl')
        st.experimental_rerun()

# Once setup is done, show the map and time bin selection
if 'setup_done' in st.session_state and st.session_state['setup_done']:
    # Return to Home button
    if st.sidebar.button('Return to Home', key='home'):
        clear_state()
        st.experimental_rerun()
        
    df = label_samples("/home/jaro/Project/GeoGeneTrack",st.session_state['time_bins'],st.session_state['resolution'])
    time_bins = rename_time_bins(df)
    time_bins_hexagons = get_time_bin_hexagons(df)
    time_bins_dist = calc_dist_time_bin(df, st.session_state['matrix'], st.session_state['allow_k_distance'])
    
    # dropdown to select time bins
    selected_time_bin = st.sidebar.selectbox("Time Bin", options=time_bins)
    hexagons = time_bins_hexagons[selected_time_bin]
    timebin = time_bins_dist[selected_time_bin]
    
    # checkbox for normalizing IBS values
    if st.sidebar.checkbox("Normalize IBS values", value=False):
        timebin = normalize_distances(timebin)
    
    # get min and max distance for the selected time bin for the threshold
    min_dist, max_dist = get_min_max_dist(timebin)
    
    # input for entering a threshold between 0 and 1
    threshold = st.sidebar.slider('choose threshold:', min_dist, max_dist, max_dist, 0.0001)
     
    if st.sidebar.button("Why normalize IBS values?"):
        st.sidebar.write("""
    The majority of IBS values fall within the 0.72 to 0.8 range. Normalization is applied to adjust these values to a 0 to 1 scale within each timebin, enhancing the visibility of differences among the IBS values.

    IMPORTANT NOTE:
    - Normalization is calculated individually for each timebin.
    - The resulting values are dimensionless and serve solely to highlight variations among the IBS values.
    """)

    m = draw_hexagons(hexagons)
    m = draw_all_boarders_for_time_bin(timebin, m, threshold=threshold)

    # Display the map in Streamlit
    folium_static(m, width=800, height=600)