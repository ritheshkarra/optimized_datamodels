import pandas as pd
from pandas.io.json import json_normalize
import warnings

warnings.filterwarnings('ignore')
import math
# from geo_api import *
from app.models.genericmodels.geo_api import *


class NearByPlaces:
    # lat = '0.0'
    # lng = '0.0'
    # radius = '5'
    # global cong

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    # self.radius = radius


    def nearby(self, rad, keyword):
        c = geoAPI()
        pois = c.pois(self.lat, self.lng, radius=rad, keyword=keyword)
        # embed()
        print("-------", keyword)
        n = json_normalize(pois['result'], 'results')[['name', 'opening_hours', 'rating', 'vicinity', 'geometry']]
        l = json_normalize(n['geometry'])[['location.lat', 'location.lng']]
        l['new'] = 'rr'
        js = {}
        for i in range(0, len(l)):
            l['new'][i] = str(l['location.lat'][i]) + "," + str(l['location.lng'][i])
        source = self.lat + "," + self.lng
        for i in range(0, len(l)):
            js[i] = c.get_route(source, l['new'][i], "fastest,car")
        n['text'] = 'tt'
        n['distance'] = 'd'
        n['travelTime'] = 'tt'
        n['route'] = 'r'
        n['keyword'] = keyword
        for i in range(len(n)):
            n['text'][i] = js[i]['result']['response']['route'][0]['summary']['text']
            n['distance'][i] = js[i]['result']['response']['route'][0]['summary']['distance']
            n['travelTime'][i] = js[i]['result']['response']['route'][0]['summary']['travelTime']
            n['route'][i] = js[i]['result']['response']['route'][0]['leg'][0]['maneuver']
        print(n)
        return n

    '''def nearby_map(self,result):
        c = geoAPI()
        l = json_normalize(result['geometry'])[['location.lat','location.lng']]
        l_list = l.values.tolist()
        p_list = result['text'].values.tolist()
        k_list = result['keyword'].values.tolist()
        dd_list = result[['name','distance','travelTime']].values.tolist()
        SF_COORDINATES = (float(self.lat),float(self.lng))
        blr = folium.Map(location=SF_COORDINATES, zoom_start=16,control_scale=True)
        marker_cluster = folium.MarkerCluster("Emergency cluster").add_to(blr)

        #Marker Cluster
        for each,p,k in zip(l_list,dd_list,k_list):
            if k == 'hospital':
                folium.Marker(each,popup=p[0]+',distance = '+str(p[1])+"meters, travel time = "+str(math.ceil(p[2]/60))+"mins",icon=folium.Icon(color='green',icon='plus-sign')).add_to(marker_cluster)
            else:
                folium.Marker(each,popup=p[0]+',distance = '+str(p[1])+"meters, travel time = "+str(math.ceil(p[2]/60))+"mins",icon=folium.Icon(color='blue',icon='hdd')).add_to(marker_cluster)

        folium.Marker([float(self.lat),float(self.lng)], popup='incident point',icon=folium.Icon(color='red',icon='warning-sign')).add_to(blr)
        #folium.Marker([12.974493,77.7309553], popup="incident point",icon=folium.Icon(color='red',icon='info-sign')).add_to(blr)

        #Polyline
        for index,row in result.iterrows():
            print(row['route'])
            dic = json_normalize(row['route'])
            a = dic[['position.latitude','position.longitude']].values.tolist()
            folium.PolyLine(a, color="red", weight=2.5, opacity=1).add_to(blr)
        #return display(blr)
        return blr'''

    def nearby_traffic(self):
        c = geoAPI()
        # tf = c.traffic_flow(float(self.lat), float(self.lng), self.radius)
        tf = c.traffic_flow(float(self.lat), float(self.lng))
        rws_list = tf['result']['RWS']
        final_list = []
        for rws in rws_list:
            for rw in rws['RW']:
                fis = rw['FIS']
                for fi in fis:
                    for fin in fi['FI']:
                        tmc_obj = fin
                        for last_iter in tmc_obj['CF']:
                            last_iter['DE'] = tmc_obj['TMC']['DE']
                            last_iter['FIS_DE'] = rw['DE']
                            final_list.append(last_iter)
        b = final_list
        congestion = pd.DataFrame(b)[['DE', 'JF']]
        # print(congestion.values.tolist())
        return congestion.values.tolist()

    '''def nearby_map(self, result):

        l = json_normalize(result['geometry'])[['location.lat', 'location.lng']]
        l_list = l.values.tolist()
        p_list = result['text'].values.tolist()
        k_list = result['keyword'].values.tolist()
        dd_list = result[['name', 'distance', 'travelTime']].values.tolist()
        SF_COORDINATES = (float(self.lat), float(self.lng))
        blr = folium.Map(location=SF_COORDINATES, tiles='Cartodb dark_matter', attr='osm', zoom_start=16,
                         control_scale=True)
        # congestion list
        # cong_table = cong()
        html = """
				<html>
				<body>
					<h2>Traffic Level in surrounding Roads</h2>
					<table>
						{0}
					</table>
				</body>
				</html>"""

        items = self.cong()
        tr = "<tr>{0}</tr>"
        td = "<td>{0}</td>"
        subitems = [tr.format(''.join([td.format(a) for a in item])) for item in items]
        html1 = html.format("".join(subitems))  # or write, whichever
        te = folium.Html(html1, script=True)

        # iframe = folium.element.IFrame(html=html, width=450, height=200)

        popup = folium.Popup(te, max_width=2650)
        distance = []
        for each, p, k in zip(l_list, dd_list, k_list):
            distance = distance + [math.ceil(p[2] / 60)]
        distance.sort()
        # print(distance)
        # Marker Cluster
        for each, p, k in zip(l_list, dd_list, k_list):
            if k == 'police station':
                travelTime = math.ceil(p[2] / 60)
                if (travelTime == distance[0]):
                    folium.Marker(each, popup=p[0] + ',distance = ' + str(p[1]) + "meters, travel time = " + str(
                        math.ceil(p[2] / 60)) + "mins", icon=folium.Icon(color='green', icon='plus-sign')).add_to(blr)
                else:
                    folium.Marker(each, popup=p[0] + ',distance = ' + str(p[1]) + "meters, travel time = " + str(
                        math.ceil(p[2] / 60)) + "mins", icon=folium.Icon(color='blue	', icon='plus-sign')).add_to(
                        blr)
                # else:
                #		folium.Marker(each,popup=p[0]+',distance = '+str(p[1])+"meters, travel time = "+str(math.ceil(p[2]/60))+"mins",icon=folium.Icon(color='blue',icon='hdd')).add_to(blr)
        folium.Marker([float(self.lat), float(self.lng)], popup=popup,
                      icon=folium.Icon(color='red', icon='warning-sign')).add_to(blr)
        return blr '''

    def cong(self):
        c = geoAPI()
        tf = c.traffic_flow(float(self.lat), float(self.lng), 20)
        rws_list = tf['result']['RWS']
        final_list = []
        for rws in rws_list:
            for rw in rws['RW']:
                fis = rw['FIS']
                for fi in fis:
                    for fin in fi['FI']:
                        tmc_obj = fin
                        for last_iter in tmc_obj['CF']:
                            last_iter['DE'] = tmc_obj['TMC']['DE']
                            last_iter['FIS_DE'] = rw['DE']
                            final_list.append(last_iter)
        b = final_list
        # print(json.dumps(rws_list, indent=2))
        congestion = pd.DataFrame(b)[['DE', 'JF']]
        # congestion =  congestion.sort(['DE', 'JF'], ascending=[True, True])
        congestion = congestion.sort_values(['JF'], ascending=[True])
        # print congestion
        intensity_names = ['low', 'medium', 'high']

        congestion['intensity'] = pd.cut(congestion['JF'], bins=[0, 5, 7.5, 10], labels=intensity_names, right=False)

        return congestion[['DE', 'intensity']].values.tolist()


def main():
    lat = '17.450954'
    lng = '78.380411'
    myArea = NearByPlaces(lat, lng)
    result1 = myArea.nearby(rad='500', keyword='police station')
    result2 = myArea.nearby(rad='500', keyword='hospital')
    result = pd.concat([result1, result2], ignore_index=True)
    print(result[0:10])

    myArea.nearby_map(result)


# myArea.nearby_traffic()


if __name__ == "__main__":
    main()
