from numpy import *
from pandas import *
import time
import math
import app.models.toxic_heavy_gas_dispersion.toxicLightGasDispersionPlumeHeightRise as tlgdphr
import app.models.toxic_heavy_gas_dispersion.gasDispersionModelingUtilityFunctions as gdmuf
import config
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
from app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
import app.models.toxic_heavy_gas_dispersion.latLongUtil as latLongUtil
import folium
import pandas
import app.models.toxic_heavy_gas_dispersion.visual_on_maps as visual_on_maps

#Algorithm is successfully applied when at a distance duration t(s) is greater than 2.5 x / wind_speed so that a steady
# state is reached.
class ToxicLightGasDispersionPlumeModel():
    #gasDensity = {'LP':500, 'CH4':0.717, 'CO':1.25, 'Cl':2.994}
    #nameOfColumns = ['x', 'he', 'sigmx', 'sigmay', 'C'] #x(m),he(m),sigmax(m),sigmay(m), C(mug/m3)

    def round(self,value):
        return config.customRounding(value)

    def DispersionCoefficientPlume(self,x, stable_class,terrain="urban"):
        # assign transverse and vertical dispersion coefficients (standard terrain)
        if (terrain == "rural"):

            if stable_class == 'A':
                sigma_y = 0.22*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.2*x
            elif stable_class == 'B':
                sigma_y = 0.16*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.12*x
            elif stable_class == 'C':
                sigma_y = 0.11*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.08*x / sqrt(1.0 + 0.0002*x)
            elif stable_class == 'D':
                sigma_y = 0.08*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.06*x / sqrt(1.0 + 0.0015*x)
            elif stable_class == 'E':
                sigma_y = 0.06*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.03*x / (1.0 + 0.0003*x)
            else:
                sigma_y = 0.04*x / sqrt(1.0 + 0.0001*x)
                sigma_z = 0.016*x / (1.0 + 0.0003*x)
        else:
            if stable_class == 'A':
                sigma_y = 0.32*x / sqrt(1.0 + 0.0004*x)
                sigma_z = 0.24*x * sqrt(1.0 + 0.001*x)
            elif stable_class == 'B':
                sigma_y = 0.32 * x / sqrt(1.0 + 0.0004 * x)
                sigma_z = 0.24 * x * sqrt(1.0 + 0.001 * x)
            elif stable_class == 'C':
                sigma_y = 0.22*x / sqrt(1.0 + 0.0004*x)
                sigma_z = 0.20*x
            elif stable_class == 'D':
                sigma_y = 0.16*x / sqrt(1.0 + 0.0004*x)
                sigma_z = 0.14*x / sqrt(1.0 + 0.0003*x)
            elif stable_class == 'E':
                sigma_y = 0.11*x / sqrt(1.0 + 0.0004*x)
                sigma_z = 0.08*x / sqrt(1.0 + 0.0015*x)
            else:
                sigma_y = 0.11 * x / sqrt(1.0 + 0.0004 * x)
                sigma_z = 0.08 * x / sqrt(1.0 + 0.0015 * x)

        return self.round(sigma_y), self.round(sigma_z)

    def calcuateConcentration(self,emissionRate,windSpeed,sigma_y,sigma_z,plumeRise,x,y,z):
        c1 = ((emissionRate * pow(10,9)) / (windSpeed*2*math.pi*sigma_y))*math.exp(-((y**2)/(2*(sigma_y**2))))
        #+ math.exp(-(pow((plumeRise+z),2)/(2*pow(sigma_z,2))))

        c2 = math.exp(-(pow((plumeRise-z),2)/(2*pow(sigma_z,2)))) + math.exp(-(pow((plumeRise+z),2)/(2*pow(sigma_z,2))))
        #c2 = math.exp(-(pow((plumeRise - z), 2)))
        c = c1 * (1/sigma_z) * c2
        return self.round(c)

     #y lateral dispersion, Z height
    def calculateConcentrationForPlumeGas(self,cloudCoverage, windVelocity,windBearing,weather, day,terrain,gravity,windRefHeight,ambientTemprature, gasExitTemprature,
                                         intervalOfObservations,stackDiameter,stackHeight, exitGasSpeed,sourceEmissionRate,y,z,gas,gasLeakLat,gasLeakLong):
        stabilityClass = gdmuf.getAtmospericStabilityClass(windVelocity, cloudCoverage, day)
        # for test
        #stabilityClass = 'D'
        # Wind Speed at the top of the stack
        windSpeedAtStackHeight = gdmuf.calculateWindSpeedAtStackHeight(stabilityClass, windVelocity, stackHeight,
                                                                 windRefHeight, terrain)
        print("windSpeedAtStackHeight " + str(windSpeedAtStackHeight) + "windVelocity " + str(windVelocity))
        stackEffectiveHeight = tlgdphr.effectiveStackHeight(stackHeight, stackDiameter, exitGasSpeed, windSpeedAtStackHeight)

        isBuoyancy = tlgdphr.isBuoyancyDominated(stabilityClass, gasExitTemprature, ambientTemprature, stackDiameter,
                                         exitGasSpeed)
        # for testing
        #isBuoyancy =  False
        buoyancyFluxParameter = tlgdphr.calculateBuoyancyFluxParameter(gravity, exitGasSpeed, stackDiameter, gasExitTemprature,
                                                               ambientTemprature)
        distanceOfMaxPlumeRise = tlgdphr.calculationOfDistanceOfMaximumPlumeRise(isBuoyancy, buoyancyFluxParameter,
                                                                         stabilityClass,
                                                                         windSpeedAtStackHeight, gasExitTemprature,
                                                                         stackDiameter, exitGasSpeed)

        gradualPlumeRise, plumeRisexf = tlgdphr.calculationOfFinalPlumeRise(isBuoyancy,buoyancyFluxParameter, stackEffectiveHeight,distanceOfMaxPlumeRise
                                                        ,intervalOfObservations,stabilityClass,windSpeedAtStackHeight
                                                        ,ambientTemprature,gasExitTemprature,stackDiameter,exitGasSpeed)


        startingPoint = 0
        if (gas != None):
            list_c50 = ['y_c50','y_c50_lat1','y_c50_long1','y_c50_lat2','y_c50_long2']
            list_idlh = ['y_idlh', 'y_idlh_lat1', 'y_idlh_long1', 'y_idlh_lat2', 'y_idlh_long2']
            list_loc = ['y_loc', 'y_loc_lat1', 'y_loc_long1', 'y_loc_lat2', 'y_loc_long2']
            nameOfColumns = ['gas','x','x_lat','x_long', 'gasLeakLat','gasLeakLong','he', 'sigmx', 'sigmay', 'C','windSpeed','windBearing','weather']
            nameOfColumns.extend(list_c50)
            nameOfColumns.extend(list_idlh)
            nameOfColumns.extend(list_loc)

        else:
            nameOfColumns = ['gas','x', 'x_lat','x_long','gasLeakLat','gasLeakLong','he', 'sigmx', 'sigmay', 'C','windSpeed','windBearing','weather']
        concentrationAndDistanceDataFrame = pandas.DataFrame(columns=nameOfColumns)

        for values in gradualPlumeRise:
            observationPoint = values[0]   #distance in x direction
            plumeRise = values[1]  #plume height
            sigma_y, sigma_z = self.DispersionCoefficientPlume(observationPoint, stabilityClass, terrain)
            c = self.calcuateConcentration(sourceEmissionRate, windSpeedAtStackHeight, sigma_y, sigma_z, plumeRise,
                                           observationPoint, y, z)
            lat2, long2 = latLongUtil.endPointLatLong(gasLeakLat, gasLeakLong, observationPoint, windBearing)
            if (gas != None):
                c0 = self.calcuateConcentration(sourceEmissionRate, windSpeedAtStackHeight, sigma_y, sigma_z, plumeRise,
                                           observationPoint, 0, 0)
                y_c50,y_idlh,y_loc = gdmuf.calculateIsopleths(sigma_y, gas, c0,GasChemicalConstantsUtilityFunction.MICROG)
                #need to calculate the various lat long of isopleths
                y_lc501_lat, y_lc501_long = latLongUtil.endPointLatLong(lat2, long2, y_c50, windBearing + 90)
                y_lc502_lat, y_lc502_long = latLongUtil.endPointLatLong(lat2, long2, -y_c50, windBearing + 90)
                l1 = [y_c50,y_lc501_lat, y_lc501_long,y_lc502_lat, y_lc502_long]

                y_ldhl1_lat, y_ldhl1_long = latLongUtil.endPointLatLong(lat2, long2, y_idlh, windBearing + 90)
                y_ldhl2_lat, y_ldhl2_long = latLongUtil.endPointLatLong(lat2, long2, -y_idlh, windBearing + 90)
                l2 = [y_idlh,y_ldhl1_lat, y_ldhl1_long,y_ldhl2_lat, y_ldhl2_long]

                y_loc1_lat, y_loc1_long = latLongUtil.endPointLatLong(lat2, long2, y_loc, windBearing + 90)
                y_loc2_lat, y_loc2_long = latLongUtil.endPointLatLong(lat2, long2, -y_loc, windBearing + 90)
                l3 = [y_loc,y_loc1_lat, y_loc1_long,y_loc2_lat, y_loc2_long]

                #We will calculate the lat long for all the y values
                tupleValues = [gas,observationPoint,lat2,long2,gasLeakLat,gasLeakLong, plumeRise, sigma_y, sigma_z, math.floor(c),windVelocity,windBearing,weather]
                tupleValues.extend(l1)
                tupleValues.extend(l2)
                tupleValues.extend(l3)
            else:
                tupleValues = [gas,observationPoint,lat2,long2,gasLeakLat,gasLeakLong, plumeRise, sigma_y, sigma_z, math.floor(c),windVelocity,windBearing,weather]
            # print(tupleValues)
            # nameOfColumns = ['x', 'he', 'sigmx', 'sigmay', 'C']
            concentrationAndDistanceDataFrame = concentrationAndDistanceDataFrame.append(
                pandas.DataFrame([tupleValues], columns=nameOfColumns), ignore_index=True)
            startingPoint = observationPoint

        intervalOfObservations = 2*intervalOfObservations
        initialC = 0
        observationPoint = startingPoint
        #we align observation point with the nearest hundred.
        x = observationPoint % 100
        observationPoint = observationPoint + x
        lc50, ldhl, loc = GasChemicalConstantsUtilityFunction.getGasLethalConcentration(gas,
                                                                                        GasChemicalConstantsUtilityFunction.MICROG)
        stopingConcentration = 0.5 * loc
        for x in range(1,1000):

            observationPoint = observationPoint +  intervalOfObservations
            if (observationPoint >= 1000):
                intervalOfObservations = 200
            #print("observation point " + str(observationPoint))
            #if ((observationPoint >= 1000) & (observationPoint < 3000)):
            #    intervalOfObservations = 500
            #elif ((observationPoint >= 3000) & (observationPoint < 10000)):
            #    intervalOfObservations = 1000
            #elif (observationPoint >= 10000):
            #    intervalOfObservations = 10000

            sigma_y,sigma_z = self.DispersionCoefficientPlume(observationPoint, stabilityClass, terrain)
            c = self.calcuateConcentration(sourceEmissionRate,windSpeedAtStackHeight,sigma_y,sigma_z,plumeRisexf,observationPoint,y,z)
            lat2, long2 = latLongUtil.endPointLatLong(gasLeakLat, gasLeakLong, observationPoint, windBearing)
            if (gas != None):
                c0 = self.calcuateConcentration(sourceEmissionRate, windSpeedAtStackHeight, sigma_y, sigma_z, plumeRise,
                                           observationPoint, 0, 0)
                y_c50,y_idlh,y_loc = gdmuf.calculateIsopleths(sigma_y, gas, c0,GasChemicalConstantsUtilityFunction.MICROG)
                y_lc501_lat, y_lc501_long = latLongUtil.endPointLatLong(lat2, long2, y_c50, windBearing + 90)
                y_lc502_lat, y_lc502_long = latLongUtil.endPointLatLong(lat2, long2, -y_c50, windBearing + 90)
                l1 = [y_c50, y_lc501_lat, y_lc501_long, y_lc502_lat, y_lc502_long]

                y_ldhl1_lat, y_ldhl1_long = latLongUtil.endPointLatLong(lat2, long2, y_idlh, windBearing + 90)
                y_ldhl2_lat, y_ldhl2_long = latLongUtil.endPointLatLong(lat2, long2, -y_idlh, windBearing + 90)
                l2 = [y_idlh, y_ldhl1_lat, y_ldhl1_long, y_ldhl2_lat, y_ldhl2_long]

                y_loc1_lat, y_loc1_long = latLongUtil.endPointLatLong(lat2, long2, y_loc, windBearing + 90)
                y_loc2_lat, y_loc2_long = latLongUtil.endPointLatLong(lat2, long2, -y_loc, windBearing + 90)
                l3 = [y_loc, y_loc1_lat, y_loc1_long, y_loc2_lat, y_loc2_long]

                # We will calculate the lat long for all the y values
                tupleValues = [gas,observationPoint, lat2, long2,gasLeakLat,gasLeakLong, plumeRise, sigma_y, sigma_z, math.floor(c),windVelocity,windBearing,weather]
                tupleValues.extend(l1)
                tupleValues.extend(l2)
                tupleValues.extend(l3)
            else:
                tupleValues = [gas,observationPoint, lat2, long2,gasLeakLat,gasLeakLong, plumeRise, sigma_y, sigma_z, math.floor(c),windVelocity,windBearing,weather]

            concentrationAndDistanceDataFrame = concentrationAndDistanceDataFrame.append(pandas.DataFrame([tupleValues],columns=nameOfColumns),ignore_index=True)
            #print("c " + str(c) + " stoping " + str(stopingConcentration))
            if (x > 15) & (c < stopingConcentration):
                break

        return concentrationAndDistanceDataFrame

    def draw_circles(self,leakageLat, leakageLong, rad, col, pop, fill, map_name):
        folium.CircleMarker([leakageLat, leakageLong],
                        radius=rad,
                        color=col,
                        popup=pop,
                        fill_color=fill,
                       ).add_to(map_name)

