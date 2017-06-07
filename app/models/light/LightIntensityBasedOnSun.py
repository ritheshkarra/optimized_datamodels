#!/usr/bin/python
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
import os
from server.logs import logger
from dateutil.parser import parse

#os.environ['TZ']="America/New_York"
#os.environ['TZ']='Newyork'
class LightIntensityBasedOnSun:
    def forecast(self,location,offset):
     try:
        logger.info("Getting Latitude and Longitude from map API for location")
        # Getting Latitude and Longitude from HERE map API
        result_1 = requests.get(
            'https://geocoder.cit.api.here.com/6.2/geocode.json?searchtext=' + location + '/&app_id=QacvSHflGqkVBJGvs9OS&app_code=9dbgDyDrC1ChasubHX7Xfw&gen=8')
        try:
          out_1 = result_1.json()
          if len(out_1) == 0:
            logger.info("No lat and long available for location")
        except Exception as e:
            logger.error("Failed with error. {} ".format(e))
        Latitude = out_1['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude']
        Longitude = out_1['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']
        # Getting Sunrise and Sunset from Dark Sky API
        # Access Key - f837b14f3e53cfed0e7cec9e3765e3c5
        result_2 = requests.get(
            'https://api.darksky.net/forecast/f837b14f3e53cfed0e7cec9e3765e3c5/' + str(Latitude) + ',' + str(
                Longitude) + '/?exclude=currently,minutely?extend=hourly')
        try:
           logger.info("getting Sunrise and Sunset for location")
           out_2 = result_2.json()
        except Exception as e:
           logger.error("Failed to get Sunrise and Sunset. {} ".format(e))
        sunrise_time = []
        sunset_time = []
        dates = []

        for x in range(7):
            sunriseTime = out_2['daily']['data'][x]['sunriseTime']
            sunrise_time.append(sunriseTime)
            sunsetTime = out_2['daily']['data'][x]['sunsetTime']
            sunset_time.append(sunsetTime)
            date = out_2['daily']['data'][x]['time']
            dates.append(date)

        # Converting Sunrise time to proper datetime format
        sunrise_realtime = []
        for i in sunrise_time:
            your_timestamp = i
            #date = datetime.fromtimestamp(your_timestamp) + timedelta(hours=5) + timedelta(minutes=30) - timedelta(minutes=offset)
            date = datetime.fromtimestamp(your_timestamp) - timedelta(minutes=offset)
            #date = datetime.fromtimestamp(your_timestamp)
            sunr_date_real = str(date.strftime(str(date)))
            # print(sunr_date_real)
            sunrise_realtime.append(sunr_date_real)

        # Converting Sunset time to proper datetime format
        sunset_realtime = []
        for i in sunset_time:
            your_timestamp = i
            #date = datetime.fromtimestamp(your_timestamp) + timedelta(hours=5) + timedelta(minutes=30) + timedelta(minutes=offset)
            date = datetime.fromtimestamp(your_timestamp) + timedelta(minutes=offset)
            #date = datetime.fromtimestamp(your_timestamp)
            suns_date_real = str(date.strftime(str(date)))
            sunset_realtime.append(suns_date_real)

        Data = pd.DataFrame()
        Data['Off_time'] = sunrise_realtime
        Data['On_time'] = sunset_realtime
        off = [parse(x) for x in Data['Off_time']]
        ee_1 = []
        for i in off:
            off_utc = i.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
            ee_1.append(off_utc)
        Data['Off_time'] = pd.DataFrame(ee_1)

        on = [parse(x) for x in Data['On_time']]
        ee_2 = []
        for i in on:
            on_utc = i.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
            ee_2.append(on_utc)
        Data['On_time'] = pd.DataFrame(ee_2)
        return (Data)
     except Exception as e:
        logger.error("Error in function forecast. {}".format(e))

def main():
    l = LightIntensityBasedOnSun()
    logger.info("calling forecast method")
    s = l.forecast("Banglore", 10)
    output = {}
    #output['data'] = json.loads(s.to_json(orient='records', date_format='iso', date_unit='ms'))
    output['data'] = json.loads(s.to_json(orient='records', date_unit='ms'))
    print("------------------------------------------")
    print(json.dumps(output))

    
if __name__ == "__main__":
    main()
