from app.models.toxic_heavy_gas_dispersion.bmmCurveApproximation import bmmCurveApproximation
import pandas
import math
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
from app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
import app.models.toxic_heavy_gas_dispersion.latLongUtil as latLongUtil
import app.models.toxic_heavy_gas_dispersion.visual_on_maps as visual_on_maps
import app.models.toxic_heavy_gas_dispersion.airDispersionOutflowModels as airDispersionOutflowModels
#Algorithm is successfully applied when at a distance duration t(s) is greater than 2.5 x / wind_speed so that a steady
# state is reached.
class ToxicHeaveyGasDispersionPuffModel():
    #gasDensity = {'LP':500, 'CH4':0.717, 'CO':1.25, 'Cl':2.994}
    #gasDensity = {'LP': 500, 'CH4': 0.717, 'CO': 6.0, 'Cl': 2.994,'MIC':923}
    gasName = ''
    gas_density =  0
    air_density = 1.21
    wind_speed = 0
    initial_concentration = 0
    #source_radius = 0
    gravity = 9.81
    instantaneous_release = 0
    windBearing = 0
    weather = ''
    gasLeakLat = 0
    gasLeakLong = 0
    loc = 0
    ldhl = 0
    lc50 = 0
    envSenorLat = -1
    envSensorLong = -1
    concentrationCollectedFromEnvSensor = None
    concentrationThresold = GasChemicalConstantsUtilityFunction.concentrationThresoldRatio  #Creating an assumption as a thresold.
    nameOfColumns = ['gasName','ratio','yValue','cmax','x','t','b','bz','above_lc50','above_idlh','above_loc','windBearing',
                     'windVelocity','weather','gasLeakLat','gasLeakLong','envSensorLat','envSensorLong','x_lat','x_long']
    concentrationRatioPuff = [0.1, 0.05, 0.02, 0.01, 0.005, 0.002,0.001]

    def __init__(self,gasName,windSpeed,windBearing,weather,initial_concentration, source_radius,instantaneous_release,gravity,
                 airDensity,gasLeakLat,gasLeakLong):
        self.gasName = gasName
        self.gas_density = GasChemicalConstantsUtilityFunction.getGasDensity(gasName)
        self.wind_speed = windSpeed
        self.initial_concentration = initial_concentration
        self.source_radius = source_radius
        self.instantaneous_release = instantaneous_release
        self.gravity = gravity
        self.air_density = airDensity
        self.windBearing = windBearing
        self.weather = weather
        self.gasLeakLat = gasLeakLat
        self.gasLeakLong = gasLeakLong
        self.lc50,self.ldhl,self.loc = GasChemicalConstantsUtilityFunction.getGasLethalConcentration(gasName,GasChemicalConstantsUtilityFunction.KG)

    def initializeDataForEnvironmentCensor(self,envSensorLat,envSensorLong):
        self.envSenorLat = envSensorLat
        self.envSensorLong = envSensorLong
        self.concentrationCollectedFromEnvSensor = True

    def resetDataForDispersionCalculation(self,instantaneousRelease,initialRadius):
        self.instantaneous_release = instantaneousRelease
        self.source_radius = initialRadius

    def constructConcentrationAndSizeOfPluff(self):
        #Test if this model can be applied
        g0 = self.calculate_acceleration_g0()
        canModelApply = self.canWeApplyBoxModel(self.instantaneous_release,g0,self.wind_speed)
        if (canModelApply == False):
            return "Model Can not be applied"
        xRatio = self.calculateXRatio(g0)
        #print("xRatio " + str(xRatio))
        concentrationAndSizeDataFrame = pandas.DataFrame(columns=self.nameOfColumns)

        bmCA = bmmCurveApproximation()
        for concentrationRatio in self.concentrationRatioPuff:
            y =  bmCA.getBMModelCurveApproxForPuffs(concentrationRatio,xRatio)
            cmax = concentrationRatio * self.initial_concentration
            x = y*(self.instantaneous_release**(1/3))
            t,b = self.calculateWidthAndTimeOfPluff(x,g0)
            bz = self.calculateDispersionHeight(b,concentrationRatio)
            if (self.concentrationCollectedFromEnvSensor == True):
                if (concentrationRatio == self.concentrationThresold):
            #We need to estimate gas leak position first.
                    self.gasLeakLat, self.gasLeakLong = latLongUtil.endPointLatLong(self.envSenorLat, self.envSensorLong, -x, self.windBearing)
            lat2, long2 = latLongUtil.endPointLatLong(self.gasLeakLat, self.gasLeakLong, x, self.windBearing)
            #'windBearing','windVelocity','gasLeakLat','gasLeakLong','lat2','long2'
            #Concentration in kg/m3
            above_lc50 = (cmax > self.lc50)
            above_idlh = (cmax > self.ldhl)
            above_loc = (cmax > self.loc)
            tupleValues  = [self.gasName,concentrationRatio,y,cmax,x,t,b,bz,above_lc50,above_idlh,above_loc,self.windBearing,self.wind_speed,
                            self.weather,self.gasLeakLat,self.gasLeakLong,self.envSenorLat,self.envSensorLong,lat2,long2]
            #print(tupleValues)
            concentrationAndSizeDataFrame = concentrationAndSizeDataFrame.append(pandas.DataFrame([tupleValues],columns=self.nameOfColumns),ignore_index=True)
        return concentrationAndSizeDataFrame


    #Calculate correction to acceleration due to gravity
    def calculate_acceleration_g0(self):
        #g0 = g(gas_density - air_density)/air_density
        g0 = self.gravity* ((self.gas_density - self.air_density) / self.air_density)
        #print("g0 " + str(g0) + " gas_density " + str(self.gas_density))
        return g0

    def calculateXRatio(self,g0):
        x = (((g0 * (self.instantaneous_release**(1/3)))) / (self.wind_speed**2))**(1/2)
        return x

    def calculateWidthAndTimeOfPluff(self,x,g0):

        #time = (x-plumeWidth)/0.4*self.wind_speed
        #plumeWidthSqr = (self.source_radius**2) + 1.2*time*((g0*self.instanttaneous_release)**1/2)
        #To solve this we convert it in a quadratic equation for b. Let calculate some constants first.
        z = (g0*self.instantaneous_release)**(1/2)
        a = self.wind_speed
        b = 3 * z
        c = -((self.wind_speed * pow(self.source_radius,2)) + (3*x*z))
        #now we can solve it for b
        discRoot = math.sqrt((b * b) - 4 * a * c)  # first pass
        root1 = (-b + discRoot) / (2 * a)  # solving positive
        root2 = (-b - discRoot) / (2 * a)  # solving negative
        plumeWidth = root1
        time = (x-plumeWidth)/(0.4*self.wind_speed)
        return time,plumeWidth

    def calculateDispersionHeight(self,dispersionWidth,concentrationRatio):
        return  self.instantaneous_release/ ((math.pi * pow(dispersionWidth,2))*concentrationRatio)

    #Test if the Box model can be applied to this data set.
    def canWeApplyBoxModel(self,initial_volumeOfReleaseGas,g0,windVelocity):
        characteristicSourceDimension = pow(initial_volumeOfReleaseGas,1/3)
        instanteousReleaseCriteria = pow((pow((g0*initial_volumeOfReleaseGas),1/2)/(windVelocity*characteristicSourceDimension)),1/3)
        #print("InstantneousReleaseCriteria " + str(instanteousReleaseCriteria))
        return (instanteousReleaseCriteria >= 0.20)

