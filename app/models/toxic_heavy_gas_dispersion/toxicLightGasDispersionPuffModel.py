from numpy import *
from pandas import *
import math
import app.models.toxic_heavy_gas_dispersion.toxicLightGasDispersionPuffHeightRise as heightRisePuff
import app.models.toxic_heavy_gas_dispersion.gasDispersionModelingUtilityFunctions as utilityFunction
import config
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
from  app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
import app.models.toxic_heavy_gas_dispersion.latLongUtil as latLongUtil
import app.models.toxic_heavy_gas_dispersion.visual_on_maps as visual_on_maps
#Algorithm is successfully applied when at a distance duration t(s) is greater than 2.5 x / wind_speed so that a steady
# state is reached.
class ToxicLightGasDispersionPuffModel():
    #gasDensity = {'LP':500, 'CH4':0.717, 'CO':1.25, 'Cl':2.994}
    #nameOfColumns = ['gas','x','x_lat','x_long', 'gasLeakLat','gasLeakLong','he', 'y','z','sigmx', 'sigmaz','zb','zt','puffRadius','meanWindSpeed','weather','tin','tout','tpeak']

    def round(self,value):
        return config.customRounding(value)

    def puffLowerAndUpperPart(self,puffMaxHeight,sigm_z):
        constant_b = puffMaxHeight - 2.15 * sigm_z
        constant_t = puffMaxHeight + 2.15 * sigm_z

        zb = 2
        if (constant_b > 2):
            zb = constant_b

        zt = puffMaxHeight
        if (constant_t < puffMaxHeight):
            zt = constant_t
        #calculate Radius of puff
        puffRadius = (zt-zb)/2
        return self.round(zb),self.round(zt),self.round(puffRadius)

    def calculateMeanWindSpeed(self,windRefSpeed,windRefHeight,puffMaxHeight,windProfile,sigm_z):
        #Calculate zb values
        zb,zt,puffRadius = self.puffLowerAndUpperPart( puffMaxHeight, sigm_z)

        meanWindSpeed = windRefSpeed * (pow(zt,1+windProfile) -
                        pow(zb,1+windProfile))/ ((zt-zb)*(1+ windProfile)*pow(windRefHeight,windProfile))
        return zb,zt,puffRadius,self.round(meanWindSpeed)

    def calculatePuffInandOutTime(self,observationPoint,windMeanSpeed,sigma_x):

        t_in     = (observationPoint-(2.45*sigma_x))/ windMeanSpeed
        t_out    = (observationPoint+(2.45*sigma_x))/ windMeanSpeed
        t_peak  =   observationPoint / windMeanSpeed
        return self.round(t_in),self.round(t_out),self.round(t_peak)

    def DispersionCoefficientPuff(self,x, stable_class):
        # assign transverse and vertical dispersion coefficients (standard terrain)

        if stable_class == 'A':
            sigma_y = 0.18*pow(x,0.92)
            sigma_z = 0.60*pow(x,0.76)
        elif stable_class == 'B':
            sigma_y = 0.14 * pow(x, 0.92)
            sigma_z = 0.53 * pow(x, 0.73)
        elif stable_class == 'C':
            sigma_y = 0.10 * pow(x, 0.92)
            sigma_z = 0.34 * pow(x, 0.72)
        elif stable_class == 'D':
            sigma_y = 0.06 * pow(x, 0.92)
            sigma_z = 0.15 * pow(x, 0.70)
        elif stable_class == 'E':
            sigma_y = 0.04 * pow(x, 0.91)
            sigma_z = 0.10 * pow(x, 0.67)
        else:
            sigma_y = 0.03 * pow(x, 0.90)
            sigma_z = 0.05 * pow(x, 0.64)

        return self.round(sigma_y), self.round(sigma_z)
    #method to calculate concentration at a given point in given time.
    def calcuateConcentration(self,totalGassMass,meanWindSpeed,sigma_x,sigma_y,sigma_z,plumeRise,x,y,z,t):

        c1 = (2*totalGassMass*10**9)/(pow((2*math.pi),3/2)*sigma_x*sigma_y*sigma_z)
        #+ math.exp(-(pow((plumeRise+z),2)/(2*pow(sigma_z,2))))

        c2 = math.exp(-(pow((x-meanWindSpeed*t),2)/(2*pow(sigma_x,2))))
        c3 = math.exp(-((y**2)/2*pow(sigma_y,2)))
        c4 = math.exp(-(pow((plumeRise-z),2)/(2*pow(sigma_z,2))))
        c5 = math.exp(-(pow((plumeRise+z),2)/(2*pow(sigma_z,2))))
        c = c1*c2*c3*(c4+c5)
        return self.round(c)
    #helper function
    def createColumnNameStr(self,val,gas,prefix):
        suffix = val
        if val == -1:
            suffix = 'peak'
        elif val == -2:
            suffix = 'in'
        elif val == -3:
            suffix = 'out'
        columnName = str(prefix) + str(suffix)

        return  columnName




    def helperCalculateConcentrationForPuffGas(self,stabilityClass,totalGassMass,  plumeRise, windVelocity,windBearing,weather, windRefHeight,
                                               windProfile,observationPoint,y,z,concentrationAndDistanceDataFrame,
                                               timeList,gas,gasLeakLat,gasLeakLong,expandedColumn):

        sigma_y, sigma_z = self.DispersionCoefficientPuff(observationPoint, stabilityClass)
        sigma_x = sigma_y
        zb, zt, puffRadius,meanWindSpeed = self.calculateMeanWindSpeed(windVelocity, windRefHeight, plumeRise, windProfile, sigma_z)
        t_in, t_out, t_peak = self.calculatePuffInandOutTime(observationPoint, meanWindSpeed, sigma_x)
        #Lat long corresponding observation points
        lat2,long2 = latLongUtil.endPointLatLong(gasLeakLat, gasLeakLong, observationPoint, windBearing)

        # we need to generate concentration for different time frame
        concentrationList = []
        refConcentrationFlag = False
        refConcentration = 0
        for i, val in enumerate(timeList):
            t = val
            if (val == -1):
                t = t_peak
                refConcentrationFlag = True
            elif (val == -1):
                t = t_in
                refConcentrationFlag = True
            elif (val == -2):
                t = t_out
                refConcentrationFlag = True

            c = self.calcuateConcentration(totalGassMass,meanWindSpeed,sigma_x,sigma_y,sigma_z,plumeRise,observationPoint,y,z,t)
            concentrationList.append(c)
            if (refConcentrationFlag):
                refConcentration = c
                refConcentrationFlag = False
            if (gas != None):
                c_x_0_0_t = self.calcuateConcentration(totalGassMass,meanWindSpeed,sigma_x,sigma_y,sigma_z,plumeRise,observationPoint,0,0,t)
                y_lc50, y_ldhl, y_loc = utilityFunction.calculateIsopleths(sigma_y,gas,c_x_0_0_t,GasChemicalConstantsUtilityFunction.MICROG)
                #We will be calculating the corresponding isopleath lat long
                y_lc501_lat, y_lc501_long = latLongUtil.endPointLatLong(lat2, long2, y_lc50, windBearing + 90)
                y_lc502_lat, y_lc502_long = latLongUtil.endPointLatLong(lat2, long2, -y_lc50, windBearing + 90)

                y_ldhl1_lat, y_ldhl1_long = latLongUtil.endPointLatLong(lat2, long2, y_ldhl, windBearing + 90)
                y_ldhl2_lat, y_ldhl2_long = latLongUtil.endPointLatLong(lat2, long2, -y_ldhl, windBearing + 90)

                y_loc1_lat, y_loc1_long = latLongUtil.endPointLatLong(lat2, long2, y_loc, windBearing + 90)
                y_loc2_lat, y_loc2_long = latLongUtil.endPointLatLong(lat2, long2, -y_loc, windBearing + 90)

                concentrationList.extend([y_lc50,y_lc501_lat, y_lc501_long,y_lc502_lat, y_lc502_long, y_ldhl,
                                          y_ldhl1_lat, y_ldhl1_long,y_ldhl2_lat, y_ldhl2_long, y_loc,y_loc1_lat, y_loc1_long,y_loc2_lat, y_loc2_long])

        tupleValues = [gas,observationPoint,lat2,long2,gasLeakLat,gasLeakLong, plumeRise, y,z,sigma_y, sigma_z,zb, zt,puffRadius, meanWindSpeed,weather,t_in, t_out, t_peak] \
                      + concentrationList

        #  nameOfColumns = ['x', 'he','y','z', 'sigmx', 'sigmaz','zb','zt','meanWindSpeed','tin','tout','tpeak']
        concentrationAndDistanceDataFrame = concentrationAndDistanceDataFrame.append(
            pandas.DataFrame([tupleValues], columns=expandedColumn), ignore_index=True)
        return concentrationAndDistanceDataFrame,refConcentration

     #y lateral dispersion, Z height
    def calculateConcentrationForPuffGas(self,stackHeight,cloudCoverage, day, gravity, airDensity, TotalGasMassInPuff, puffInitialRadius,
                          intervalOfObservations, windVelocity,windBearing,weather, windRefHeight,ambientTemprature, tempratureOfReleaseGas,terrain,y,z,
                                         timeList, coeff, gas,gasLeakLat,gasLeakLong):
        print("windVelocity " + str(windVelocity) + " cloudCoverage " + str(cloudCoverage) + " day " + str(day))
        stabilityClass = utilityFunction.getAtmospericStabilityClass(windVelocity, cloudCoverage, day)
        windProfile = utilityFunction.getWindProfileExponent(stabilityClass, terrain)
        print("Windprofile - " + str(windProfile))

        gradualPuffRise, puffHeight = heightRisePuff.calculatePuffRise(stackHeight, cloudCoverage, day, gravity, airDensity,
                        TotalGasMassInPuff, puffInitialRadius,intervalOfObservations, windVelocity, ambientTemprature,
                        tempratureOfReleaseGas, windRefHeight, terrain, coeff)
        expandedColumn = ['gas','x','x_lat','x_long', 'gasLeakLat','gasLeakLong','he', 'y','z','sigmx', 'sigmaz','zb','zt','puffRadius','meanWindSpeed','weather','tin','tout','tpeak']
        #Add columns to the list of columns for all given time specific concentration.
        #print(timeList)
        #print(expandedColumn)
        for i, val in enumerate(timeList):
            columnName = self.createColumnNameStr(val,gas,'C')
            expandedColumn.append(columnName)
            if (gas != None):
                columnName = self.createColumnNameStr(val, gas, 'y_c50_')
                expandedColumn.append(columnName)
                expandedColumn.extend([columnName+'_lat1',columnName+'_long1', columnName+'_lat2',columnName+'_long2'])
                columnName = self.createColumnNameStr(val, gas, 'y_idlh_')
                expandedColumn.append(columnName)
                expandedColumn.extend(
                    [columnName + '_lat1', columnName + '_long1' ,columnName + '_lat2', columnName + '_long2'])

                columnName = self.createColumnNameStr(val, gas, 'y_loc_')
                expandedColumn.append(columnName)
                expandedColumn.extend(
                    [columnName + '_lat1', columnName + '_long1' , columnName + '_lat2', columnName + '_long2'])
        print("number of columns " + str(len(expandedColumn)))
        concentrationAndDistanceDataFrame = pandas.DataFrame(columns=expandedColumn)
        print("gradual puff rise " + str(gradualPuffRise) + "final pluff rise " + str(puffHeight))
        startingPoint = 0
        for values in gradualPuffRise:
            observationPoint = values[0]   #distance in x direction
            plumeRise = values[1]  #plume height
            concentrationAndDistanceDataFrame,refConcentration = self.helperCalculateConcentrationForPuffGas(stabilityClass, TotalGasMassInPuff,
                                                    plumeRise, windVelocity,windBearing,weather,windRefHeight,windProfile,  observationPoint, y, z,
                                                   concentrationAndDistanceDataFrame, timeList,gas,gasLeakLat,gasLeakLong,expandedColumn)
            startingPoint = observationPoint

        intervalOfObservations = 2*intervalOfObservations
        initialC = 0
        observationPoint = startingPoint
        #we align observation point with the nearest hundred.
        x = observationPoint % 100
        observationPoint = observationPoint + x
        lc50, ldhl, loc = GasChemicalConstantsUtilityFunction.getGasLethalConcentration(gas,GasChemicalConstantsUtilityFunction.MICROG)
        stopingConcentration = 0.8 * loc
        for x in range(1,1000):

            observationPoint = observationPoint +  intervalOfObservations
            concentrationAndDistanceDataFrame,refConcentration = self.helperCalculateConcentrationForPuffGas(stabilityClass,
                                                                                            TotalGasMassInPuff,
                                                                                            plumeRise, windVelocity,windBearing,weather,
                                                                                            windRefHeight, windProfile,
                                                                                            observationPoint,
                                                                                            y, z,
                                                                                            concentrationAndDistanceDataFrame,
                                                                                            timeList,gas,gasLeakLat,gasLeakLong,expandedColumn)
            #print("refConcentration " + str(refConcentration) + " stopping concentration " + str(stopingConcentration))
            if (x > 15) & (refConcentration < stopingConcentration):
                #if we reach a concentration is too low let us break.
                break

        return concentrationAndDistanceDataFrame


