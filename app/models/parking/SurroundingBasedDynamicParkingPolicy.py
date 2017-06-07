# !/usr/bin/python
import pandas as pd
import numpy as np
import os,sys,ast,requests
from math import radians, cos, sin, asin, sqrt
import json
import falcon
import requests
import psycopg2
from server.logs import logger
#from IPython.display import display,HTML
os.environ['TZ'] = 'Asia/Kolkata'

class DynamicParking:

    def getDBConnection(self, psqlhost, databaseName, userName, password):
     try:
        logger.info("Establishing connnection to Postgres")
        psqlConnection = psycopg2.connect(host=psqlhost, dbname=databaseName, user=userName, password=password)
        marker = psqlConnection.cursor();
        return marker
     except Exception as e:
        logger.error("Error in creating connection to DataBase. {}".format(e))

    def get_geo_parking(self,spaceId):
      try:
        logger.info("Executing get_geo_parking function")
        import requests
        data_1 = json.dumps({
            "Query": {
                "Find": {
                    "ParkingSpace": {
                        "sid": {
                            "eq": spaceId
                        }
                    }
                }
            }
        })
        # Real time api for parking
        link = 'https://cdp-jaipur.cisco.com/deveng/fid-CIMQueryInterface?SensorCustomerKey=500001&AppKey=CDP-App&UserKey=500060'
        headers = {'Content-type': 'application/json', 'body': 'raw'}
        try:
           parking_real_time = requests.post(link, data=data_1)
           # print(parking_real_time.status_code)
           data = parking_real_time.json()
        except Exception as e:
           logger.error("API request failed. {}".format(e))
        li = []
        colms = ['sid', 'levelLabel', 'operatedBy', 'label', 'occupied', 'total', 'sensorCustomerId', 'hierId',
                 'siblingIndex' \
            , 'provider', 'providerId', 'geo_pts', 'maxDurationMinutes', 'parkingRate_durationMinutes' \
            , 'parkingRate_farePerMinute', 'zoneType']
        li.append(colms)
        if data['Find']['Status'] == "NoResult":
          logger.info("Data or spaceId is not available")
          raise Exception("Data or spaceId is not available. {}".format(e)) 
        else:
          for item in data['Find']['Result']:
            elem = item['ParkingSpace']
            sid = elem['sid']
            try:
                levelLabel = elem['levelLabel']
            except:
                levelLabel = np.nan
            try:
                operatedBy = elem['operatedBy']
            except:
                operatedBy = np.nan
            label = elem['label']
            occupied = elem['state']['occupied']
            total = elem['state']['total']
            sensorCustomerId = elem['sensorCustomerId']
            hierId = elem['hierId']
            try:
                siblingIndex = elem['siblingIndex']
            except:
                siblingIndex = np.nan
            provider = elem['providerDetails']['provider']
            providerId = elem['providerDetails']['providerId']
            geo_pt = elem['boundary']
            try:
                maxDurationMinutes = elem['opParams']['maxDurationMinutes']
                parkingRate_durationMinutes = elem['opParams']['parkingRate']['durationMinutes']
                parkingRate_farePerMinute = elem['opParams']['parkingRate']['farePerMinute']
                zoneType = elem['opParams']['zoneType']
            except:
                maxDurationMinutes = np.nan
                parkingRate_durationMinutes = np.nan
                parkingRate_farePerMinute = np.nan
                zoneType = np.nan
            geo_pts = []
            for elem_1 in geo_pt['geoPoint']:
                geo_pts.append([elem_1['latitude'], elem_1['longitude']])
            li.append(
                [sid, levelLabel, operatedBy, label, occupied, total, sensorCustomerId, hierId, siblingIndex, provider,
                 providerId \
                    , geo_pts, maxDurationMinutes, parkingRate_durationMinutes, parkingRate_farePerMinute, zoneType])

          data_df = pd.DataFrame(li[1:], columns=li[0])
          return data_df
      except Exception as e:
        logger.error("geo_parking function failed with errors. {}".format(e))

    ### 2. a parking will be more important if aggregated score of a pois with smaller distance with high rating ; is high
    ## Google maps based approach
    def haversine(self,pt1, pt2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        lat1 = pt1[0]
        lon1 = pt1[1]
        lat2 = pt2[0]
        lon2 = pt2[1]
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6367 * c
        return km

    # getting important params from  google places api
    def get_reviews(self,sen_pts,categ,radius,label='mean_position'):
      try:
        logger.info("Getting parking reviews for geo points with in the radius")
        poi_pos = {}
        for i in range(sen_pts.shape[0]):
            poi_pos_1 = {}
            for cat in categ:
                pt = sen_pts.iloc[i][label]
                key=['AIzaSyCS-RjgQk-XsuyTiaRTh040D9iibCsW9zQ','AIzaSyDoZZaxE3da9nD2U2GzC3xs1FWDywWkOiI','AIzaSyC6zF5CWGqw9Mha4aUrEzFsSYw5n3I3raM']
                key_i=0
                while True:
                    link='https://maps.googleapis.com/maps/api/place/search/json?location='+str(pt[0])+','+str(pt[1])+'&radius='+str(radius)+'&type='+cat+'&key='+key[key_i]
                    #link = 'https://maps.googleapis.com/maps/api/place/search/json?location=' + str(pt[0]) + ',' + str(
                    #pt[1]) + '&radius='+str(radius)+'&type=' + cat + '&key=AIzaSyC6zF5CWGqw9Mha4aUrEzFsSYw5n3I3raM'
                    try:
                       r = requests.get(link)
                       if r.json()['status']=='OVER_QUERY_LIMIT':
                         if key_i == 2:
                            key_i=0
                         else:
                            key_i+=1
                       else:
                            break
                    except Exception as e:
                       logger.error("Failed to contact google maps. {}".format(e))
                jsn = r.json()['results']
                li = []
                for poi in jsn:
                  try:
                     is_open = poi['opening_hours']['open_now']
                  except:
                     is_open = True
                  types = poi['types']
                  loc = [poi['geometry']['location']['lat'], poi['geometry']['location']['lng']]
                  name=poi['name']
                  try:
                    rating = poi['rating']
                  except:
                    rating = np.nan
                  dist = self.haversine(pt, loc)
                  li.append([name,is_open, types, loc, rating, dist])
                poi_pos_1[cat] = pd.DataFrame(li, columns=['name','is_open', 'types', 'loc', 'rating', 'dist(km)'])
            poi_pos[sen_pts.index[i]] = poi_pos_1
        return poi_pos
      except Exception as e:
        logger.error("Failed to get review for parking. {}".format(e))

    # combining  results to get single index
    #Categories to invest in

    def get_rating(self,sen_pts, categ,radius):
     try:
        logger.info("Finding parking rate for categories")
        poi_pos = self.get_reviews(sen_pts,categ,radius)
        net_res = {}
        for key in poi_pos.keys():
            temp = poi_pos[key]
            res_temp = {}
            for cat in categ:
                temp1 = temp[cat].fillna(0)
                try:
                   res_temp[cat]=(temp1.iloc[:,1]*temp1.iloc[:,4]/temp1.iloc[:,5]).mean()
                    #res_temp[cat] = (temp1.iloc[:, 0] * temp1.iloc[:, 3] / temp1.iloc[:, 4]).mean()
                except:
                    res_temp[cat] = np.nan
            net_res[key] = res_temp
        return net_res,poi_pos
     except Exception as e:
        logger.error("Failed to find parking rate. {}".format(e))

    def conv_2_list(self,row):
        geo_pts = []
        for elem_1 in row['geoPoint']:
            geo_pts.append([elem_1['latitude'], elem_1['longitude']])
        return geo_pts

    def poi(self,spaceId,radius):
      try:
        logger.info("Finding point of Interest on Parking for spaceid") 
        #dp = DynamicParking()
        '''marker = dp.getDBConnection("52.55.107.13", "cdp", "sysadmin", "sysadmin")
        marker.execute("""select sid, state, providerdetails, boundary, label, levellabel, ts from parking_space""")
        data_db = marker.fetchall()
        geo_pts = pd.DataFrame(data_db, columns=['sid', 'state', 'providerdetails', 'geo_pts', 'label', 'levellabel', 'ts'])
        geo_pts['geo_pts'] = geo_pts['geo_pts'].apply(lambda x: ast.literal_eval(x))
        geo_pts['geo_pts'] = geo_pts['geo_pts'].apply(lambda x: dp.conv_2_list(x))
        print("line after getting data from db")'''
        logger.info("Fetching Lat and Longs for spaceId")
        geo_pts = self.get_geo_parking(spaceId)
        geo_pts['mean_position'] = geo_pts['geo_pts'].apply(lambda x: [np.mean([i[0] for i in x]), np.mean([i[1] for i in x])])
        sen_pts = geo_pts.groupby('sid').agg({'mean_position': 'first'})
        categ=['mosque','hindu_temple','home_good_store','university','electronics_store','courthouse','restaurant','bank','store','embassy','shopping_mall']

        print("Now going to fetch ratings")
        ratings,poi_info=self.get_rating(sen_pts,categ,radius)
        return ratings,poi_info,categ
      except Exception as e:
        logger.error("Unable to gather POI for parking area. {}".format(e))
        '''
        print("getting values")
        mean_rating = pd.DataFrame(ratings).mean()
        print("after fetching ratings")
        norm_rating = 10 * (mean_rating - mean_rating.min()) / (mean_rating.max() - mean_rating.min())
        s = pd.DataFrame(norm_rating)
        ss = s.to_json()
        sss = json.loads(ss)
        print(sss)'''

if __name__== "__main__":
    dp = DynamicParking()
    dp.poi('ParkingSpace__metro__Bldg1Flr7',50)
