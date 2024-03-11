from h3 import h3
import folium
from func import normalize_distances
import matplotlib.colors as mcolors

def draw_hexagons(hexagons, m=None, color='orange', zoom_start=1):
    if m is None:
        # Generate basemap
        m = folium.Map(location=[0.0, 0.0], tiles="Esri worldstreetmap", zoom_start=zoom_start, max_bounds=True)

    def split_hexagon_if_needed(hexagon):
        boundary = h3.h3_to_geo_boundary(hexagon, geo_json=False)
        longitudes = [lon for lat, lon in boundary]

        # Check if the hexagon crosses the antimeridian
        if max(longitudes) - min(longitudes) > 180:
            boundary = list(boundary)
            first_hex = list()
            second_hex = list()
            # make get two hexagons from the original one
            for i in range(len(boundary)):
                if boundary[i][1] <= 0:
                    first_hex.append((boundary[i][0], boundary[i][1] + 360))
                    second_hex.append((boundary[i][0], boundary[i][1]))
                if boundary[i][1] > 0:
                    first_hex.append((boundary[i][0], boundary[i][1]))
                    second_hex.append((boundary[i][0], boundary[i][1] - 360))
            # return two tuples of coordinates
            return [tuple(first_hex), tuple(second_hex)]
        else:
            # return the original hexagon
            return [boundary]

    # Plot hexagons
    for hexagon in hexagons:
        parts = split_hexagon_if_needed(hexagon)
        for part in parts:
            folium.Polygon(
                locations=part,
                weight=1,
                color=color,
                fill_opacity=0.2,
                fill=True
            ).add_to(m)
    return m

# this function takes two hexagons and a map and draws a line between the two midpoints of the hexagons
def draw_borders(hexagon1, hexagon2, m, color, ibs=None):
    # get the midpoint of both hexagons
    mid1 = h3.h3_to_geo(hexagon1)
    mid2 = h3.h3_to_geo(hexagon2)
    
    # check if the points are on the opposite sides of the antimeridian
    if abs(mid1[1] - mid2[1]) > 180:
        # if they are, add 360 to the longitude of the point with the smaller longitude
        if mid1[1] < mid2[1]:
            mid1 = (mid1[0], mid1[1] + 360)
        else:
            mid2 = (mid2[0], mid2[1] + 360)
            
    # Draw line between the two midpoints
    line = [mid1, mid2]
    folium.PolyLine(locations=line,
                    color=color,
                    weight=5,
                    tooltip=f"{ibs}").add_to(m)
    return m

# this function takes a timebin and a map and draws all neighboring lines for the hexagons in the timebin
def draw_all_boarders_for_time_bin(timebin, m, color="red", threshold=1):
    # get the normalized ibs for the color gradient
    normalized_timebin = normalize_distances(timebin)
    # color gradient 
    colors = [(10,0,0), (1,1,0)]
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_darkred_to_yellow", colors)
    # loop through all hexagons in the timebin
    for pair in timebin:
        if timebin[pair] < threshold:
            # get the color for the line based on the normalized ibs
            col = mcolors.to_hex(cmap(normalized_timebin[pair]))
            m = draw_borders(pair[0], pair[1], m, color= col, ibs=timebin[pair])
    return m

