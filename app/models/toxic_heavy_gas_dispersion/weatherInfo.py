#!/usr/bin/python
import requests
import json
from pandas.io.json import json_normalize
import datetime
from dateutil import parser
from logbook import Logger, StreamHandler
import sys
StreamHandler(sys.stdout).push_application()
log = Logger('Logbook')
#temprature,wind angle,wind direction,wind speed,current observations
#in meter


class WeatherInfo:

    def windRefHeight(self):
        return 10

    def weatherInfo(self,lat,lng):
        #f = requests.get('http://api.wunderground.com/api/b06babfa6f196d38/forecast/conditions/q/'+country+'/'+city+'.json')
        f = requests.get('http://api.wunderground.com/api/b06babfa6f196d38/forecast/conditions/q/' + str(lat) + ',' + str(lng) + '.json')

        result = f.json()
        temprature = result['current_observation']['temp_c']
        #We need temprature in kevin as well.
        temprature = temprature + 273.15 # add 273.15 to convert it to kevin scale.
        windBearing = result['current_observation']['wind_degrees']
        windDirection = result['current_observation']['wind_dir']
        windSpeed = result['current_observation']['wind_kph']
        # forcasted ave wind speed. we will use this value for wind speed in case it fails to get a value
        avg_windSpeed = result['forecast']['simpleforecast']['forecastday'][0]['avewind']['kph']
        localTime = result['current_observation']['local_time_rfc822']
        dt = parser.parse(localTime)
        hour = dt.hour
        day = True
        if (hour >= 0) and (hour <= 6):
            day = False
        elif (hour >= 7) and (hour <= 18):
            day = True
        else:
            day = False
        #convert wind speed to m/s
        if (windSpeed == 0):
            #log.info("Setting avg wind speed as fetching current wind failed.")
            windSpeed = avg_windSpeed
        windSpeed = round(windSpeed * 0.277778) #convert in m/s
        if (windSpeed == 0):
            #log.info("Eveng avg wind speed could not obtained so setting up a default value of 5 m/s")
            windSpeed = 5  # A default arbitatiry number choosen to avoid any divind by zero issues.
        c_type = result['current_observation']['icon']
        pressure = result['current_observation']['pressure_mb']
        #Convert to Pa
        #print("pressure " + pressure)
        p = float(pressure) * 100
        pressure = p

        if c_type == 'clear' or c_type == 'very Hot' or c_type == 'very Cold':
            c_type = 'clear'
            cloudCoverage = 1/8
        elif c_type == 'hazy' or c_type == 'foggy':
            c_type = 'hazy'
            cloudCoverage = 4 / 8
        else:
            c_type = 'cloudy'
            cloudCoverage = 7 / 8
        weather = c_type
        return temprature,windBearing,windDirection,windSpeed,weather,pressure,cloudCoverage,hour,day

    #set up Beaufort scale
    #ref https://en.wikipedia.org/wiki/Beaufort_scale
    bft_threshold = (0.3, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6)
    bft_threshold_descriptions = ('calm', 'light air', 'Light Breeze', 'Gentle Breeze', 'Moderate Breeze', 'Fresh Breeze','Strong Breeze', 'High Wind', 'Gale', 'Strong Gale', 'Storm', 'Violent Storm','Hurricane')

    #Converts wind from m/s to Beaufort scale.
    def wind_bft(self,wondSpeed_ms):
        "Convert wind from metres per second to Beaufort scale"
        if wondSpeed_ms is None:
            return None
        for bft in range(len(self.bft_threshold)):
            if wondSpeed_ms < self.bft_threshold[bft]:
                return bft,self.bft_threshold_descriptions[bft]
        return len(self.bft_threshold),self.bft_threshold_descriptions[len(self.bft_threshold)]

def main():
    #print(weatherInfo('IN','Kolkata'))
    wi = WeatherInfo()
    #Mexico City, Mexico
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847
    temprature, windBearing, windDirection, windSpeed, weather,pressure,cloudCoverage,hour,day = wi.weatherInfo(gasLeakLat, gasLeakLong)
    print(temprature)
    print(windBearing)
    print(windDirection)
    print(windSpeed)
    print(weather)
    print(pressure)
    print(hour)
    print(day)



if __name__ == "__main__":
    main()
