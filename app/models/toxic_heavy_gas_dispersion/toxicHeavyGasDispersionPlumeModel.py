import pandas
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
from app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
import app.models.toxic_heavy_gas_dispersion.latLongUtil as latLongUtil
import app.models.toxic_heavy_gas_dispersion.visual_on_maps as visual_on_maps
import app.models.toxic_heavy_gas_dispersion.airDispersionOutflowModels as airDispersionOutflowModels
from app.models.toxic_heavy_gas_dispersion.bmmCurveApproximation import bmmCurveApproximation

#Algorithm is successfully applied when at a distance duration t(s) is greater than 2.5 x / wind_speed so that a steady
# state is reached.
class ToxicHeaveyGasDispersionPlumeModel():
    #gasDensity = {'LP':500, 'CH4':0.717, 'CO':1.25, 'Cl':2.994}
    #gasDensity = {'LP': 500, 'CH4': 0.717, 'CO': 6.0, 'Cl': 2.994,'MIC':923}
    gasName =''
    gas_density =  0
    air_density = 1.21
    wind_speed = 0
    initial_concentration = 0
    dispersion_volume = 0
    source_radius = 0
    gravity = 9.81
    windBearing = 0
    weather = ''
    gasLeakLat = 0
    gasLeakLong = 0
    envSensorLat = 0
    envSensorLong = 0
    concentrationCollectedFromEnvSensor = None
    loc = 0
    ldhl = 0
    lc50 = 0
    nameOfColumns = ['gasName','ratio','yValue','cmax','x','b','bz','above_lc50','above_idlh','above_loc','windBearing',
                     'windVelocity','weather','gasLeakLat','gasLeakLong','envSensorLat','envSensorLong','x_lat','x_long','y1_lat','y1_long','y2_lat','y2_long']
    concentrationRatioPlume = [0.1,0.05,0.02,0.01,0.005,0.002]

    def __init__(self,gasName,windSpeed,windBearing,weather,initial_concentration,dispersion_volume, source_radius,gasLeakLat,gasLeakLong):
        self.gasName = gasName
        self.gas_density = GasChemicalConstantsUtilityFunction.getGasDensity(gasName)
        self.wind_speed = windSpeed
        self.dispersion_volume = dispersion_volume
        self.initial_concentration = initial_concentration
        self.source_radius = source_radius
        self.gravity = GasChemicalConstantsUtilityFunction.getGravity()
        self.air_density = GasChemicalConstantsUtilityFunction.getAirDensity()
        self.windBearing = windBearing
        self.gasLeakLat = gasLeakLat
        self.gasLeakLong = gasLeakLong
        self.weather = weather
        self.lc50, self.ldhl, self.loc = GasChemicalConstantsUtilityFunction.getGasLethalConcentration(gasName,
                                                                                                       GasChemicalConstantsUtilityFunction.KG)

    def initializeDataForEnvSensor(self,envLat,envLong):
        self.envSensorLat = envLat
        self.envSensorLong = envLong
        self.concentrationCollectedFromEnvSensor = True

    def constructConcentraitonAndSizeOfPlume(self):
        g0 = self.calculate_acceleration_g0()
        xRatio = self.calculateXRatio(g0)
        print("xRatio " + str(xRatio))
        lb = self.calculateLb(g0)
        yDenominator = pow((self.dispersion_volume/self.wind_speed),1/2)
        concentrationAndSizeDataFrame = pandas.DataFrame(columns=self.nameOfColumns)

        bmCA = bmmCurveApproximation()
        for concentrationRatio in self.concentrationRatioPlume:
            y =  bmCA.getBMModelCurveApproxForPlumes(concentrationRatio,xRatio)
            cmax = concentrationRatio * self.initial_concentration
            x = y*yDenominator
            b = self.calculateWidthOfPlume(x,lb)
            bz = self.calculateDispersionHeight(b)
            if (self.concentrationCollectedFromEnvSensor == True):
                if (concentrationRatio == GasChemicalConstantsUtilityFunction.concentrationThresoldRatio):
                    print("Calculating las long at leak point")
            #We need to estimate gas leak position first.
                    self.gasLeakLat, self.gasLeakLong = latLongUtil.endPointLatLong(self.envSensorLat, self.envSensorLong, -x, self.windBearing)
            #Calculate the end latlong.
            #x is in m
            lat2, long2 = latLongUtil.endPointLatLong(self.gasLeakLat, self.gasLeakLong, x, self.windBearing)
            #We need to get the lat and long for cross wind directions.
            #print(lat2,long2,b)
            y1_lat, y1_long = latLongUtil.endPointLatLong(lat2, long2, b, self.windBearing + 90)
            y2_lat, y2_long = latLongUtil.endPointLatLong(lat2, long2, -b, self.windBearing + 90)
            above_lc50 = (cmax > self.lc50)
            above_idlh = (cmax > self.ldhl)
            above_loc = (cmax > self.loc)
            tupleValues  = [self.gasName,concentrationRatio,y,cmax,x,b,bz,above_lc50,above_idlh,above_loc,self.windBearing,
                            self.wind_speed,self.weather,self.gasLeakLat,self.gasLeakLong,self.envSensorLat,self.envSensorLong,
                            lat2,long2,y1_lat,y1_long,y2_lat,y2_long]
            #print(tupleValues)
            #Concentration values in kg/m3
            concentrationAndSizeDataFrame = concentrationAndSizeDataFrame.append(pandas.DataFrame([tupleValues],columns=self.nameOfColumns),ignore_index=True)
        return concentrationAndSizeDataFrame


    #Calculate correction to acceleration due to gravity
    def calculate_acceleration_g0(self):
        #g0 = g(gas_density - air_density)/air_density
        g0 = self.gravity* ((self.gas_density - self.air_density) / self.air_density)
        #print("g0 " + str(g0) + " gas_density " + str(self.gas_density))
        return g0

    def calculateXRatio(self,g0):
        x = (((g0**2) * self.dispersion_volume) / self.wind_speed**5)**(1/5)
        return x

    def calculateLb(self,g0):
        print("calculateLB")
        print(g0,self.dispersion_volume,self.wind_speed)
        return (g0 * self.dispersion_volume) / pow(self.wind_speed,3)

    def calculateWidthOfPlume(self,x, lb):
        print("calculateWidthOfPlume")
        print(self.source_radius,lb,x)
        plumeWidth = 2 * self.source_radius + 8 * lb + 2.5 * pow(lb,(1/3)) * pow(x, (2/3))
        return plumeWidth

    def calculateDispersionHeight(self,dispersionWidth):
        return self.dispersion_volume / (2 * self.wind_speed * dispersionWidth)


    def dispersionBehindTheSource(self,lb):
        return self.source_radius + 2 * lb

