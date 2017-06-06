import requests
import pandas as pd
from pandas.io.json import json_normalize
import json
import folium
import time
from app.models.wastemanagement.cdp_config import *

# API keys used
here_appid = 'UqaMihQzIQUR2E5FHMMo'
here_appcode = 'jV_DMt-iBrRWWRecw3uyZQ'
grass_key = '21833ce2-effd-4b69-979e-60a7b9d6d112'
link = "https://graphhopper.com/api/1/vrp/optimize?key=" + grass_key

class wasteCollectionRoute:
    # input data from file, vehicle information,depot location, landfill location etc
    def dataVehicles(self,vehicle_file):
        vehicle_df = pd.read_csv(vehicle_file)
        # print(vehicle_df.head())
        vehicle_json = {}
        vehicle_type = {}
        for index, row in vehicle_df.iterrows():
            vehicle = {}
            vehicle['vehicle_id'] = row['vehicle_id']
            nested1 = {}
            nested1['location_id'] = "start" + str(index)
            nested1['lon'] = row['start_lng']
            nested1['lat'] = row['start_lat']
            vehicle['start_address'] = nested1
            nested2 = {}
            nested2['location_id'] = 'deliver' + str(index)
            nested2['lon'] = row['end_lng']
            nested2['lat'] = row['end_lat']
            vehicle['end_address'] = nested2
            vehicle['type_id'] = "vehicle_type" + str(index)
            # incase we have start time
            if row['earliest_start'] != -1:
                vehicle['earliest_start'] = row['earliest_start']
            if row['latest_end'] != -1:
                vehicle['latest_end'] = row['latest_end']
            # maximum distance each vehicle can travel in a day
            if row['max_distance'] != -1:
                vehicle['max_distance'] = row['max_distance']
            # if there is a break in between service
            if row['break'] != -1:
                nested3 = {}
                nested3['duration'] = row['duration']
                vehicle['break'] = nested3
            key = "vehicles"
            vehicle_json.setdefault(key, [])
            vehicle_json[key].append(vehicle)

            vtype = {}
            vtype['type_id'] = 'vehicle_type' + str(index)
            vtype['profile'] = "truck"
            vtype['capacity'] = [row['capacity']]
            vtype['speed_factor'] = self.speedFactor(row['start_lat'], row['start_lng'])
            key = "vehicle_types"
            vehicle_type.setdefault(key, [])
            vehicle_type[key].append(vtype)
            vehicle_json['vehicle_types'] = vehicle_type['vehicle_types']
        return vehicle_json

    # data of all the pickup points
    def dataPickups(self,pickup_file, threshold):
        df = pd.read_csv(pickup_file)
        df_fill = df[df['fill'] > threshold]

        pickup_json = {}
        i = 1
        for index, row in df_fill.iterrows():
            data = {}
            nest = {}
            data['id'] = "service" + str(i)
            data['name'] = "name" + str(i)
            data['size'] = [row['size']]
            nest['location_id'] = "pickup" + str(i)
            nest['name'] = row['PROPERTY_ADDRESS']
            nest['lon'] = row['lng']
            nest['lat'] = row['lat']
            data['address'] = nest
            # duration spent at each pickup point
            if row['duration'] != -1:
                data['duration'] = row['duration']
            # if any pickup point has a time window
            if row['time_windows'] != -1:
                nest2 = {}
                nest2['earliest'] = int(row['earliest'])
                nest2['latest'] = int(row['latest'])
                nest3 = {}
                key = "time_windows"
                nest3.setdefault(key, [])
                nest3[key].append(nest2)
                data['time_windows'] = nest3['time_windows']
            i = i + 1
            key = "services"
            pickup_json.setdefault(key, [])
            pickup_json[key].append(data)
        # v['services'] = a['services']
        return pickup_json

    # Public Interface
    def dataProcessingFromSampleFiles(self,vehicle_file, pickup_file, pickupReadinessThreshold):
        input_json = {}
        input_json = self.dataVehicles(vehicle_file)
        pickups = self.dataPickups(pickup_file, pickupReadinessThreshold)
        input_json['services'] = pickups['services']
        input_json["configuration"] = {"routing": {"calc_points": True}}
        return input_json

    def dataProcessingFromParameter(self,pickups, vehicle, threshold):
        # when CDP data is in place
        # for item in pickups:
        df_pickup = pd.DataFrame()
        lat, lng, fill, duration, time_window, size, add = [], [], [], [], [], [], []
        for item in pickups:
            lat.append(item[0])
            lng.append(item[1])
            fill.append(item[2])
            duration.append(300)
            time_window.append(-1)
            size.append(1)
            add.append("Granada")
        df_pickup['PROPERTY_ADDRESS'] = add
        df_pickup['lat'] = lat
        df_pickup['lng'] = lng
        df_pickup['fill'] = fill
        df_pickup['duration'] = duration
        df_pickup['time_windows'] = time_window
        df_pickup['size'] = size
        df_pickup.to_csv("pickup_parameter.csv")

        df_vehicles = pd.DataFrame()
        s_lat, s_lng, e_lat, e_lng, capacity, vid = [], [], [], [], [], []
        i = 1
        for v in vehicle:
            s_lat.append(v[0])
            s_lng.append(v[1])
            e_lat.append(v[2])
            e_lng.append(v[3])
            vid.append("vehicle" + str(i))
            capacity.append(v[4])
            i = i + 1
        df_vehicles['vehicle_id'] = vid
        df_vehicles['start_lat'] = s_lat
        df_vehicles['start_lng'] = s_lng
        df_vehicles['end_lat'] = e_lat
        df_vehicles['end_lng'] = e_lng
        df_vehicles['capacity'] = capacity
        df_vehicles['earliest_start'] = -1
        df_vehicles['latest_end'] = -1
        df_vehicles['max_distance'] = -1
        df_vehicles['break'] = -1
        df_vehicles.to_csv("vehicles_parameter.csv")
        input_json = self.dataProcessingFromSampleFiles("vehicles_parameter.csv", "pickup_parameter.csv", threshold)
        return input_json

    def dataProcessingFromCDP(self):

        sayme = get_sayme()
        df_sayme = json_normalize(sayme['Find']['Result'])[['UltrasonicSensor.deviceState.batteryPercentage',
                                                            'UltrasonicSensor.geocoordinates.latitude',
                                                            'UltrasonicSensor.geocoordinates.longitude',
                                                            'WasteBin.lastCollected', 'WasteBin.sid',
                                                            'WasteBin.state.fillLevel.value', 'WasteBin.status',
                                                            'WasteBin.temperature.value']]
        df_sayme.rename(columns={'UltrasonicSensor.deviceState.batteryPercentage': 'battery_percentage',
                                 'UltrasonicSensor.geocoordinates.latitude': 'lat',
                                 'UltrasonicSensor.geocoordinates.longitude': 'lng',
                                 'WasteBin.lastCollected': 'lastcollected',
                                 'WasteBin.sid': 'sid', 'WasteBin.state.fillLevel.value': 'fill',
                                 'WasteBin.status': 'status', 'WasteBin.temperature.value': 'temperature'},
                        inplace=True)
        wellness = get_wellness()
        df_wellness = json_normalize(wellness['Find']['Result'])[['UltrasonicSensor.deviceState.batteryPercentage',
                                                                  'UltrasonicSensor.geocoordinates.latitude',
                                                                  'UltrasonicSensor.geocoordinates.longitude',
                                                                  'WasteBin.lastCollected', 'WasteBin.sid',
                                                                  'WasteBin.state.fillLevel.value', 'WasteBin.status',
                                                                  'WasteBin.temperature.value']]
        df_wellness.rename(columns={'UltrasonicSensor.deviceState.batteryPercentage': 'battery_percentage',
                                    'UltrasonicSensor.geocoordinates.latitude': 'lat',
                                    'UltrasonicSensor.geocoordinates.longitude': 'lng',
                                    'WasteBin.lastCollected': 'lastcollected',
                                    'WasteBin.sid': 'sid', 'WasteBin.state.fillLevel.value': 'fill',
                                    'WasteBin.status': 'status', 'WasteBin.temperature.value': 'temperature'},
                           inplace=True)
        df_all = pd.concat([df_sayme, df_wellness], ignore_index=True)
        df_all['duration'] = 300
        df_all['time_windows'] = -1
        df_all['size'] = 1
        df_all['PROPERTY_ADDRESS'] = "Granada"
        df_all.to_csv("CDP_pickups.csv")

        vehicle = [[37.1811867, -3.6050833, 37.16742, -3.6052387, 50],
                   [37.1811867, -3.6050833, 37.16742, -3.6052387, 50]]
        df_vehicles = pd.DataFrame()
        s_lat, s_lng, e_lat, e_lng, capacity, vid = [], [], [], [], [], []
        i = 1
        for v in vehicle:
            s_lat.append(v[0])
            s_lng.append(v[1])
            e_lat.append(v[2])
            e_lng.append(v[3])
            vid.append("vehicle" + str(i))
            capacity.append(v[4])
            i = i + 1
        df_vehicles['vehicle_id'] = vid
        df_vehicles['start_lat'] = s_lat
        df_vehicles['start_lng'] = s_lng
        df_vehicles['end_lat'] = e_lat
        df_vehicles['end_lng'] = e_lng
        df_vehicles['capacity'] = capacity
        df_vehicles['earliest_start'] = -1
        df_vehicles['latest_end'] = -1
        df_vehicles['max_distance'] = -1
        df_vehicles['break'] = -1
        df_vehicles.to_csv("CDP_vehicles.csv")
        input_json = self.dataProcessingFromSampleFiles("CDP_vehicles.csv", "CDP_pickups.csv", 75)
        return input_json

    # taking traffic data around the depot and mappingit to speed_factor
    def speedFactor(self,lat, lng):
        # radius 5 kms
        link_1 = 'https://traffic.cit.api.here.com/traffic/6.1/flow.json?prox=' + str(lat) + '%2C' + str(
            lng) + '%2C5000&app_id=' + here_appid + '&app_code=' + here_appcode
        try:
            tf = requests.get(link_1).json()
            rws_list = tf['RWS']
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
            congestion = congestion.sort('JF')
            # congestion = congestion['DE'].unique()
            # congestion.drop_duplicates('DE',inplace=True)
            # intensity_names = ['low','medium','high']
            # congestion['intensity'] = pd.cut(congestion['JF'],bins=[0,5,7.5,10],labels=intensity_names,right=False)
            # congestion[['DE','intensity']].values.tolist()
            t_mean = congestion['JF'].mean()
            # print(congestion)
            if t_mean >= 0 and t_mean < 5:
                return 1.0
            elif t_mean >= 5 and t_mean < 7.5:
                return 0.8
            else:
                return .6
        except Exception as x:
            print(x)
            return 1.0
            # tf.json()

    # API call and parsing the output json
    def model(self,input_json):
        try:
            headers = {"Content-Type": "application/json"}
            result = requests.post(link, data=json.dumps(input_json), headers=headers)
            # print(result.json())
            job_id = result.json()['job_id']
            while True:
                sol = requests.get("https://graphhopper.com/api/1/vrp/solution/" + job_id + "?key=" + grass_key)
                if sol.json()['status'] != 'processing':
                    break
                time.sleep(.5)
            # print(sol.json())
            return sol.json()
        except Exception as x:
            print(x)

    # Test function
    def testRouter(self):
        # input_json = dataProcessingFromSampleFiles("ferrovial_vehicle.csv","ferrovial_pickups.csv",75)
        # raw output json
        # input_json = dataProcessingFromParameter([[37.193710,-3.604993,60.0],[37.191051,-3.630041,75],[37.191255,-3.619984,70],[37.199898,-3.619984,68],[37.183502,-3.614848,90]]
        # ,[[37.1811867,-3.6050833,37.16742,-3.6052387,5],[37.1811867,-3.6050833,37.16742,-3.6052387,5]],50)
        input_json = self.dataProcessingFromCDP()
        result_json = self.model(input_json)
        self.visualization(result_json)
        # print(result_json)
        # print(json.dumps(input_json))
        # dataProcessingFromCDP()

    # return the summary and indivisual vehicle's information
    def visualization(self,result_json):
        print("Total distance Travelled: {} kms ".format(result_json['solution']['distance'] / 1000))
        print("Total time taken: {} mins ".format(result_json['solution']['completion_time'] / 60))
        print("Number of bins unassigned : {} ".format(result_json['solution']['no_unassigned']))

        # url_here_list = []
        for i in range(result_json['solution']['no_vehicles']):
            location_df = json_normalize(result_json['solution']['routes'][i]['activities'])
            print("Vehile {} data:".format(i + 1))
            print(location_df)

            #        location_list = location_df[['address.lat','address.lon']].values.tolist()
            #
            #        url_here = ""
            #        for l in location_list:
            #            url_here += str(l[0]) + "," + str(l[1]) + ","
            #        url_here_list.append(url_here)
            #    print(url_here_list)
            # img = requests.get("https://image.maps.cit.api.here.com/mia/1.6/route?r0=52.5338%2C13.2966%2C52.538361%2C13.325329&r1=52.540867%2C13.262444%2C52.536691%2C13.264561%2C52.529172%2C13.268337%2C52.528337%2C13.273144%2C52.52583%2C13.27898%2C52.518728%2C13.279667&m0=52.5338%2C13.2966%2C52.538361%2C13.325329&m1=52.540867%2C13.262444%2C52.518728%2C13.279667&lc0=00ff00&sc0=000000&lw0=6&lc1=ff0000&sc1=0000ff&lw1=3&w=500&app_id=DemoAppId01082013GAL&app_code=AJKnXv84fjrb0KIHawS0Tg")

    def rev(self,g_list):
        new_list = []
        if (any(isinstance(i, list) for i in g_list)):
            for l in g_list:
                newlist = l[::-1]
                new_list.append(newlist)

        else:
            new_list = [g_list[::-1]]

        return new_list

def main():
    waste = wasteCollectionRoute()
    waste.testRouter()

if __name__ == "__main__":
        main()
