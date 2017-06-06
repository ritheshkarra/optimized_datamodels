
def doWeGetMetrologicalData(temprature, windBearing, windDirection, windVelocity, weather,pressure,cloudCoverage):
    if (temprature== None) or (windBearing == None) or (windDirection == None) or (windVelocity == None) or (weather == None) \
        or (pressure == None) or (cloudCoverage == None):
        errorno = 5
        errorMsg = "Metrological Data Not recieved " + "temprature " + str(temprature) + " windBearing " + str(windBearing) +\
                   " windDirection " + str(windDirection) + " windVelocity " + str(windVelocity) + " weather " + str(weather) + \
                    " pressure " + str(pressure) + " cloud Coverage " + str(cloudCoverage)
        return False, errorno, errorMsg

    errorno = 0
    errorMsg = " Metrological  Data " + "temprature " + str(temprature) + " windBearing " + str(windBearing) +\
                   " windDirection " + str(windDirection) + " windVelocity " + str(windVelocity) + " weather " + str(weather) + \
                    " pressure " + str(pressure) + " cloud Coverage " + str(cloudCoverage)
    return True,errorno,errorMsg

def checkAllRelevantParamtersareSetForInitalGasVolumeCalcualtions(leakType,initialVesselPressure,initialVesselTemprature,
                                holeDiameter, initialPressureInPipe,initialTempratureOfPipe,pipeDiameter,pipeLengthUntilRapturePoint):
    if (leakType == None):
        errorno = 1
        errorMsg = "Leak Type need to provided"
        return False,errorno,errorMsg

    if (leakType == 'VESSEL'):
        if (initialVesselPressure == None) or (initialVesselTemprature == None) or (holeDiameter == None):
            errorno = 2
            errorMsg = "Required parameters missing for leak Type " + leakType + " Vessel Pressure " \
                       + str(initialVesselPressure) + " Vessel Temprature " + str(initialVesselTemprature) + " Hole Diameter " + str(holeDiameter)
            return False,errorno,errorMsg
    else:
        if (initialPressureInPipe == None) or (initialTempratureOfPipe == None) or (pipeDiameter == None) or (pipeLengthUntilRapturePoint == None):
            errorno = 3
            errorMsg = "Required parameters missing for leak Type " + leakType + " Pipe Pressure " \
                       + str(initialPressureInPipe) + " Pipe Temprature " + str(initialTempratureOfPipe) \
                       + " Pipe Diameter " + str(pipeDiameter) + " Pipe Lenght Until Rapture " + str(pipeLengthUntilRapturePoint)
            return False,errorno,errorMsg
    errorno = 0
    errorMsg = "Parameters Leak Type " + " Vessel Pressure " \
                       + str(initialVesselPressure) + " Vessel Temprature " + str(initialVesselTemprature) + " Hole Diameter " \
               + str(holeDiameter) + " Pipe Pressure " \
                       + str(initialPressureInPipe) + " Pipe Temprature " + str(initialTempratureOfPipe) \
                       + " Pipe Diameter " + str(pipeDiameter) + " Pipe Lenght Until Rapture " + str(pipeLengthUntilRapturePoint)
    return True, errorno, errorMsg

