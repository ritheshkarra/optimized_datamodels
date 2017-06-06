import pandas as pd
from pandas.io.json import json_normalize
import requests
import datetime
import json
import warnings
import folium
import math

warnings.filterwarnings('ignore')

class CrisisManagement:

    def nearby(self,s_lat, s_lng, radius, keyword):
        link = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + s_lat + "," + s_lng + '&radius=' + radius + '&type=' + keyword + '&key=AIzaSyC6zF5CWGqw9Mha4aUrEzFsSYw5n3I3raM'
        pois = requests.get(link).json()
        n = json_normalize(pois['results'])[['name', 'geometry.location.lat', 'geometry.location.lng']]
        js = {}
        l = n[['geometry.location.lat', 'geometry.location.lng']].values.tolist()
        source = s_lat + "," + s_lng
        for i in range(0, len(l)):
            js[i] = self.calc_route(source, str(l[i][0]) + "," + str(l[i][1]), "fastest;car")
        n['text'] = 'tt'
        n['distance'] = 'd'
        n['travelTime'] = 'tt'
        n['route'] = 'r'
        n['keyword'] = keyword
        for i in range(len(n)):
            n['text'][i] = js[i]['response']['route'][0]['summary']['text']
            n['distance'][i] = js[i]['response']['route'][0]['summary']['distance']
            n['travelTime'][i] = js[i]['response']['route'][0]['summary']['travelTime']
            n['route'][i] = js[i]['response']['route'][0]['leg'][0]['maneuver']
        return n

    def cong_source(self,lat, lng, radius):
        tf1 = requests.get("https://traffic.cit.api.here.com/traffic/6.1/flow.json?prox=" + lat + "%2C" + lng + "%2C" + str(radius) + "&responseattributes=sh%2Cfc&app_id=ONe0616Q1jK0RLmeN7fc&app_code=bWQ6Eir1V2KRjaS-5oMOcw")
        tf_df = self.create_data_1(tf1.json())
        congestion = tf_df[['DE', 'SHP', 'JF']]
        intensity_names = ['low', 'medium', 'high']
        congestion['intensity'] = pd.cut(congestion['JF'], bins=[0, 5, 7.5, 10], labels=intensity_names, right=False)
        return congestion

    def create_data_1(self,dictionary):
        RWS = dictionary['RWS']
        l = []
        for rw in RWS:
            EBU_COUNTRY_CODE = rw['EBU_COUNTRY_CODE']
            EXTENDED_COUNTRY_CODE = rw['EXTENDED_COUNTRY_CODE']
            UNITS = rw['UNITS']
            for elem in rw['RW']:
                DE = elem['DE']
                LI = elem['LI']
                PBT = elem['PBT']
                mid = elem['mid']
                FIS = elem['FIS']
                for FI in FIS:
                    elem_1 = FI['FI']
                    for elem_2 in elem_1:
                        LE = elem_2['TMC']['LE']
                        PC = elem_2['TMC']['PC']
                        QD = elem_2['TMC']['QD']
                        SHP = elem_2['SHP']
                        CF = elem_2['CF']
                        for elem_3 in CF:
                            FF = elem_3['FF']
                            CN = elem_3['CN']
                            JF = elem_3['JF']
                            SP = elem_3['SP']
                            SU = elem_3['SU']
                            TY = elem_3['TY']
                            l.append([EBU_COUNTRY_CODE, EXTENDED_COUNTRY_CODE, UNITS, DE, LI, PBT, mid, LE, PC, QD, SHP, FF, CN,JF, SP, SU, TY])
        clms = ['EBU_COUNTRY_CODE', 'EXTENDED_COUNTRY_CODE', 'UNITS', 'DE', 'LI', 'PBT', 'mid', 'LE', 'PC', 'QD', 'SHP','FF', 'CN', 'JF', 'SP', 'SU', 'TY']
        df = pd.DataFrame(l, columns=clms)
        df['PBT'] = datetime.datetime.now()
        return df


    def calc_route(self, source, destination, car_type):
        link = "https://route.cit.api.here.com/routing/7.2/calculateroute.json?waypoint0=" + source + "&waypoint1=" + destination + "&mode=" + car_type + "%3Btraffic%3Aenabled&app_id=ONe0616Q1jK0RLmeN7fc&app_code=bWQ6Eir1V2KRjaS-5oMOcw&departure=now"
        return requests.get(link).json()


    def nearby_map(self,result, lat, lng):
        l_list = result[['geometry.location.lat', 'geometry.location.lng']].values.tolist()
        p_list = result['text'].values.tolist()
        k_list = result['keyword'].values.tolist()
        dd_list = result[['name','distance','travelTime']].values.tolist()
        SF_COORDINATES = (float(lat),float(lng))
        blr = folium.Map(location=SF_COORDINATES,tiles='Cartodb dark_matter', attr='osm', zoom_start=16,control_scale=True)

        html = """<html>
                    <body>
                        <h2>Traffic Level in surrounding Roads</h2>
                        <table>
                            {0}
                        </table>
                    </body>
                </html>"""

        items = self.cong_source(lat, lng, 200)
        tr = "<tr>{0}</tr>"
        td = "<td>{0}</td>"
        subitems = [tr.format(''.join([td.format(a) for a in item])) for item in items]
        html1 = html.format("".join(subitems))
        te = folium.Html(html1, script=True)
        popup = folium.Popup(te, max_width=2650)
        distance = []
        for each, p, k in zip(l_list, dd_list, k_list):
            distance = distance + [math.ceil(p[2] / 60)]
        distance.sort()
        marker_cluster = folium.MarkerCluster("Emergency cluster").add_to(blr)

        #Marker Cluster
        for each,p,k in zip(l_list,dd_list,k_list):
            if k == 'hospital':
                folium.Marker(each,popup=p[0]+',distance = '+str(p[1])+"meters, travel time = "+str(math.ceil(p[2]/60))+"mins",icon=folium.Icon(color='green',icon='plus-sign')).add_to(marker_cluster)
            else:
                folium.Marker(each,popup=p[0]+',distance = '+str(p[1])+"meters, travel time = "+str(math.ceil(p[2]/60))+"mins",icon=folium.Icon(color='blue',icon='hdd')).add_to(marker_cluster)

        folium.Marker([float(lat),float(lng)], popup='incident point',icon=folium.Icon(color='red',icon='warning-sign')).add_to(blr)

        #Polyline
        for index,row in result.iterrows():
            print(row['route'])
            dic = json_normalize(row['route'])
            a = dic[['position.latitude','position.longitude']].values.tolist()
            folium.PolyLine(a, color="red", weight=2.5, opacity=1).add_to(blr)
        #blr.save('/home/raghuram/Documents/RaghuProjects/datamodels/map1.html')
        return blr

def main():
    cm = CrisisManagement()
    df_police = cm.nearby('17.450954', '78.380411', radius='1500', keyword='police')
    df_hospital = cm.nearby('17.450954', '78.380411', radius='500', keyword='hospital')
    result = pd.concat([df_police, df_hospital], ignore_index=True)
    # radius in meters
    tf = cm.cong_source('17.450954', '78.380411', 200)
    print(tf.to_json(orient='records'))
    print("-----------------------------")
    print(result.to_json(orient='records'))

    print("-----------------------------*********************")
    cm.nearby_map(result,'17.450954', '78.380411')

if __name__ == "__main__":
    main()