# Public Interface 1.

def predictGasDispersionHeaveyGasPlumeUseCaseEnvSensor(gasName,initialConcentrationAtLeakPoint,envSensorLat,envSensorLong
                                                       ,pWindBearing=None,pWindSpeed=None):
    model = "toxicHeavyPlumeEnvSensor"
    winfo = WeatherInfo()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage, hour, day = winfo.weatherInfo(
        envSensorLat, envSensorLong)

    if (pWindBearing != None):
        windBearing = pWindBearing
    if (pWindSpeed != None):
        windVelocity = pWindSpeed

    #We will estimate the dispersion Volume, Source Radius
    type, maxoutflow, corespondingRadius= airDispersionOutflowModels.enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName)
    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windVelocity, windBearing, weather,
                                                         initialConcentrationAtLeakPoint
                                                         , maxoutflow, corespondingRadius, -1,
                                                         -1)
    dispersionModel.initializeDataForEnvSensor(envSensorLat,envSensorLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    #dataSet.to_csv("plumeconcentrationheaveyGas1.csv")
    output=[]
    output.append(model)
    output.append(dataSet)
    #return model, dataSet

    return output

# Public Interface 1.5
def predictGasDispersionHeaveyGasPlumeUseCaseEnvSensorNoGasLeakPointEstimation(gasName,initialConcentrationAtLeakPoint,
                                                                               gasLeakLat, gasLeakLong):
    model = "toxicHeavyPlumeEnvSensor"
    winfo = WeatherInfo()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage, hour, day = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)
    #We will estimate the dispersion Volume, Source Radius
    type, maxoutflow, corespondingRadius= airDispersionOutflowModels.enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName)
    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windVelocity, windBearing, weather,
                                                         initialConcentrationAtLeakPoint
                                                         , maxoutflow, corespondingRadius, gasLeakLat,gasLeakLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    #dataSet.to_csv("plumeconcentrationheaveyGas1.csv")
    return model, dataSet