#Public Interface
def predictGasDispersionLightGasPlume(gasExitTemprature, stackDiameter, stackHeight, exitGasSpeed, sourceEmissionRate,
                                      terrain, gas, gasLeakLat, gasLeakLong):
    model ="LightGasPlume"
    intervalOfObservations = 100  # m
    y = 0
    z = 2  # m height of human
    windRefHeight = WeatherInfo.windRefHeight()
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day \
        = WeatherInfo.weatherInfo(gasLeakLat,gasLeakLong)

    dispersionModel = ToxicLightGasDispersionPlumeModel()
    concentrationData = dispersionModel.calculateConcentrationForPlumeGas( cloudCoverage, windVelocity,windBearing,weather, day, terrain, gravity, windRefHeight,
                                      temprature, gasExitTemprature,
                                      intervalOfObservations, stackDiameter, stackHeight, exitGasSpeed,
                                      sourceEmissionRate, y, z,gas,gasLeakLat,gasLeakLong)
    concentrationData.to_csv("testOutComeLightGasPlume.csv")
    return model, concentrationData



def testCalculateGasDispersionModel():

    gasExitTemprature   = 350 #K
    stackDiameter       = 1 #m
    stackHeight         = 5 #m
    exitGasSpeed        = 4 #m/s
    sourceEmissionRate  = 2000 #kg/s
    day = False
    terrain = 'rural'
    windRefHeight = WeatherInfo.windRefHeight()
    intervalOfObservations = 100 #m
    y = 0
    z = 2 #m height of human
    gas = 'CH4'
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day = WeatherInfo.weatherInfo(gasLeakLat,gasLeakLong)

    dispersionModel = ToxicLightGasDispersionPlumeModel()
    concentrationData = dispersionModel.calculateConcentrationForPlumeGas( cloudCoverage, windVelocity,windBearing,weather, day, terrain, gravity, windRefHeight,
                                      temprature, gasExitTemprature,
                                      intervalOfObservations, stackDiameter, stackHeight, exitGasSpeed,
                                      sourceEmissionRate, y, z,gas,gasLeakLat,gasLeakLong)
    visual_on_maps.drawForLightPlume(concentrationData,15)
    print("Final outcome " + str(concentrationData.head(500)) )
    concentrationData.to_csv("testOutComeLightGasPlume.csv")


def main():
    #testCaseBhopal()
    testCalculateGasDispersionModel()




if __name__ == "__main__":
    main()