#Public Interface1
def predictGasDispersionForHeavyGasPuffUseCaseEnvSensor(gasName,initialConcentrationAtLeakPoint,envSensorLat,envSensorLong,pWindBearing=None,pWindSpeed=None):
    #First we will estimate the volume of vessel.
    modelName = "HeavyGasPuffEnvSensor"
    winfo = WeatherInfo()
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()

    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage, day, hour = winfo.weatherInfo(envSensorLat,envSensorLong)

    if (pWindBearing != None):
        windBearing = pWindBearing
    if (pWindSpeed != None):
        windVelocity = pWindSpeed

    type, finalRadius75, finalVolume75, finalRadius25, finalVolume25 = \
        airDispersionOutflowModels.enumerateAllPossibleValuesforSetOfGivenToxicLiquifiedGasVolumes(gasName, windVelocity)

    dispersionModel = ToxicHeaveyGasDispersionPuffModel(gasName, windVelocity, windBearing, weather,
                                                        initialConcentrationAtLeakPoint
                                                        , finalRadius75, finalVolume75, gravity,
                                                        airDensity, -1, -1)
    dispersionModel.initializeDataForEnvironmentCensor(envSensorLat,envSensorLong)
    dataSet_75 = dispersionModel.constructConcentrationAndSizeOfPluff()
    #Reset the initialization parameters with new concentration values.
    dispersionModel.resetDataForDispersionCalculation(finalVolume25,finalRadius25)
    dataSet_25 = dispersionModel.constructConcentrationAndSizeOfPluff()
    output = []
    output.append(modelName)
    output.append(dataSet_75)
    output.append(dataSet_25)
    #return modelName,dataSet_75,dataSet_25
    return output
