import requests

loc_pick = [139.700621, 35.658341]
loc_del = [139.745747, 35.659034]
query_url = "http://192.168.0.150:5000/route/v1/driving/{},{};{},{}?steps=true".format(loc_pick[0], loc_pick[1], loc_del[0], loc_del[1])
response = requests.get(query_url)

result = response.json()
route = result["routes"][0]
legs = route["legs"][0]["steps"]
list_locations = []
for point in legs:
    for it in point["intersections"]:
        list_locations.append(it["location"][::-1])


loc_mid = list_locations.copy()

import folium

folium_map = folium.Map(location=loc_mid[::-1], zoom_start=14)
folium.Marker(location=loc_pick[::-1], icon=folium.Icon(color='red')).add_to(folium_map)
folium.Marker(location=loc_del[::-1]).add_to(folium_map)
line = folium.vector_layers.PolyLine(locations=list_locations, color='black', weight=10)
line.add_to(folium_map)
folium_map.save("map.html")