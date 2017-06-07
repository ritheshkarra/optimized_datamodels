#!/usr/bin/python
import json
import pickle
import datetime
import os
import numpy as np
import psycopg2
from server.logs import logger

class So2Predictions(object):
    def on_get(self, req, resp):
     try:                                     #try block to check and catch the exceptions if req is empty
        input_params = req.params
        location = input_params['location']
        if 'id' in input_params:
            sensorid = input_params['id']
        else:
            sensorid = "all"            #If, sensorid not found in input request, it takes all as value
        starttime = input_params['starttime']
        endtime = input_params['endtime']
        resp.status = falcon.HTTP_200
        pf= Forecast()
        fileName = "AirSo2All.pickle"
        filePath = os.path.join(fileDir, fileName)
        models = pickle.load(open(filePath, 'rb'))
        if len(models.keys()) == 0:        
           ##Falcon HTTP Exception handling loop begins http://falcon.readthedocs.io/en/stable/api/errors.html
           logger.info('No data available for location {}.'.format(location))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"Data not available","title":"SO2 Predictions"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='SO2 Predictions',description='No data available',code=204)
     except KeyError as e:
         logger.error('Invalid So2 Request'.format(e))
         resp.status = falcon.HTTP_400
         resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"SO2 Predictions"})
         #raise falcon.HTTPError(status="400 Bad Request",title='SO2 Predictions',description='Invalid Request',code=400)
     except FileNotFoundError as e:                                     #Raises exception, if pickle file not found
        logger.error('Error loading pickle file.{}'.format(e))
        resp.status = falcon.HTTP_404
        resp.body= json.dumps({"Status Code":404,"Description":"File not found","title":"SO2 Predictions"})
        #raise falcon.HTTPError(status="404 Not found",title='SO2 Predictions',description='Not Found',code='404')
     except Exception as e:
         logger.error('Unknown error at So2 Predictions.{}'.format(e))
         resp.status = falcon.HTTP_500
         resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"SO2 Predictions"})
         #raise falcon.HTTPError(status="500 Internal Server Error",title='SO2 Predictions',description='Internal Server Error',code='500')
     forecast ={}
     for sensid in models.keys():
         if sensorid == "all":    #calling get_parkingforecast
                forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
         elif sensid == sensorid:
                forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
                resp.body = forecast[sensid]
         else:
                logger.info("No forcasting for :: ", sensid)


class HumidityPredictions(object):
    def on_get(self, req, resp):
     try:
        input_params = req.params
        location = input_params['location']
        if 'id' in input_params:
            sensorid = input_params['id']
        else:
            sensorid = "all"
        starttime = input_params['starttime']
        endtime = input_params['endtime']
        resp.status = falcon.HTTP_200
        pf= Forecast()
        fileDir = os.path.dirname(__file__)
        fileName = "humidityAll.pickle"                 #Using the humidity data available in pickefile
        filePath = os.path.join(fileDir, fileName)
        models = pickle.load(open(filePath, 'rb'))           #Loading the pickle file
        if len(models.keys()) == 0:
           logger.info('No data available for location {}.'.format(location))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"Data not available","title":"Humidity Predictions"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Humidity Predictions',description='No data available',code=204)
     except KeyError as e:
        logger.error('Invalid HumidityPredictions Request.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"Humidity Predictions"})
        #raise falcon.HTTPError(status="400 Bad Request",title='Humidity Predictions',description='Invalid Request',code=400)
     except FileNotFoundError as e:
        logger.error('Error loading pickle file.{}'.format(e))
        resp.status = falcon.HTTP_404
        resp.body= json.dumps({"Status Code":404,"Description":"File not found","title":"Parking Predictions"})
        #raise falcon.HTTPError(status="404 Not found",title='Humidity Predictions',description='Not Found',code='404')
     except Exception as e:
        logger.error('Error at So2 predictions.{}'.format(e))
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Humidity Predictions"})
        #raise falcon.HTTPError(status="500 Internal Server Error",title='Humidity Predictions',description='Internal Server Error',code='500')

     forecast ={}
     for sensid in models.keys():
            if sensorid == "all":
                forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
            elif sensid == sensorid:
                forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
                resp.body = forecast[sensid]
            else:
                logger.info("No forcasting for :: ", sensid)


class AmbientTempPredictions(object):
    def on_get(self, req, resp):
     try:
        input_params = req.params
        location = input_params['location']
        if 'id' in input_params:
            sensorid = input_params['id']
        else:
            sensorid = "all"
        starttime = input_params['starttime']
        endtime = input_params['endtime']
        resp.status = falcon.HTTP_200
        pf= Forecast()
        fileDir = os.path.dirname(__file__)
        fileName = "ambienttemperatureAll.pickle"
        filePath = os.path.join(fileDir, fileName)
        models = pickle.load(open(filePath, 'rb'))
        if len(models.keys()) == 0:
           logger.info('No data available for location {}.'.format(location))
           resp.status = falcon.HTTP_204
           resp.body= json.dumps({"Status Code":204,"Description":"Data not available","title":"AmbientTemperature Predictions"})
           #raise falcon.HTTPError(status="204 Data Not Avilable",title='Ambient Temperature',description='No data available',code=204)
     except KeyError as e:
        logger.error('Invalid Ambient Temperature Request.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Invalid Request","title":"AmbientTemperature Predictions"})
        #raise falcon.HTTPError(status="400 Bad Request",title='Ambient Temperature',description='Invalid Request',code=400)
     except FileNotFoundError as e:
        logger.error('Error loading pickle file.{}'.format(e))
        resp.status = falcon.HTTP_404
        resp.body= json.dumps({"Status Code":404,"Description":"File not found","title":"AmbientTemperature Predictions"})
        #raise falcon.HTTPError(status="404 Not found",title='Ambient Temperature',description='Not Found',code='404')
     except Exception as e:
        logger.error('Error at Ambient Temperature predictions.{}'.format(e))
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Ambient TemperaturePredictions"})
        #raise falcon.HTTPError(status="500 Internal Server Error",title='Ambient Temperature',description='Internal Server Error',code='500')

     forecast ={}
     for sensid in models.keys():
         if sensorid == "all":
            forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
         elif sensid == sensorid:
              forecast[sensid] = pf.get_forecast(models[sensid],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))).to_json(orient='records', date_format='iso', date_unit='s')
              resp.body = forecast[sensid]
         else:
              logger.info("No forcasting for :: ", sensid)