def calculateGasDispersionModelForLightGasPuff(stackHeight, cloudCoverage, day, gravity, airDensity, TotalGasMassInPuff,
                                     puffInitialRadius,
                                     intervalOfObservations, windVelocity,windBearing,weather, windRefHeight, temprature,
                                     tempratureOfReleaseGas, terrain, y, z,timeList, coeff,gas,gasLeakLat,gasLeakLong,zoom):


    dispersionModel = ToxicLightGasDispersionPuffModel()


    concentrationData = dispersionModel.calculateConcentrationForPuffGas(stackHeight, cloudCoverage, day, gravity, airDensity,
                                    TotalGasMassInPuff,
                                     puffInitialRadius,
                                     intervalOfObservations, windVelocity,windBearing,weather, windRefHeight, temprature,
                                     tempratureOfReleaseGas, terrain, y, z,timeList, coeff,gas,gasLeakLat,gasLeakLong)

    #print("Final outcome " + str(concentrationData.head(500)) )
    concentrationData.to_csv("testOutComePuffmodelLightGases.csv")
    map = visual_on_maps.drawForLightPuff(concentrationData,zoom)
    return map,concentrationData

#Public Interface
def predictGasDispersionLightGasPuff(tempratureOfReleaseGas, stackHeight, terrain, windRefHeight,
                          gas, puffInitialRadius, TotalGasMassInPuff, timeList, gasLeakLat, gasLeakLong):
    model = "LightGasPuff"
    intervalOfObservations = 200  # m
    coeff = 0.64
    y = 0
    z = 2  # m height of human
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day = WeatherInfo.weatherInfo(
        gasLeakLat, gasLeakLong)

    dispersionModel = ToxicLightGasDispersionPuffModel()


    concentrationData = dispersionModel.calculateConcentrationForPuffGas(stackHeight, cloudCoverage, day, gravity, airDensity,
                                    TotalGasMassInPuff,
                                     puffInitialRadius,
                                     intervalOfObservations, windVelocity,windBearing,weather, windRefHeight, temprature,
                                     tempratureOfReleaseGas, terrain, y, z,timeList, coeff,gas,gasLeakLat,gasLeakLong)

    concentrationData.to_csv("testOutComePuffmodelLightGases.csv")
    return model, concentrationData