#Public Interface 1.5
def predictGasDispersionForHeavyGasPuffUseCaseEnvSensorNoGasLeakPointEstimation(gasName,initialConcentrationAtLeakPoint
                                                                                ,gasLeakLat,gasLeakLong):
    #First we will estimate the volume of vessel.
    modelName = "HeavyGasPuffEnvSensor"
    winfo = WeatherInfo()

    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()

    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage, day, hour = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)
    type, finalRadius75, finalVolume75, finalRadius25, finalVolume25 = \
        airDispersionOutflowModels.enumerateAllPossibleValuesforSetOfGivenToxicLiquifiedGasVolumes(gasName, windVelocity)

    dispersionModel = ToxicHeaveyGasDispersionPuffModel(gasName, windVelocity, windBearing, weather,
                                                        initialConcentrationAtLeakPoint
                                                        , finalRadius75, finalVolume75, gravity,
                                                        airDensity, gasLeakLat,gasLeakLong)
    dataSet_75 = dispersionModel.constructConcentrationAndSizeOfPluff()
    #Reset the initialization parameters with new concentration values.
    dispersionModel.resetDataForDispersionCalculation(finalVolume25,finalRadius25)
    dataSet_25 = dispersionModel.constructConcentrationAndSizeOfPluff()

    return modelName,dataSet_75,dataSet_25

#public interface 2
def predictGasDispersionForHeavyGasPuff(gasName,initial_concentration,source_radius,instantaneous_release,gasLeakLat,gasLeakLong):

    winfo = WeatherInfo()
    moduleName = "HeavyGasPuff"
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()

    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,day,hour = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)

    dispersionModel = ToxicHeaveyGasDispersionPuffModel(gasName, windVelocity,windBearing,weather, initial_concentration
                                                        , source_radius, instantaneous_release,gravity,
                 airDensity,gasLeakLat,gasLeakLong)
    dataSet = dispersionModel.constructConcentrationAndSizeOfPluff()
    return moduleName, dataSet


def testCase2():
    winfo = WeatherInfo()
    gasName = 'LPG'
    print(gasName)
#    windSpeed = 4  # 4 m/s
    initial_concentration = 100  # 6 kg/m3
    #dispersion_volume = 1  # 1 m3/s
    source_radius = 2  # 2m
    instantaneous_release = 1000  # m3
    gravity = GasChemicalConstantsUtilityFunction.getGravity()
    airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,day,hour = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)

    dispersionModel = ToxicHeaveyGasDispersionPuffModel(gasName, windVelocity,windBearing,weather, initial_concentration
                                                        , source_radius, instantaneous_release,gravity,
                 airDensity,gasLeakLat,gasLeakLong)
    dataSet = dispersionModel.constructConcentrationAndSizeOfPluff()
    dataSet.to_csv("concentrationDataPuffModel.csv")
    map_osm = visual_on_maps.drawForHeavyPuff(dataSet,initial_concentration,15)
    print(dataSet.head(10))

def testpredictGasDispersionForHeavyGasPuffUseCaseEnvCensor():
    gasName = 'LPG'
    concentrationAtEnvSensor = 6  # 6 kg/m3
    envSensorLat = 19.43000031
    envSensorLong = -99.09999847

    modelName,dataSet75, dataSet25 = predictGasDispersionForHeavyGasPuffUseCaseEnvSensor(gasName, concentrationAtEnvSensor, envSensorLat,
                                                                  envSensorLong)
    data = pandas.DataFrame(dataSet75)
    data = data.append(dataSet25)
    print(data.head(15))
    map_osm = visual_on_maps.drawForHeavyPuff(dataSet75, concentrationAtEnvSensor/0.1, 15)
    map_osm = visual_on_maps.drawForHeavyPuff(dataSet75, concentrationAtEnvSensor / 0.1, 15,map_osm)
    map_osm

    data.to_csv("experimentalHeavyGasLeak.csv")
    return map_osm

def main():
    testpredictGasDispersionForHeavyGasPuffUseCaseEnvCensor()
    #testCase2()
    #testCaseBhopal()


if __name__ == "__main__":
    main()
