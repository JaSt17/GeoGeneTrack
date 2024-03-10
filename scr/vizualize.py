from h3 import h3
import folium

def draw_hexagons(hexagons, m=None, color='orange', zoom_start=1):
    if m is None:
        # Generate basemap
        m = folium.Map(location=[0.0, 0.0], tiles="Cartodb positron", zoom_start=zoom_start, max_bounds=True)

    def split_hexagon_if_needed(hexagon):
        boundary = h3.h3_to_geo_boundary(hexagon, geo_json=False)
        longitudes = [lon for lat, lon in boundary]

        # Check if the hexagon crosses the antimeridian
        if max(longitudes) - min(longitudes) > 180:
            # Split the hexagon into two parts
            left_polygon = []
            right_polygon = []
            for lat, lon in boundary:
                if lon < 0:
                    left_polygon.append((lat, lon if lon > -180 else -180))
                    right_polygon.append((lat, 180))
                else:
                    left_polygon.append((lat, -180))
                    right_polygon.append((lat, lon if lon < 180 else 180))
            return [left_polygon, right_polygon]
        else:
            return [boundary]

    # Plot hexagons
    for hexagon in hexagons:
        parts = split_hexagon_if_needed(hexagon)
        for part in parts:
            folium.Polygon(
                locations=part,
                weight=1,
                color=color,
                fill_opacity=0.3,
                fill=True
            ).add_to(m)
    return m

# this function takes two hexagons and a map and draws the shared border between the two hexagons
def draw_borders(hexagon1, hexagon2, m, color='red', ibs=None):
    # get the midpoint of both hexagons
    mid1 = h3.h3_to_geo(hexagon1)
    mid2 = h3.h3_to_geo(hexagon2)

    # Draw line between the two midpoints
    line = [mid1, mid2]
    folium.PolyLine(locations=line,
                    color=color,
                    weight=1).add_to(m)
    # Add a text over the line if ibs is not None
    if ibs is not None:
        folium.Marker([sum([x[0] for x in line])/len(line),
                       sum([x[1] for x in line])/len(line)], 
                      icon=folium.DivIcon(html=f'<div style="font-size: 20; color: black;">{ibs}</div>')).add_to(m)
    return m

# this function takes a timebin and a map and draws all the borders between neighboring hexagons in the timebin
def draw_all_boarders_for_time_bin(timebin, m, threshold=1):
    # loop through all hexagons in the timebin
    for pair in timebin:
        if timebin[pair] < threshold:
            m = draw_borders(pair[0], pair[1], m, ibs=timebin[pair])
    return m

