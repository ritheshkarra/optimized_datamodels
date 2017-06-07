#!/usr/bin/python
import falcon
import json
from app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
from app.models.toxic_heavy_gas_dispersion.airDispersionModelCommander import airDispersionModel
from server.logs import logger

class Weather:
    def on_get(self,req, resp):
     try:
        input_params = req.params #Gather paramaters from the request i.e lat and longs
        lat = input_params['lat']
        lng = input_params['lng']
        winfo = WeatherInfo()
        temperature, windBearing, windDirection, windSpeed, weather, pressure, cloudCoverage, hour, day = winfo.weatherInfo(lat,lng)
        #output = {"temperature":'+ str(temperature) +', "windBearing":'+str(windBearing)+', "windDirection":'+str(windDirection)+', "windSpeed":'+str(windSpeed)+', "weather":'+str(weather)+', "pressure":'+str(pressure)+', "cloudCoverage":'+str(cloudCoverage)+', "hour":'+str(hour)+', "day":'+str(day)+'}
     except KeyError as e:
        logger.error('Weather Info request ended with exception.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Malformed Request","title":"Weather Info"})
        #raise falcon.HTTPError(status="400 Bad Request",title='Weather Information',description='Invalid Request',code=400)
     output = {}  #Declaring dictiornary variable to empty
     output["temperature"] = temperature
     output["windBearing"] = windBearing
     output["windDirection"] = windDirection
     output["windSpeed"] = windSpeed
     output["weather"] = weather
     output["pressure"] = pressure
     output["cloudCoverage"] = cloudCoverage
     output["hour"] = hour
     output["day"] = day
     if len(output) == 0: #if length is zero, then there is no data available for the request
        logger.info("No data available for requested Lat {} and Long {}".format(lat,lng))
        resp.status = falcon.HTTP_204
        resp.body= json.dumps({"Status Code":204,"Description":"Data Not Available","title":"WeatherInfo"})
        #raise falcon.HTTPError(status="204 Data Not Avilable",title='Weather Information',description='No data available',code=204)
     resp.status = falcon.HTTP_200
     resp.body =  json.dumps(output) #output in json format -> browser

class airDispersion:
    def on_get(self, req, resp):
     try:
        input_params = req.params #takes input params from browser
        gasName = input_params['gasname']
        concentrationLevel = input_params['clevel']
        lat = input_params['lat']
        lng = input_params['lng']
        airDisp = airDispersionModel() #calling Air Dispersion function where the alogarith is defined and shows in which way gas is travelling
     except KeyError as e:
        logger.error('Air Dispersion request ended with exception.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Malformed Request","title":"Air Dispersion"})
        #raise falcon.HTTPError(status="400 Bad Request",title='Air Dispersion',description='Invalid Request',code=400)
     if 'windbearing' in input_params:
            windBearing = input_params['windbearing']
            if 'windspeed' in input_params:
                print('in both')
                windSpeed = input_params['windspeed']
                print(gasName)
                print(concentrationLevel, lat, lng)
                out = airDisp.predictGasDispersionHeaveyGasEnvSensor(str(gasName),float(concentrationLevel),float(lat), float(lng),float(windBearing),float(windSpeed))
            else:
                print('in windbearing')
                out = airDisp.predictGasDispersionHeaveyGasEnvSensor(str(gasName),float(concentrationLevel),float(lat), float(lng),pWindBearing=float(windBearing))
     elif 'windspeed' in input_params:
            windSpeed = input_params['windspeed']
            print('in wind speed')
            out = airDisp.predictGasDispersionHeaveyGasEnvSensor(str(gasName),float(concentrationLevel),float(lat), float(lng),pWindSpeed=float(windSpeed))
     else:
            print('in nothing')
            print(gasName)
            print(concentrationLevel, lat, lng)
            out = airDisp.predictGasDispersionHeaveyGasEnvSensor(str(gasName),float(concentrationLevel),float(lat),float(lng))

     output = {}
     output["modelName"] = out[0]
     s1 = out[1].to_json(orient='records')
     ss1 = json.loads(s1)
     output["dataset75"] = ss1

     if len(out) == 3:
         s2 = out[2].to_json(orient='records')
         ss2 = json.loads(s2)
         output["dataSet25"] = ss2
     elif len(out) == 2:
          output["dataSet25"] = "nodata"
     if len(output) == 0:
        logger.info("No data available for requested Lat {} and Long {}".format(lat,lng))
        resp.status = falcon.HTTP_204
        resp.body= json.dumps({"Status Code":204,"Description":"Data Not Available","title":"Air Dispersion"})
        #raise falcon.HTTPError(status="204 Data Not Avilable",title='Air Dispersion',description='No data available',code=204)
     resp.status = falcon.HTTP_200
     resp.body = json.dumps(output)
