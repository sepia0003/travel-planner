import requests
import polyline
import folium

loc_pick = [139.700621, 35.658341]
loc_del = [139.745747, 35.659034]
query_url = "http://localhost:5000/route/v1/driving/139.700621,35.658341;139.745747,35.659034"
# query_url = "http://localhost:5000/route/v1/driving/{},{};{},{}?steps=true".format(loc_pick[0], loc_pick[1], loc_del[0], loc_del[1])
response = requests.get(query_url)
result = response.json() #.json() 메소드는 response 객체가 json일때 이를 딕셔너리로 변환

# routes_dict = result["routes"][0] "routes"에 해당하는 밸류가 리스트이기에 0으로 접근
geometry = result["routes"][0]["geometry"]
travel = polyline.decode(geometry) # 튜플짝의 원소로이루어진 리스트1개
start_point = [result["waypoints"][0]["location"][0] , result["waypoints"][0]["location"][1]]
end_point = [result["waypoints"][1]["location"][0] , result["waypoints"][1]["location"][1]]
start_point.reverse() # 반환해주는 순서가 귀찮게 경도,위도 순서라 뒤바꿔줘야함 
end_point.reverse()
# 리스트안에 인덱스0으로서 딕셔너리가, 인덱스1로서 딕셔너리가 각각들어가있으므로 리스트[인덱스]로 각딕셔너리에 접근
# 리스트 슬라이싱 리스트[::] 는 슬라이싱한 새로운리스트를 반환한다. 기존리스트를 변경하는게 아님

map = folium.Map(location=[(start_point[0] + end_point[0])/2 , (start_point[1] + end_point[1])/2], zoom_start=13)
folium.PolyLine(travel, weight=8, color='blue', opacity=0.6).add_to(map)
folium.Marker(location=start_point, icon=folium.Icon(icon='play', color='green')).add_to(map)
folium.Marker(location=end_point, icon=folium.Icon(icon='stop', color='red')).add_to(map)
# folium은 location값을 기본적으로 리스트로 준다.
map.save('testmap.html')

# folium_map = folium.Map(location=loc_mid[::-1], zoom_start=14)
# folium.Marker(location=loc_pick[::-1], icon=folium.Icon(color='red')).add_to(folium_map)
# folium.Marker(location=loc_del[::-1]).add_to(folium_map)
# line = folium.vector_layers.PolyLine(locations=list_locations, color='black', weight=10)
# line.add_to(folium_map)
# folium_map.save("map.html")