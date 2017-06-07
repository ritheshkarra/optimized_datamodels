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
from server.logs import logger
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
            logger.info("parking spaceid not sent through URL so setting it to ALL")
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
        logger.info("Loading pickle file",filename)
        models = pickle.load(open(filePath, 'rb'))
        if len(models.keys()) == 0:
           logger.info('No data available for location {}.'.format(location))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"Data not available","title":"Parking Predictions"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Parking Predictions',description='No data available',code=204)
      except KeyError as e:
        logger.error('Parking predictions ended with exception.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"Parking Predictions"})
        #raise falcon.HTTPError(status="400 Bad Request",title='Parking Predictions',description='Invalid Request',code=400)
      except FileNotFoundError as e:
        logger.error('Error loading pickle file.{}'.format(e))
        resp.status = falcon.HTTP_404
        resp.body= json.dumps({"Status Code":404,"Description":"File not found","title":"Parking Predictions"})
        #raise falcon.HTTPError(status="404 Not found",title='Parking Predictions',description='Not Found',code='404')
      except Exception as e:
         logger.error('Unknow exception at parking predictions.{}'.format(e))
         resp.status = falcon.HTTP_500
         resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Parking Predictions"})
         #raise falcon.HTTPError(status="500 Internal Server Error",title='Parking Predictions',description='Internal Server Error',code='500')
      forecast_values = {}
      for parking_space in models.keys():
          if parkingspaceid == "all":
             logger.info("set parking spaceid to ALL")
             forecast_values[parking_space] = pf.get_parkingforecast(models[parking_space], datetime.datetime.fromtimestamp(float(starttime)                               ),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
             resp.body = forecast_values[parking_space]
          elif parking_space == parkingspaceid:
               logger.info("Parking space id set to",parking_space)
               forecast_values[parking_space]=pf.get_parkingforecast(models[parking_space], datetime.datetime.fromtimestamp(float(starttime)),                                   datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
               resp.body = forecast_values[parking_space]
          else:
                logger.info("No forcasting for :: ", parking_space)



class NextPSpace(object):
    def on_get(self, req, resp):
     try:
        input_params = req.params  #loading input parameters from the URL requested in browser.If params are empty then it will raise exception
        spaceId = input_params['spaceid']
        if 'radius' in input_params:
            radius = int(input_params['radius'])
        else:
            logger.info("Radius value not passed through request url so setting it to 50 by default")
            radius=50
        nps = NextParkingSpace()
        output = {}
        rd=nps.next_parkingspace_main(spaceId,radius)
        le = []
        for index, row in rd.iterrows():
            ke = {"Name": row['DE'], "Location": row['SHP']}
            le.append(ke)
        output["nearBySpaceName"]=le
        resp.status = falcon.HTTP_200
        resp.body= json.dumps(output)
        if len(le) == 0:
           logger.info('No data available for spaceID {}.'.format(spaceId))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"Data Not Available","title":"Next Parking Space"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Next Parking Space',description='No data available',code=204)
     except KeyError as e:
        logger.error('Invalid Request.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"Next Parking Space"})
        #raise falcon.HTTPBadRequest(status="400 Bad Request",title='Next Parking Space',description='Invalid Request',code=400)
     except Exception as e:
        logger.info('Next Parking Space ended up with error .{}'.format(e))
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Next Parking Space"})
        #raise falcon.HTTPError(status='500 Internal Server Error',title='Next Parking Space',description='Internal Server Error',code=500)     
     
      
class DynamicParkingBasedOnSurrounding(object):
    def on_get(self,req, resp):
     try:
        input_params = req.params
        spaceId = input_params['spaceid']
        if 'radius' in input_params:
            radius = int(input_params['radius'])
        else:
            logger.info("Radius value not passed through request url so setting it to 50 by default")
            radius=50
        dp = DynamicParking()
        ratings,poi_info,categ=dp.poi(spaceId,radius)
        poi = []
        output={}
        for cat in categ:
            for index,row in poi_info[spaceId][cat].iterrows():
                if str(row['rating']) == "nan":
                    row['rating'] = 0
                poid = {"name": row['name'], "location": row['loc'], "rating": row['rating'], "distance": round(row['dist(km)'],6), "isOpen":row['is_open']}
                poi.append(poid)
        pr = []
        for i in ratings[spaceId]:
            if str(ratings[spaceId][i]) == "nan":
                ratings[spaceId][i] = 'NULL'
            prd = {"typeOfPlace": i, "rating": ratings[spaceId][i]}
            pr.append(prd)
        if len(pr) == 0:
           logger.info('No data available for location {}.'.format(spaceId))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"No data available","title":"Dynamic Parking Space"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Dynamic Parking Space',description='No data available',code=204)
        output["poi"] = poi
        #output["prakingRate"]=pr
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output)
     except KeyError as e:
        logger.error('Invalid Request.{}'.format(e))
        #raise falcon.HTTPBadRequest(status="400 Bad Request",title='Dynamic Parking Space',description='Invalid Request',code=400)
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"Dynamic Parking Space"})
     except Exception  as e:
        logger.info('Unable to fetch Dynamic Parking for spaceId.{}'.format(e))
        #raise falcon.HTTPError(status='500 Internal Server Error',title='Dynamic Parking Space',description='Internal Server Error',code=500)
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Dynamic Parking Space"})

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
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"Comp Parking Space"})
        #raise falcon.HTTPBadRequest(status="400 Bad Request",title='Comp Parking',description='Invalid Request',code=400)
     except psycopg2.OperationalError as e:
        logger.error('Failed to execute DB Query.{}'.format(e))
        resp.status = falcon.HTTP_408
        resp.body= json.dumps({"Status Code":408,"Description":"Connection Timed Out","title":"Comp Parking Space"})
        #raise falcon.HTTPError(status='408 Timed Out',title='Comp Parking SPace',description='Internal Server Error',code=408)
     except Exception as e:
        logger.error('Comp Parking Space ended with Error .{}'.format(e))
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Comp Parking Space"})
        #raise falcon.HTTPBadRequest(status='500 Internal Server ,title='Comp Parking Space',description='Internal Server Error',code=500)

     out = marker.fetchall()
     if len(out) == 0: #If length of out is zero, which means no data available for the DB query executed so resultant will raise HTTP 204 code
           logger.info('No data available for location {}.'.format(spaceId))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"No data available","title":"Comp Parking Space"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Comp Parking Space',description='No data available',code=204)
     output = {}
     for i in out:
         output["parkingSpace"] = i[0]
         output["nearBySpace"] = i[1]
         output["rating"] = i[2]
     resp.status = falcon.HTTP_200 #Falcon httpp status code to 200
     resp.body = json.dumps(output) # Will return the data to browser in json format
