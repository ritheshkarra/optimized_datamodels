#!/usr/bin/python
import json
import falcon
from falcon import HTTPBadRequest
from app.models.light.LightIntensityBasedOnSun import LightIntensityBasedOnSun
from server.logs import logger

class lightIntensity:
    def on_get(self, req, resp):
        try:
              input_params = req.params  #loading paramters from the URL 
              location = input_params['location']
              offset = input_params['offset']
              logger.info("Executing LightIntensityBasedOnSun model")
              light = LightIntensityBasedOnSun()
              output = light.forecast(location,int(offset))
              jsonoutput = {} # Defining the dictionary jsonoutput variable and set its value to empty
              jsonoutput['data'] = json.loads(output.to_json(orient='records', date_format='iso', date_unit='s'))
              resp.status = falcon.HTTP_200
              resp.body = json.dumps(jsonoutput) #sending data to browser in json format
              if len(resp.body) == 0: #If the resp.body is empty(the request doesnt have data, it shows no data available)
                logger.info("No data available for location {}.".format(location))
                resp.status = falcon.HTTP_204
                resp.body= json.dumps({"Status Code":204,"Description":"Data not available","title":"Light Intensity"})
                #raise falcon.HTTPError(status="204 Data Not Avilable",title='LightIntensity',description='No data available',code=204)
        except KeyError as e:
              logger.error('Request doesnt have all the required parameters.{}'.format(e))
              resp.status = falcon.HTTP_400
              resp.body= json.dumps({"Status Code":400,"Description":"Malformed Request","title":"Light Intensity"})
              #raise falcon.HTTPError(status="400 Bad Request",title='LightIntensity',description='The requested URL is not correct',code=400)
        except Exception as e:
              logger.error('Exception at Light intensity end point.{}'.format(e))
              resp.status = falcon.HTTP_500
              resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"Light Intensity"})
              #raise falcon.HTTPError(status="500 Internal Server Error",title='LightIntensity',description='Internal Server Error',code=500)
