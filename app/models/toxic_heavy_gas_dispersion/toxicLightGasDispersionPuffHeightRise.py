import math
import app.models.toxic_heavy_gas_dispersion.gasDispersionModelingUtilityFunctions as gdmuf
import config

def round(value):
    return config.customRounding(value)

#Fb = g (9.8 m/s2 * vs (m/s) * d2(m) * ΔT / (4 * Ts)
def calculateBuoyancyFluxParameterPuff(gravity,airDensity,TotalGasMassInPuff,ambientTemprature,tempratureOfReleaseGas):
    Fbi = ((gravity * TotalGasMassInPuff)/(math.pi*airDensity)) * ((tempratureOfReleaseGas - ambientTemprature) / ambientTemprature)
    return round(Fbi)

#Calculate the maximum distance for puff release.
def calculationOfDistanceOfMaximumPuffRise(buoyancyFluxParameter, stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir):
    mutliplier = pow(windSpeedAtStackHeight,2/3)
    if (stabilityClass in ['A','B','C','D']):
        if (buoyancyFluxParameter < 300*mutliplier):
            x = 12 * pow(buoyancyFluxParameter,1/2) * pow(windSpeedAtStackHeight,1/3)
        else:
            x = 50 * pow(buoyancyFluxParameter, 1 / 4) * pow(windSpeedAtStackHeight, 1 / 2)
    elif (stabilityClass in ['E','F']):
        s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
        x = math.pi * windSpeedAtStackHeight/pow(s,1/2)

    return round(x)


def plumeHeightRiseAfterMaxDistance(stackHeight,buoyancyFluxParameter, maxDistance,puffInitialRadius,
                                           stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,coeff=0.64):

    if (stabilityClass in ['A', 'B', 'C', 'D']):
        plumeHeightRiseAfterXf = stackHeight + pow(((2 * buoyancyFluxParameter * (maxDistance**2)) / ((coeff ** 3) * (windSpeedAtStackHeight ** 2))), 1 / 4)
    elif (stabilityClass in ['E', 'F']):
        s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
        rRatio = puffInitialRadius / coeff
        fluxParameterMultiplier = 8 * buoyancyFluxParameter / ((coeff ** 3) * s)
        plumeHeightRiseAfterXf = stackHeight + pow((fluxParameterMultiplier + (rRatio ** 4)), 1 / 4) - rRatio

    return round(plumeHeightRiseAfterXf)

def calculatePluffHeightAtObservationPoint(stackHeight,buoyancyFluxParameter, puffInitialRadius,pointOfObservation,
                                           stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,coeff=0.64):
    if (stabilityClass in ['A', 'B', 'C', 'D']):
        height = stackHeight + pow(((2*buoyancyFluxParameter*(pointOfObservation**2))/((coeff**3)*(windSpeedAtStackHeight**2))),1/4)
    elif (stabilityClass in ['E', 'F']):
        s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
        rRatio = puffInitialRadius / coeff
        cosineValue = 1 - math.cos(pointOfObservation*pow(s,1/2)/windSpeedAtStackHeight)
        fluxParameterMultiplier = 4*buoyancyFluxParameter/((coeff**3)*s)
        height = stackHeight + pow((fluxParameterMultiplier*cosineValue + (rRatio**4)),1/4) - rRatio
    return round(height)

#plume gradual plume rise before xf and after xf with function of distance x
def calculationOfgradualPluffRise(stackHeight,buoyancyFluxParameter, puffInitialRadius,distanceOfMaxPlumeRise,
                                intervalOfObservations,stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,coeff=0.64):

    #We will calculate the plume rise for every 50m till the distance of max Plume Rise.
    numberOfIteration = int(distanceOfMaxPlumeRise // intervalOfObservations)
    plumeGradualRise = []
    #Let do an initial calculation
    plumeHeightRise = calculatePluffHeightAtObservationPoint(stackHeight, buoyancyFluxParameter, puffInitialRadius,
                                                             1,
                                                             stabilityClass, windSpeedAtStackHeight,
                                                             tempratureOfSurroundingAir, coeff)

    plumeGradualRise.append([1, plumeHeightRise])

    for x in range(1,numberOfIteration+1):
    #for x in range(1, 100):
        pointOfObservation = x * intervalOfObservations
        plumeHeightRise = calculatePluffHeightAtObservationPoint(stackHeight,buoyancyFluxParameter, puffInitialRadius,pointOfObservation,
                                           stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,coeff)

        plumeGradualRise.append([pointOfObservation,plumeHeightRise])
        plumeHeightRise = 0
    #let calcualte plume final height beyound distance xf

    plumeHeightRiseAfterxf = plumeHeightRiseAfterMaxDistance(stackHeight,buoyancyFluxParameter, distanceOfMaxPlumeRise,
                                puffInitialRadius,stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,coeff)
    return plumeGradualRise,plumeHeightRiseAfterxf

def calculatePuffRise(stackHeight,cloudCoverage,day,gravity, airDensity,TotalGasMassInPuff,puffInitialRadius,
                                intervalOfObservations,windRefSpeed,ambientTemprature,tempratureOfReleaseGas,WindRefHeight,terrain,coeff=0.64):
    stabilityClass = gdmuf.getAtmospericStabilityClass(windRefSpeed, cloudCoverage, day)
    print("Stability Class " + stabilityClass)
    windSpeedAtStackHeight = gdmuf.calculateWindSpeedAtStackHeight(stabilityClass, windRefSpeed, stackHeight, WindRefHeight,
                                                       terrain)
    print("windSpeedAtStackHeight " + str(windSpeedAtStackHeight))
    buoyancyFluxParameter = calculateBuoyancyFluxParameterPuff(gravity,airDensity,TotalGasMassInPuff,ambientTemprature,tempratureOfReleaseGas)
    print("buoyancyFluxParameter " + str(buoyancyFluxParameter))
    distanceOfMaxPluffRise = calculationOfDistanceOfMaximumPuffRise(buoyancyFluxParameter, stabilityClass,windSpeedAtStackHeight,ambientTemprature)
    print("Distance of max pluff rise " + str(distanceOfMaxPluffRise))
    gradualRise,puffHeight = calculationOfgradualPluffRise(stackHeight, buoyancyFluxParameter, puffInitialRadius, distanceOfMaxPluffRise,
                                  intervalOfObservations, stabilityClass, windSpeedAtStackHeight,
                                                           ambientTemprature,coeff)
    return gradualRise,puffHeight

def testCalculatePuffRiseOfPollutant():
    instaneousRelease   = 500 #kg
    windRefSpeed       = 4 #m/s
    ambientTemprature  =298 #K
    gasExitTemprature   = 420 #K
    stackDiameter       = 1 #m
    stackHeight         = 2 #m
    #exitGasSpeed        = 4 #m/s
    day = True
    terrain = 'rural'
    windRefHeight = 10 #m
    gravity = 9.8 #m2/s
    intervalOfObservations = 50 #m
    airDensity =1.21 #kg/m3
    cloudCoverage = 0/8
    coeff = 0.64
    h,h1 = calculatePuffRise(stackHeight,cloudCoverage,day,gravity, airDensity,instaneousRelease,stackDiameter,
                                intervalOfObservations,windRefSpeed,ambientTemprature,gasExitTemprature,windRefHeight,terrain,coeff)
    print("Final outcome " + str(h) + "," + str(h1))


def main():
    #testCaseWindSpeed()
    #testDownWashtobeConsider()
    #testCriticalTempratureCalculation()
    #testCaseAtmosphericStability()
    testCalculatePuffRiseOfPollutant()

if __name__ == "__main__":
    main()






