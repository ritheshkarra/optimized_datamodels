#!/usr/bin/python
import pandas as pd
import falcon
import json
import pickle
import datetime
import os
from requests.exceptions import ConnectionError
import numpy as np
import psycopg2
#from server.logs import logger
from app.models.parking.Forecastingutility import Forecast
from app.models.parking.NextParkingSpace import NextParkingSpace
from app.models.parking.SurroundingBasedDynamicParkingPolicy import DynamicParking

class ParkingPredictions(object):
    def on_get(self, req, resp):
      try: 
        input_params = req.params  #loading input parameters from the URL requested in browser
        location = input_params['location']
        if 'spaceid' in input_params:
            parkingspaceid = input_params['spaceid']
        else:
            parkingspaceid = "all"
        starttime = input_params['starttime']
        endtime = input_params['endtime']
        resp.status = falcon.HTTP_200
        logger.info("calling Forecast method")
        pf= Forecast()
        fileDir = os.path.dirname(__file__)
        #fileName = "parkingforcastModelAll.pickle"
        fileName = "parkingforcast.pickle"
        filePath = os.path.join(fileDir, fileName)
        models = pickle.load(open(filePath, 'rb'))
        if len(models.keys()) == 0:
           logger.info('No data available for location {}.'.format(location))
           raise falcon.HTTPError(status="204 Data Not Avilable",title='Parking Predictions',description='No data available',code=204)
      except KeyError as e:
        logger.error('Parking predictions ended with exception.{}'.format(e))
        raise falcon.HTTPError(status="400 Bad Request",title='Parking Predictions',description='Invalid Request',code=400)
      except FileNotFoundError as e:
        logger.error('Error loading pickle file.{}'.format(e))
        raise falcon.HTTPError(status="404 Not found",title='Parking Predictions',description='Not Found',code='404')
      except Exception as e:
         logger.error('Unknow exception at parking predictions.{}'.format(e))
         raise falcon.HTTPError(status="500 Internal Server Error",title='Parking Predictions',description='Internal Server Error',code='500')
      forecast_values = {}
      for parking_space in models.keys():
          if parkingspaceid == "all":
             forecast_values[parking_space] = pf.get_parkingforecast(models[parking_space], datetime.datetime.fromtimestamp(float(starttime)                               ),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
             resp.body = forecast_values[parking_space]
          elif parking_space == parkingspaceid:
               forecast_values[parking_space]=pf.get_parkingforecast(models[parking_space], datetime.datetime.fromtimestamp(float(starttime)),                                   datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
               resp.body = forecast_values[parking_space]
          else:
                logger.info("No forcasting for :: ", parking_space)



class NextPSpace(object):
    def on_get(self, req, resp):
     try:
        input_params = req.params  #loading input parameters from the URL requested in browser.If params are empty then it will raise exception
        spaceId = input_params['spaceid']
        radius = int(input_params['radius'])
        nps = NextParkingSpace()
        output = {}
        rd=nps.next_parkingspace_main(spaceId,radius)
        ke = {}
        le = []
        for index, row in rd.iterrows():
            ke = {"Name": row['DE'], "Location": row['SHP']}
            le.append(ke)
        output["nearBySpaceName"]=le
        resp.status = falcon.HTTP_200
        resp.body= json.dumps(output)
     except KeyError as e:
        logger.error('Invalid Request.{}'.format(e))
        raise falcon.HTTPBadRequest(status="400 Bad Request",title='Next Parking Space',description='Invalid Request',code=400)
     except psycopg2.OperationalError as e:
        logger.error('Failed to connect to DB.{}'.format(e))
        raise falcon.HTTPBadRequest(status='408 Timed Out',title='Next Parking Space',description='Request Time Out',code=408)
     except Exception as e:
        logger.info('Execution of DB query failed.{}'.format(e))
        raise falcon.HTTPError(status='500 Internal Server Error',title='Next Parking Space',description='Internal Server Error',code=500)     

     if len(rd) == 0:
           logger.info('No data available for spaceID {}.'.format(spaceId))
           raise falcon.HTTPError(status="204 Data Not Avilable",title='Next Parking Space',description='No data available',code=204)
     
      
class DynamicParkingBasedOnSurrounding(object):
    def on_get(self,req, resp):
     try:
        input_params = req.params
        spaceId = input_params['spaceid']
        radius = int(input_params['radius'])
        dp = DynamicParking()
        ratings,poi_info,categ=dp.poi(spaceId,radius)
        poi = []
        poid = {}
        for cat in categ:
            for index,row in poi_info[spaceId][cat].iterrows():
                if str(row['rating']) == "nan":
                    row['rating'] = 'NULL'
                poid = {"name": row['name'], "Location": row['loc'], "Rating": row['rating'], "Distance": row['dist(km)'],"is_open":row['is_open']}
                poi.append(poid)
        pr = []
        prd = {}
        for i in ratings[spaceId]:
            if str(ratings[spaceId][i]) == "nan":
                ratings[spaceId][i] = 'NULL'
            prd = {"TypeOfPlace": i, "Rating": ratings[spaceId][i]}
            pr.append(prd)
        output["poi"] = poi
        output["prakingrate"]=pr
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output)
     except KeyError as e:
        logger.error('Invalid Request.{}'.format(e))
        raise falcon.HTTPBadRequest(status="400 Bad Request",title='Dynamic Parking Space',description='Invalid Request',code=400)
     except psycopg2.OperationalError  as e:
        logger.error('Failed to connect to DB.{}'.format(e))
        raise falcon.HTTPBadRequest(status='408 Timed Out',title='Dynamic Parking Space',description='Request Time Out',code=408)
     except Exception  as e:
        logger.info('Execution of DB query failed.{}'.format(e))
        raise falcon.HTTPError(status='500 Internal Server Error',title='Dynamic Parking SPace',description='Internal Server Error',code=500)

     if len(poi_info) == 0:
           logger.info('No data available for location {}.'.format(spaceId))
           raise falcon.HTTPError(status="204 Data Not Avilable",title='Dynamic Parking Space',description='No data available',code=204)

class CompParking(object):
    def on_get(self,req, resp):
     try:
        input_params = req.params
        spaceId = input_params['spaceid']
        dp = DynamicParking()
        marker = dp.getDBConnection("52.55.107.13", "cdp", "sysadmin", "sysadmin") # Connection to Postgres DB
        query = "select n.parkingsapce,n.nearparkingspace, r.rating from next_parking_space as n, parking_space_rating as r where n.parkingsapce = r.parkingsapce and n.parkingsapce = '" + spaceId + "'"
        marker.execute(query)
     except KeyError as e:
        logger.error('Invalid Request.{}'.format(e))
        raise falcon.HTTPBadRequest(status="400 Bad Request",title='Comp Parking',description='Invalid Request',code=400)
     except RuntimeError as e:
        logger.error('Failed to execute DB Query.{}'.format(e))
        raise falcon.HTTPError(status='500 Internal Server Error',title='Comp Parking SPace',description='Internal Server Error',code=500)
     except Exception as e:
        logger.error('Failed to connect to DB.{}'.format(e))
        raise falcon.HTTPBadRequest(status='408 Timed Out',title='Comp Parking Space',description='Request Time Out',code=408)

     out = marker.fetchall()
     if len(out) == 0: #If length of out is zero, which means no data available for the DB query executed so resultant will raise HTTP 204 code
           logger.info('No data available for location {}.'.format(spaceId))
           raise falcon.HTTPError(status="204 Data Not Avilable",title='Comp Parking Space',description='No data available',code=204)
     output = {}
     for i in out:
         output["parkingSpace"] = i[0]
         output["nearBySpace"] = i[1]
         output["rating"] = i[2]
     resp.status = falcon.HTTP_200 #Falcon httpp status code to 200
     resp.body = json.dumps(output) # Will return the data to browser in json format