"""
def predictGasDispersionHeaveyGasPlumeUseCaseEnvSensor(gasName,initialConcentrationAtLeakPoint,envSensorLat,envSensorLong):
    model = "toxicHeavyPlumeEnvSensor"
    winfo = WeatherInfo()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage, hour, day = winfo.weatherInfo(
        envSensorLat, envSensorLong)
    #We will estimate the dispersion Volume, Source Radius
    type, maxoutflow, corespondingRadius= airDispersionOutflowModels.enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName)
    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windVelocity, windBearing, weather,
                                                         initialConcentrationAtLeakPoint
                                                         , maxoutflow, corespondingRadius, -1,
                                                         -1)
    dispersionModel.initializeDataForEnvSensor(envSensorLat,envSensorLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    #dataSet.to_csv("plumeconcentrationheaveyGas1.csv")
    return model, dataSet
"""
def testPredictGasDispersionHeaveyGasPlumeEnvSensor():
    #gasName = 'CO'
    #concentrationAtEnvSensor = 6
    #envSensorLat = 19.43000031
    #envSensorLong = -99.09999847
    #compressedGases = ['CO','SO2','NO2','NO']

    gasName = 'NO'
    initialConcentrationAtLeakPoint = 6/0.1  # 6 kg/m3
    envSensorLat = 19.43000031
    envSensorLong = -99.09999847
    model,dataSet = predictGasDispersionHeaveyGasPlumeUseCaseEnvSensor(gasName, initialConcentrationAtLeakPoint, envSensorLat, envSensorLong)
    print(dataSet.head(15))
    dataSet.to_csv("experimentalPlumeGasEnv.csv")

#Public Interface 2.
def predictGasDispersionHeaveyGasPlume(gasName,initial_concentration, dispersion_volume, source_radius, gasLeakLat, gasLeakLong):
    model="toxicHeavyPlume"
    winfo = WeatherInfo()
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)


    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windVelocity, windBearing,weather,initial_concentration
                                                        , dispersion_volume,source_radius, gasLeakLat,gasLeakLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    dataSet.to_csv("plumeconcentrationheaveyGas1.csv")
    return model, dataSet


def testCaseBhopal():
    gasName = 'MIC'
    windSpeed = 1.9  # 4 m/s
    initial_concentration = 6  # 6 kg/m3
    source_radius = 2  # 2m
    instantaneous_release = 4000  # kg
    dispersion_volume = 4000/(923*90*60)
    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windSpeed, initial_concentration,dispersion_volume
                                                        , source_radius)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    print(dataSet.head(10))

def testCase1():
    winfo = WeatherInfo()
    gasName = 'LPG'
    #windSpeed = 4  # 4 m/s
    initial_concentration = 9.204070778928614 # 6 kg/m3
    dispersion_volume = 73.38381519067447  # 1 m3/s
    source_radius = 2  # 2m
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage,hour,day = winfo.weatherInfo(
        gasLeakLat, gasLeakLong)


    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windVelocity, windBearing,weather,initial_concentration, dispersion_volume,
                                                         source_radius, gasLeakLat,
                                                         gasLeakLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    dataSet.to_csv("plumeconcentrationheaveyGas1.csv")
    print(dataSet.head(10))
    map_osm = visual_on_maps.drawForHeavyPlume(dataSet,initial_concentration)

def testCase2():
    #gasName = 'Cl'
    gasName='so2'
    winfo = WeatherInfo()
    windSpeed = 4  # 4 m/s
    initial_concentration = 6  # 6 kg/m3
    dispersion_volume = 1  # 1 m3/s
    source_radius = 2  # 2m
    temprature, windBearing, windDirection, windVelocity, weather, pressure, cloudCoverage = winfo.weatherInfo(
        'Mexico', 'Mexico City')
    gasLeakLat = 19.43000031
    gasLeakLong = -99.09999847

    dispersionModel = ToxicHeaveyGasDispersionPlumeModel(gasName, windSpeed,windBearing,weather, initial_concentration, dispersion_volume,
                                                         source_radius,gasLeakLat,gasLeakLong)
    dataSet = dispersionModel.constructConcentraitonAndSizeOfPlume()
    dataSet.to_csv("plumeconcentrationheaveyGas2.csv")
    print(dataSet.head(10))

def main():
    #testCaseBhopal()
    #testCase1()
    #testCase2()
    testPredictGasDispersionHeaveyGasPlumeEnvSensor()

if __name__ == "__main__":
    main()
