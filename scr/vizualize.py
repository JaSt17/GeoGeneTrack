from h3 import h3
import folium
import pandas as pd
# this is a funciton that can vizualize a polygon on a map

def vizualize_polygon(polyline, color):
    polyline.append(polyline[0])
    lat = [x[0] for x in polyline]
    long = [x[1] for x in polyline]
    m = folium.Map(location=[sum(lat)/len(lat), sum(long)/len(long)], zoom_start=3)
    m.add_child(folium.PolyLine(locations = ployline, color=color, weight=1))
    return m

def vizualize_hexagons(hexagons, color='blue', folium_map=None):
    polylines = []
    lat = []
    long = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten the polygons 
        outline = [loop for polygon in polygons for loop in polygon]
        # append the first point to the end to close the polygon
        polyline = [outline + [outline[0]] for outline in outline] [0]
        lat.extend(map(lambda x: x[0], polyline))
        long.extend(map(lambda x: x[1], polyline))
        polylines.append(polyline)
    if folium_map is None:
        folium_map = folium.Map(location=[sum(lat)/len(lat), sum(long)/len(long)], zoom_start=3)
    else:
        folium_map = folium_map
    for polyline in polylines:
        folium_map.add_child(folium.PolyLine(locations=polyline, color=color))
    return folium_map