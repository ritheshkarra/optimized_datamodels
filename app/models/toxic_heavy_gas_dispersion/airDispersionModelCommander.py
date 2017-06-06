from app.models.toxic_heavy_gas_dispersion.weatherInfo import WeatherInfo
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
import app.models.toxic_heavy_gas_dispersion.airDispersionOutflowModels as airDispersionOutflowModels
import app.models.toxic_heavy_gas_dispersion.gasDispersionModelingUtilityFunctions as gasDispersionModelingUtilityFunctions
from app.models.toxic_heavy_gas_dispersion.toxicHeavyGasDispersionPuffModel import predictGasDispersionForHeavyGasPuffUseCaseEnvSensor
from app.models.toxic_heavy_gas_dispersion.toxicHeavyGasDispersionPlumeModel import predictGasDispersionHeaveyGasPlumeUseCaseEnvSensor
import app.models.toxic_heavy_gas_dispersion.toxicLightGasDispersionPuffModel as toxicLightGasDispersionPuffModel
import app.models.toxic_heavy_gas_dispersion.toxicLightGasDispersionPlumeModel as toxicLightGasDispersionPlumeModel
import app.models.toxic_heavy_gas_dispersion.errorChecking as errorChecking
import app.models.toxic_heavy_gas_dispersion.visual_on_maps as visual_on_maps
import numpy as np
import json

import sys

