from h3 import h3
import folium

# function takes a list of hexagos and a map and draws the hexagons on the map
def draw_hexagons(hexagons, m=None, color='orange', zoom_start=1):
    # if there is no map, create a new one
    if m is None:
        # Generate basemap
                m = folium.Map(location = [50.0, 14.0], 
                 tiles = "Cartodb positron", 
                 zoom_start = zoom_start,
                 max_bounds = True)
    # Plot hexagons        
    for hexagon in hexagons:
        folium.Polygon(
            locations = h3.h3_to_geo_boundary(hexagon, geo_json = False),
            stroke = False,  
            weight = 3,
            color = color,
            fill_opacity=0.3,
            fill=True
        ).add_to(m)
    return m 

# this function takes two hexagons and a map and draws the shared border between the two hexagons
def draw_borders(hexagon1, hexagon2, m, color='red', ibs=None):
    hexagon1_boundary = h3.h3_to_geo_boundary(hexagon1, geo_json=False)
    hexagon2_boundary = h3.h3_to_geo_boundary(hexagon2, geo_json=False)
    # Get shared boundary
    shared_boundary = [x for x in hexagon1_boundary if x in hexagon2_boundary]
    
    # Proceed only if there is a shared boundary
    if shared_boundary:
        # Draw the shared boundary
        folium.PolyLine(shared_boundary,
                        color=color,
                        weight=1).add_to(m)
        # Add a text over the line if ibs is not None
        if ibs is not None:
            folium.Marker([sum([x[0] for x in shared_boundary])/len(shared_boundary),
                           sum([x[1] for x in shared_boundary])/len(shared_boundary)], 
                          icon=folium.DivIcon(html=f'<div style="font-size: 20; color: black;">{ibs}</div>')).add_to(m)
    return m

# this function takes a timebin and a map and draws all the borders between neighboring hexagons in the timebin
def draw_all_boarders_for_time_bin(timebin, m):
    # loop through all hexagons in the timebin
    for pair in timebin:
        m = draw_borders(pair[0], pair[1], m, ibs=timebin[pair])
    return m

# this function takes a timebin and a map and draws all the hexagons in the timebin
def draw_time_bin_hexagons(timebin, m):
    hexagons = {h for pair in timebin for h in pair}
    m = draw_hexagons(hexagons, m)
    return m
