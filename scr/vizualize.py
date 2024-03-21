from h3 import h3
import folium
from folium import Map, Element
from func import normalize_distances
import matplotlib.colors as mcolors
import base64


# function that draws hexagons on a map
def draw_hexagons(hexagons, m=None, color='orange', zoom_start=1):
    # Create a map if it is not provided
    if m is None:
        m = folium.Map(location=[0.0, 0.0], tiles="Esri worldstreetmap", zoom_start=zoom_start, max_bounds=True)

    # function that splits a hexagon if it crosses the antimeridian
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
            # return two tuples of coordinates of the two hexagons
            return [tuple(first_hex), tuple(second_hex)]
        else:
            # return the original hexagon
            return [boundary]

    # Plot hexagons
    for hexagon in hexagons:
        # split the hexagon if it crosses the antimeridian
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
                    # add the ibs value as a tooltip
                    tooltip=f"{ibs}").add_to(m)
    return m

# this function takes a time bin and a map and draws all neighboring lines for the hexagons in that time bin
def draw_all_boarders_for_time_bin(time_bin, m, color="red", threshold=1.0):
    # get the normalized ibs for the color gradient
    normalized_time_bin = normalize_distances(time_bin)
    
    # create a color gradient to color the lines based on the normalized ibs
    colors = [(255,0,0), (1,1,0)]
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_darkred_to_yellow", colors)
    
    # loop through all hexagons in the time bin
    for pair in time_bin:
        # only draw the line if the ibs is below the threshold
        if time_bin[pair] <= threshold:
            # get the color for the line based on the normalized ibs
            col = mcolors.to_hex(cmap(normalized_time_bin[pair]))
            m = draw_borders(pair[0], pair[1], m, color= col, ibs=time_bin[pair])
    return m

def add_colorbar_to_map(m, path):
    
    new_map = m
    
    # Open the image file in binary mode
    with open(path, 'rb') as image_file:
        # Read the binary image data
        binary_data = image_file.read()
        # Encode the binary data to base64
        base64_encoded_data = base64.b64encode(binary_data)
        # Decode the base64 bytes to string
        base64_image = base64_encoded_data.decode('utf-8')

    # JavaScript to add the colorbar to the map
    js = f"""
    <script>
    function addColorBar() {{
        var colorBarDiv = L.DomUtil.create('div', 'leaflet-control');
        colorBarDiv.style.backgroundColor = 'white';
        colorBarDiv.style.padding = '5px';
        colorBarDiv.innerHTML = '<img src="data:image/png;base64,{base64_image}">';

        var zoomControlContainer = document.getElementsByClassName('leaflet-control-zoom')[0].parentNode;
        if (zoomControlContainer.firstChild) {{
            zoomControlContainer.insertBefore(colorBarDiv, zoomControlContainer.firstChild);
        }} else {{
            zoomControlContainer.appendChild(colorBarDiv);
        }}
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        addColorBar();
    }});
    </script>
    """

    # Adding the JavaScript to the map
    element = Element(js)
    new_map.get_root().html.add_child(element)

    return new_map