class airDispersionModel:

    def frictionVelocity(windSpeed10):
        return 0.03*windSpeed10

    def calculate_acceleration_g0(self,gravity,gas_density,air_density):
        # g0 = g(gas_density - air_density)/air_density
        g0 = gravity * ((gas_density - air_density) / air_density)
        return g0

    def characteristicHeightOftheSource(self,initialVolume,areaOfSource):
        return (initialVolume/areaOfSource)

    #Test for using heavey gas or light gas
    def criticalRichardsonConstant(self,initialVolume,areaOfSource,gravity,gas_density,air_density,windSpeed10):
        H = self.characteristicHeightOftheSource(initialVolume,areaOfSource)
        g0 = self.calculate_acceleration_g0(gravity,gas_density,air_density)
        U2 = self.frictionVelocity(windSpeed10)**2 # Wind speed
        rc = (H * g0) / U2
        return rc

    def isItHeaveyGasModel(self,initialVolume,areaOfSource,gravity,gas_density,air_density,windVelocity):
        rc = self.criticalRichardsonConstant(initialVolume,areaOfSource,gravity,gas_density,air_density,windVelocity)
        if (rc < 1):
            return False  #"passive"
        else:
            return True #"nonpassive"

    def heavyGasPuffOrPlume(self,windSpeed,release_duration,distance):
        rule = windSpeed * release_duration / distance
        if rule >= 2.5:
            return "plume"
        elif rule <= 0.6:
            return "puff"
        elif rule > 0.6 and rule < 2.5:
            return "both"

    def lightGasPuffPlume(self,windSpeed,releaseDuration,stabilityClass,x):
        sigma_y , sigma_z = toxicLightGasDispersionPuffModel.DispersionCoefficientPuff(x, stabilityClass)

        if (windSpeed*releaseDuration < 2*sigma_y):
            model = "puff"
        elif (windSpeed*releaseDuration > 5*sigma_y):
            model = "plume"
        else:
            model = "both"
        return model
    concentrationRatioThresoldValue = GasChemicalConstantsUtilityFunction.concentrationThresoldRatio

    #public interface1
    def predictGasDispersionHeaveyGasEnvSensor(self,gasName,concentrationAtEnvSensor,envSensorLat,envSensorLong,pWindBearing=None,pWindSpeed=None):
        # This is the assumption. Env Sensor concentration value would be 10% of origina
        initialConcentrationAtLeakPoint = concentrationAtEnvSensor / self.concentrationRatioThresoldValue
        if gasName in GasChemicalConstantsUtilityFunction.compressedGases:
            return predictGasDispersionHeaveyGasPlumeUseCaseEnvSensor(gasName,initialConcentrationAtLeakPoint,envSensorLat,envSensorLong,pWindBearing,pWindSpeed)
        elif gasName in GasChemicalConstantsUtilityFunction.liqufiedGases:
            return predictGasDispersionForHeavyGasPuffUseCaseEnvSensor(gasName,initialConcentrationAtLeakPoint,envSensorLat,envSensorLong,pWindBearing,pWindSpeed)
        else:
            return None

    #public Inerface2
    def predictAirPollutionSpread(self,automatedCalculateInitialGasVolume
                              ,gasLeakLat, gasLeakLong
                              , gasName #To fetch gas chemical constants
                              , leakType #to get the gas mass flow rate, initial volume and inital concentration.
                              , initialVesselPressure
                              , initialVesselTemprature
                              , holeDiameter  # for calculating gas flow and initial volume
                              , initialPressureInPipe
                              , initialTempratureOfPipe
                              , pipeDiameter #
                              , pipeLengthUntilRapturePoint # m
                              , day
                              , releaseDuration
                              , pufforplume  #set it to null of we would like us to calculate which model to use.
                              , distancePuffVsPlume #distance at which we are calculating the puff Vs Plume
                              , initial_concentration  #it will come from sensor or we calculate using outflow model.
                              , dispersion_volume
                              , source_radius
                              , TotalGasMassInPuff # parameters required for toxic light gas puff model. if null we will use the calculated from pipe lenght
                              , intervalofObservations # interval on which we should calculate the concentation
                              , coefficient # indicate roughness of the source usually default to 0.64
                              , y #axix on y direction
                              , z #concentration at height usually we will keep at 2m the height of human
                              , terrain # rural or urban
                              , initialPuffRadius #Can it be source radius
                              , timeList #Time when concentration has to be calculated. -1 to calculated at peak time.
                              , stackHeight
                              , stackDiameter
                              , tempratureOfReleaseGas # should we keep same as the initialTemprature of Pipe, exitGas temprature.
                              , exitGasSpeed #Speed of gas exit from stack.
                              , sourceEmissionRate
    ):
        listOfSupportedGases = GasChemicalConstantsUtilityFunction.listOfSupprtedGases
        if (gasName not in listOfSupportedGases):
            errorMsg = "We are only supporting gases " + str(listOfSupportedGases)
            return False,errorMsg,None,None

        #get the weather and metrological data.
        temprature, windBearing, windDirection, windVelocity, weather,pressure,cloudCoverage,hour,day =  WeatherInfo.weatherInfo(gasLeakLat, gasLeakLong)
        ret, errorNo, errorMsg = errorChecking.doWeGetMetrologicalData(temprature, windBearing, windDirection, windVelocity, weather,pressure,cloudCoverage)
        if (ret == False):
            return False,errorMsg,None,None
        #Whether light or heavey gas.
        air_density = GasChemicalConstantsUtilityFunction.getAirDensity()
        gravity = GasChemicalConstantsUtilityFunction.getGravity()
        gas_density = GasChemicalConstantsUtilityFunction.getGasDensity(gasName)

        molecularWeight = GasChemicalConstantsUtilityFunction.getGasMolecularWeight(gasName, 'Kg')  # kg/mol
        specificHeat = GasChemicalConstantsUtilityFunction.getGasSpecificHeat(gasName)
        poissonRatio = GasChemicalConstantsUtilityFunction.getGasPoissonRatio(gasName)
        dischargeCoeff = coefficient
        R = GasChemicalConstantsUtilityFunction.getUniversalGasConstant()
        # we got all the chemical properties of the gas.
        massFlowRate = None
        volumeFlowRate = None
        initialDensity = None
        initialMass = None
        if (automatedCalculateInitialGasVolume):
            #Let check if all relevant Paramters value are set.
            ret,errorNo,errorMsg = errorChecking.checkAllRelevantParamtersareSetForInitalGasVolumeCalcualtions(leakType,initialVesselPressure,initialVesselTemprature,
                                holeDiameter, initialPressureInPipe,initialTempratureOfPipe,pipeDiameter,pipeLengthUntilRapturePoint)
            if (ret == False):
                return False,errorMsg,None, None

            if (leakType == 'VESSEL'):
                massFlowRate,volumeFlowRate, initialDensity = airDispersionOutflowModels.outflowMassFlowRateForWholeInVesselWall(initialVesselPressure,
                                                                           initialVesselTemprature, pressure,
                                                                           holeDiameter, dischargeCoeff,
                                                                               molecularWeight, poissonRatio, R)
            else:
                massFlowRate,volumeFlowRate, initialDensity, initialMass,initialVolume = airDispersionOutflowModels.gasMassFlowTotalPipeLineRapture(initialPressureInPipe,
                                                                                    pressure,
                                                                                    initialTempratureOfPipe,
                                                                                    pipeDiameter,
                                                                                    pipeLengthUntilRapturePoint,
                                                                                    dischargeCoeff,
                                                                                    molecularWeight,
                                                                                    poissonRatio, R)

        if (initialDensity == None):
            initialDensity = initial_concentration
        if (volumeFlowRate == None):
            volumeFlowRate = dispersion_volume

        modelIdentifier = ''
        areaOfSource = 1  # Default for time being.
        initialVolume = 1 # Default for time being.
        #Use critical Richardson number to determine if it is heavy or light gases.
        heaveyGasModel = self.isItHeaveyGasModel(initialVolume, areaOfSource, gravity, gas_density, air_density, windVelocity)
        #Get the stability class
        stabilityClass = gasDispersionModelingUtilityFunctions.getAtmospericStabilityClass(windVelocity,cloudCoverage,day)
        if (heaveyGasModel):
            modelIdentifier = 'HeavyGasModel for ' + gasName
            if (pufforplume != None):
                if (pufforplume == 'puff'):
                    usePuff = True
                else:
                    usePuff = False
            else:
                #Determine whether plume or puff model to be applied.
                #set default x = 1 and releaseDuration is 1. Ideally we should check every x for puff and plume
                modelType = self.heavyGasPuffOrPlume(windVelocity,releaseDuration,distancePuffVsPlume)

                if (modelType == 'puff'):
                    usePuff = True
                else:
                    usePuff = False

            if (usePuff):
                modelIdentifier = modelIdentifier + ' Puff'
                dispersionModel, dataSet = toxicLightGasDispersionPuffModel.predictGasDispersionForHeavyGasPuff(gasName,initial_concentration,source_radius,dispersion_volume,gasLeakLat,gasLeakLong)
                dataSet.to_csv("concentrationDataPuffModel.csv")
                return modelIdentifier , dataSet
            else:
                modelIdentifier = modelIdentifier + ' Plume'

                dispersionModel, dataSet=toxicLightGasDispersionPlumeModel.predictGasDispersionHeaveyGasPlume(gasName,initial_concentration, dispersion_volume, source_radius, gasLeakLat, gasLeakLong)
                dataSet.to_csv("plumeconcentrationheaveyGas.csv")
                return modelIdentifier, dataSet
        else:
            modelIdentifier = 'LightGasModel for ' + gasName
            #let figure out if we need to do puff or plume model.
            if (pufforplume != None):
                if (pufforplume == 'puff'):
                    usePuff = True
                else:
                    usePuff = False
            else:

                modelType = self.lightGasPuffPlume(windVelocity,releaseDuration,stabilityClass,distancePuffVsPlume)
                if (modelType == 'puff'):
                    usePuff = True
                else:
                    usePuff = False
        if (usePuff):
            modelIdentifier = modelIdentifier + ' Puff'

            windRefHeight = WeatherInfo.windRefHeight()  # m
            gravity = GasChemicalConstantsUtilityFunction.getGravity()  # m2/s
            airDensity = GasChemicalConstantsUtilityFunction.getAirDensity()
            # dispersionModel = toxicLightGasDispersionPuffModel.ToxicLightGasDispersionPuffModel()
            model,concentrationData = toxicLightGasDispersionPuffModel.predictGasDispersionLightGasPuff(tempratureOfReleaseGas, stackHeight, terrain, windRefHeight,
                          gasName, initialPuffRadius, TotalGasMassInPuff, timeList, gasLeakLat, gasLeakLong)
            # concentrationData = dispersionModel.calculateConcentrationForPuffGas(stackHeight, cloudCoverage, day, gravity, airDensity,
            #                         TotalGasMassInPuff,initialPuffRadius,intervalofObservations, windVelocity,windBearing,weather,
            #                         windRefHeight, temprature,
            #                          tempratureOfReleaseGas, terrain, y, z,timeList, coefficient,gasName,gasLeakLat,gasLeakLong)

            concentrationData.to_csv("testOutComePuffmodelLightGases.csv")
            return modelIdentifier , concentrationData
        else:
            modelIdentifier = modelIdentifier + ' Plume'
            windRefHeight = WeatherInfo.windRefHeight()  # m
            gravity = GasChemicalConstantsUtilityFunction.getGravity()  # m2/s
            # dispersionModel = toxicLightGasDispersionPlumeModel.ToxicLightGasDispersionPlumeModel()

            model, concentrationData =toxicLightGasDispersionPlumeModel.predictGasDispersionLightGasPlume(tempratureOfReleaseGas, stackDiameter, stackHeight, exitGasSpeed, sourceEmissionRate,
                                      terrain, gasName, gasLeakLat, gasLeakLong)
            # concentrationData = dispersionModel.calculateConcentrationForPlumeGas( cloudCoverage, windVelocity,windBearing,
            #                         weather, day, terrain, gravity, windRefHeight,temprature, tempratureOfReleaseGas,
            #                           intervalofObservations, stackDiameter, stackHeight, exitGasSpeed,
            #                           sourceEmissionRate, y, z,gasName,gasLeakLat,gasLeakLong)
            concentrationData.to_csv("testOutComeLightGasPlume.csv")
            return modelIdentifier,concentrationData

    def displayDispersion(self,modelIdentifier,dataSet,iC,zoom):
        print(modelIdentifier)
        if "HeavyGasModel" in modelIdentifier.split():

            if "Puff" in modelIdentifier.split():
                map_osm = visual_on_maps.drawForHeavyPuff(dataSet,iC,zoom)
            elif "Plume" in modelIdentifier.split():
                map_osm = visual_on_maps.drawForHeavyPlume(dataSet,iC,zoom)
        elif "LightGasModel" in modelIdentifier.split():
            if "Puff" in modelIdentifier.split():
                map_osm = visual_on_maps.drawForLightPlume(dataSet,zoom)
            elif "Plume" in modelIdentifier.split():
                map_osm = visual_on_maps.drawForLightPuff(dataSet,zoom)
        return  map_osm

    def testCaseRichardsonNumber(self):
        initialVolume = 500
        areaOfSource = 1
        gravity = 9.8
        gas_density = 1.1
        air_density = 1.21
        windVelocity = 2

        t = self.isItHeaveyGasModel(initialVolume, areaOfSource, gravity, gas_density, air_density, windVelocity)

    def analyze_gas_dispersion(self,gasName,leakType, automatedCalculateInitialGasVolume, initialVesselPressure, initialVesselTemprature, holeDiameter,initialPressureInPipe,initialTempratureOfPipe, pipeDiameter, pipeLengthUntilRapturePoint, day,releaseDuration, pufforplume, distancePuffVsPlume, initial_concentration, dispersion_volume, source_radius, TotalGasMassInPuff, intervalofObservations, coefficient, y, z, terrain, initialPuffRadius, timeList, stackHeight, stackDiameter,tempratureOfReleaseGas, exitGasSpeed,sourceEmissionRate, gasLeakLat, gasLeakLong):

        model="commander"
        modelIdentifier, dataSet = self.predictAirPollutionSpread(automatedCalculateInitialGasVolume
                              , gasLeakLat,gasLeakLong #lat long for the gas leak
                              , gasName #To fetch gas chemical constants
                              , leakType #to get the gas mass flow rate, initial volume and inital concentration.
                              , initialVesselPressure
                              , initialVesselTemprature
                              , holeDiameter  # for calculating gas flow and initial volume
                              , initialPressureInPipe
                              , initialTempratureOfPipe
                              , pipeDiameter #
                              , pipeLengthUntilRapturePoint # m
                              , day
                              , releaseDuration
                              , pufforplume  #set it to null of we would like us to calculate which model to use.
                              , distancePuffVsPlume
                              , initial_concentration  #it will come from sensor or we calculate using outflow model.
                              , dispersion_volume
                              , source_radius
                              , TotalGasMassInPuff # parameters required for toxic light gas puff model. if null we will use the calculated from pipe lenght
                              , intervalofObservations # interval on which we should calculate the concentation
                              , coefficient # indicate roughness of the source usually default to 0.64
                              , y #axix on y direction
                              , z #concentration at height usually we will keep at 2m the height of human
                              , terrain # rural or urban
                              , initialPuffRadius #Can it be source radius
                              , timeList #Time when concentration has to be calculated. -1 to calculated at peak time.
                              , stackHeight
                              , stackDiameter
                              , tempratureOfReleaseGas # should we keep same as the initialTemprature of Pipe, exitGas temprature.
                              , exitGasSpeed #Speed of gas exit from stack.
                              , sourceEmissionRate
    )
        return model, dataSet, modelIdentifier


    def test_public_interface(self):
        gasName='LPG'
        leakType='VESSEL'
        automatedCalculateInitialGasVolume = False
        initialVesselPressure = None
        initialVesselTemprature = None
        #vesselVolume = None
        holeDiameter = None
        initialPressureInPipe = 0.5 * (10**6) # Pa
        initialTempratureOfPipe = 288.15
        pipeDiameter  = 1
        pipeLengthUntilRapturePoint = 10000
        day = True
        releaseDuration = 10 #s
        pufforplume = 'puff'  # set it to null of we would like us to calculate which model to use.
        distancePuffVsPlume = 1
        initial_concentration  = 10# it will come from sensor or we calculate using outflow model.
        dispersion_volume = 1
        source_radius = 2
        TotalGasMassInPuff = 500 #Kg
        intervalofObservations=50  # interval on which we should calculate the concentation
        coefficient = 1  # indicate roughness of the source usually default to 0.64
        y = 0 # axix on y direction
        z = 2  # concentration at height usually we will keep at 2m the height of human
        terrain = 'rural'  # rural or urban
        initialPuffRadius = 1 # Can it be source radius
        timeList = [-1,30,60,240]  # Time when concentration has to be calculated. -1 to calculated at peak time.
        stackHeight = 2
        stackDiameter = 1
        tempratureOfReleaseGas = 288.15
        exitGasSpeed =4 # Speed of gas exit from stack.
        sourceEmissionRate = 200
        gasLeakLat = 19.43000031
        gasLeakLong = -99.09999847

        model, dataset, modelIdentifier=self.analyze_gas_dispersion(gasName,leakType, automatedCalculateInitialGasVolume, initialVesselPressure, initialVesselTemprature, holeDiameter,initialPressureInPipe,initialTempratureOfPipe, pipeDiameter, pipeLengthUntilRapturePoint, day,releaseDuration, pufforplume, distancePuffVsPlume, initial_concentration, dispersion_volume, source_radius, TotalGasMassInPuff, intervalofObservations, coefficient, y, z, terrain, initialPuffRadius, timeList, stackHeight, stackDiameter,tempratureOfReleaseGas, exitGasSpeed,sourceEmissionRate, gasLeakLat, gasLeakLong)

    def testpredictGasDispersionHeaveyGasEnvSensor(self):
        gasName = 'LPG'
        concentrationAtEnvSensor = 6
        envSensorLat = 19.43000031
        envSensorLong = -99.09999847
        # What this method do.
        # It will automatically detect which kind of dispersion model to be use. Gestimate the actual leak site. Remember Environment
        # sensor location is not the actual leak location.
        # Return
        # Model Name - One of the two - "HeavyGasPuffEnvSensor", "HeavyGasPuff" Model name will identify the file format.
        # dataSet75 - DataFrame we can save it any format we want. Let us use this data for visual
        # dataSet25 - DataFrame with data having 25 percentile values.
        #modelName, dataSet75, dataSet25 = self.predictGasDispersionHeaveyGasEnvSensor(gasName,concentrationAtEnvSensor,envSensorLat,envSensorLong,pWindBearing=None,pWindSpeed=None)
        out = self.predictGasDispersionHeaveyGasEnvSensor(gasName, concentrationAtEnvSensor,
                                                                                      envSensorLat, envSensorLong,
                                                                                      pWindBearing=None,
                                                                                      pWindSpeed=None)
        print("lenght ----" , out[1])

def main():
    airdisp = airDispersionModel()
    #testCaseBhopal()
    #testCaseRichardsonNumber()
    #testCase2()
    # testCasePredictGasSpread('Cl', None)
    #test_public_interface()
    airdisp.testpredictGasDispersionHeaveyGasEnvSensor()

if __name__ == "__main__":
    main()