def testCalculateGasDispersionModel():

    tempratureOfReleaseGas = 420  # K
    stackDiameter = 1  # m
    stackHeight = 2  # m
    day = True
    terrain = 'rural'
    windRefHeight = 10  # m

    intervalOfObservations = 200  # m
    coeff = 0.64
    y = 0
    gas = 'Cl2'
    z = 2 #m height of human
    puffInitialRadius = 1
    TotalGasMassInPuff = 500
    timeList = [-1, 60, 240]
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847

    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day = WeatherInfo.weatherInfo(
        gasLeakLat, gasLeakLong)

    dispersionModel = ToxicLightGasDispersionPuffModel()


    concentrationData = dispersionModel.calculateConcentrationForPuffGas(stackHeight, cloudCoverage, day, gravity, airDensity,
                                    TotalGasMassInPuff,
                                     puffInitialRadius,
                                     intervalOfObservations, windVelocity,windBearing,weather, windRefHeight, temprature,
                                     tempratureOfReleaseGas, terrain, y, z,timeList, coeff,gas,gasLeakLat,gasLeakLong)

    print("Final outcome " + str(concentrationData.head(500)) )
    concentrationData.to_csv("testOutComePuffmodelLightGases.csv")
    map = visual_on_maps.drawForLightPuff(concentrationData,15)
    #draw the graphics.
    visual_on_maps.distance_conc('x', 'Cpeak', "light", "puff", concentrationData, "distance (m)")
    map



def main():
    testCalculateGasDispersionModel()




if __name__ == "__main__":
    main()






