import math
import app.models.toxic_heavy_gas_dispersion.gasDispersionModelingUtilityFunctions as gdmuf
import config


def round(value):
    return config.customRounding(value)

def isthereDownWashtobeConsider(stackVelocity, windSpeedAtPlumeElevation):
    downWashtoBeConsider = ((stackVelocity/windSpeedAtPlumeElevation) < 1.5)
    return (downWashtoBeConsider)

def tempDifference(tempratureOfReleaseGas, tempratureOfSurroundingAir):
    return (tempratureOfReleaseGas - tempratureOfSurroundingAir)

#Fb = g (9.8 m/s2 * vs (m/s) * d2(m) * ΔT / (4 * Ts)
def calculateBuoyancyFluxParameter(gravity,stackVelocity,diameterofStack,tempratureOfReleaseGas, tempratureOfSurroundingAir,):
    Fb = gravity * stackVelocity * pow(diameterofStack,2) * ((tempratureOfReleaseGas - tempratureOfSurroundingAir) / (4 * tempratureOfReleaseGas))
    return round(Fb)

def calcualateCriticalTemprature(stabilityClass,tempratureOfReleaseGas,tempratureOfSurroundingAir,diameterofStack,stackVelocity,BuoyancyfluxParameter):
    if (stabilityClass in ['A','B','C','D']):
        if (BuoyancyfluxParameter < 55):
           deltaT =  0.0297 * tempratureOfReleaseGas * pow(stackVelocity,2/3)/pow(diameterofStack,1/3)
        else:
            deltaT = 0.00575 * tempratureOfReleaseGas * pow(stackVelocity,2/3) / pow(diameterofStack, 1/3)
    elif (stabilityClass in ['E','F']):
        s = gdmuf.caluclatesFactorForStability(stabilityClass,tempratureOfSurroundingAir)
        deltaT = 0.019582 * tempratureOfReleaseGas * stackVelocity * pow(s,1/2)

    return deltaT

def isBuoyancyDominated(stabilityClass,tempratureOfReleaseGas,tempratureOfSurroundingAir,diameterofStack,stackVelocity):
    gravity = 9.8
    BuoyancyfluxParameter = calculateBuoyancyFluxParameter(gravity, stackVelocity, diameterofStack,
                                                           tempratureOfReleaseGas, tempratureOfSurroundingAir)
    criticalTemprature = calcualateCriticalTemprature(stabilityClass, tempratureOfReleaseGas, tempratureOfSurroundingAir, diameterofStack,
                                 stackVelocity, BuoyancyfluxParameter)
    tempratureDifference = tempDifference(tempratureOfReleaseGas, tempratureOfSurroundingAir)

    return (tempratureDifference > criticalTemprature)

def calculationOfDistanceOfMaximumPlumeRise(buyonacyDominated,buoyancyFluxParameter, stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,diameterofStack,stackVelocity):
    if (buyonacyDominated == True):
        if (stabilityClass in ['A','B','C','D']):
            if (buoyancyFluxParameter < 55):
                x = 49 * pow(buoyancyFluxParameter,5/8)
            else:
                x = 119 * pow(buoyancyFluxParameter, 2/5)
        elif (stabilityClass in ['E','F']):
            s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
            x = 2.0715 * windSpeedAtStackHeight/pow(s,1/2)
    # Momentum
    else:
        if (stabilityClass in ['A','B','C','D']):
            if (buoyancyFluxParameter == 0):
                x = 4 * diameterofStack * pow((stackVelocity + 3 * windSpeedAtStackHeight),2) / (stackVelocity * windSpeedAtStackHeight)
            elif (buoyancyFluxParameter < 55):
                x = 49 * pow(buoyancyFluxParameter,5/8)
            else:
                x = 119 * pow(buoyancyFluxParameter,2/5)
        elif (stabilityClass in ['E','F']):
            s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
            x = 0.50* math.pi * pow(s,1/2)
    print("stability calss -" + stabilityClass + " x " + str(x) + " buyoyancy " + str(buyonacyDominated))
    return round(x)

def calulatePlumeHeight(buyonacyDominated,buoyancyFluxParameter, stackEffectiveHeight,observationDistance,stabilityClass
                        ,windSpeedAtStackHeight,tempratureOfSurroundingAir,tempratureOfReleaseGas,diameterofStack,stackVelocity):
    if (buyonacyDominated == True):
        plumeHeightRise = stackEffectiveHeight + 1.60 * (pow(buoyancyFluxParameter,1/3)*pow(observationDistance,2/3))/windSpeedAtStackHeight
    # Momentum
    else:
        betaJ = (1/3) + (windSpeedAtStackHeight/stackVelocity)
        #s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
        fm = pow(stackVelocity,2)*pow(diameterofStack,2)*(tempratureOfSurroundingAir/(4*tempratureOfReleaseGas))
        if (stabilityClass in ['A','B','C','D']):
            plumeHeightRise = stackEffectiveHeight + 1.60 * pow((3 * fm * observationDistance)/ ((betaJ**2)*(stackVelocity**2)),1/3)
        elif (stabilityClass in ['E','F']):
            s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
            plumeHeightRise = stackEffectiveHeight + pow(((3*fm)*math.sin(observationDistance*pow(s,1/2)/windSpeedAtStackHeight)/((betaJ**2)*windSpeedAtStackHeight*pow(s,1/2))),1/3)
    return round(plumeHeightRise)

def plumeHeightRiseAfterXf(buyonacyDominated,buoyancyFluxParameter, stackEffectiveHeight
                           ,stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,tempratureOfReleaseGas,diameterofStack,stackVelocity):
    if (buyonacyDominated == True):
        if (stabilityClass in ['A', 'B', 'C', 'D']):
            if (buoyancyFluxParameter < 55):
                plumeHeightRiseAfterXf = stackEffectiveHeight + 21.425 * ( pow(buoyancyFluxParameter, 3 / 4) / windSpeedAtStackHeight)
            else:
                plumeHeightRiseAfterXf = stackEffectiveHeight + 38.710 * (pow(buoyancyFluxParameter, 3 / 5) / windSpeedAtStackHeight)
        elif (stabilityClass in ['E', 'F']):
            s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
            plumeHeightRiseAfterXf = stackEffectiveHeight + 2.6 * pow((buoyancyFluxParameter / (s * windSpeedAtStackHeight)), 1 / 3)
    else:

        fm = pow(stackVelocity, 2) * pow(diameterofStack, 2) * (tempratureOfSurroundingAir / (4 * tempratureOfReleaseGas))
        if (stabilityClass in ['A', 'B', 'C', 'D']):
            plumeHeightRiseAfterXf = stackEffectiveHeight + 3 * diameterofStack * (stackVelocity / windSpeedAtStackHeight)
        elif (stabilityClass in ['E', 'F']):
            s = gdmuf.caluclatesFactorForStability(stabilityClass, tempratureOfSurroundingAir)
            plumeHeightRiseAfterXf1 = stackEffectiveHeight + 3 * diameterofStack * (stackVelocity / windSpeedAtStackHeight)
            plumeHeightRiseAfterXf2 = stackEffectiveHeight + 1.5 * pow((fm / (windSpeedAtStackHeight * (s ** 1 / 2))), 1 / 3)
            if (plumeHeightRiseAfterXf1 < plumeHeightRiseAfterXf2):
                plumeHeightRiseAfterXf = plumeHeightRiseAfterXf1
            else:
                plumeHeightRiseAfterXf = plumeHeightRiseAfterXf2
    return round(plumeHeightRiseAfterXf)

#plume gradual plume rise before xf and after xf with function of distance x
def calculationOfFinalPlumeRise(buyonacyDominated,buoyancyFluxParameter, stackEffectiveHeight,distanceOfMaxPlumeRise,
                                intervalOfObservations,stabilityClass,windSpeedAtStackHeight,tempratureOfSurroundingAir,
                                tempratureOfReleaseGas,diameterofStack,stackVelocity):

    #We will calculate the plume rise for every 50m till the distance of max Plume Rise.
    if (distanceOfMaxPlumeRise < intervalOfObservations):
        numberOfIteration = 1
    else:
        numberOfIteration = int(distanceOfMaxPlumeRise // intervalOfObservations)
    plumeGradualRise = []
    for x in range(1,numberOfIteration+1):
    #for x in range(1, 100):
        observationDistance = x * intervalOfObservations
        plumeHeightRise = calulatePlumeHeight(buyonacyDominated, buoyancyFluxParameter, stackEffectiveHeight, observationDistance,
                            stabilityClass
                            , windSpeedAtStackHeight, tempratureOfSurroundingAir, tempratureOfReleaseGas,
                            diameterofStack, stackVelocity)

        plumeGradualRise.append([observationDistance,plumeHeightRise])
        plumeHeightRise = 0
    #let calcualte plume final height beyound distance xf

    plumeHeightRiseAfterxf = plumeHeightRiseAfterXf(buyonacyDominated, buoyancyFluxParameter, stackEffectiveHeight,
                        stabilityClass, windSpeedAtStackHeight, tempratureOfSurroundingAir, tempratureOfReleaseGas,diameterofStack, stackVelocity)

    return plumeGradualRise,plumeHeightRiseAfterxf

def effectiveStackHeight(stackHeight,stackDiameter,stackVelocity,windSpeedAtStackHeight):
    if ((stackVelocity/windSpeedAtStackHeight) < 1.5):
        effectiveStackHeight = stackHeight + 2 * stackDiameter * ((stackVelocity/windSpeedAtStackHeight) - 1.5)
    else:
        effectiveStackHeight = stackHeight
    return round(effectiveStackHeight)

def calculatePlumeRiseOfPollutant(cloudCoverage,windRefSpeed,day,terrain,gravity,windRefHeight,ambientTemprature,gasExitTemprature,
                                  intervalOfObservations,stackDiameter,stackHeight,exitGasSpeed):
    stabilityClass = gdmuf.getAtmospericStabilityClass(windRefSpeed, cloudCoverage, day)
    #Wind Speed at the top of the stack
    windSpeedAtStackHeight = gdmuf.calculateWindSpeedAtStackHeight(stabilityClass, windRefSpeed, stackHeight, windRefHeight, terrain)
    print("WindSpeedatstackheight - " + str(windSpeedAtStackHeight))
    stackEffectiveHeight = effectiveStackHeight(stackHeight,stackDiameter,exitGasSpeed,windSpeedAtStackHeight)
    print("effective stack height -" + str(stackEffectiveHeight))
    isBuoyancy = isBuoyancyDominated(stabilityClass,gasExitTemprature,ambientTemprature,stackDiameter,exitGasSpeed)
    print("isBuoyancy - " + str(isBuoyancy))
    buoyancyFluxParameter = calculateBuoyancyFluxParameter(gravity,exitGasSpeed,stackDiameter,gasExitTemprature,ambientTemprature)
    distanceOfMaxPlumeRise = calculationOfDistanceOfMaximumPlumeRise(isBuoyancy,buoyancyFluxParameter, stabilityClass,
                                                                     windSpeedAtStackHeight,ambientTemprature,stackDiameter,exitGasSpeed)
    print("distance of Max Plume Rise -" +  str(distanceOfMaxPlumeRise))
    finalPlumeGradualRise,plumeFinalRise = calculationOfFinalPlumeRise(isBuoyancy,buoyancyFluxParameter, stackEffectiveHeight,distanceOfMaxPlumeRise
                            ,intervalOfObservations,stabilityClass,windSpeedAtStackHeight,ambientTemprature,gasExitTemprature,stackDiameter,exitGasSpeed)

    print("Plume gradual rise - " + str(finalPlumeGradualRise) + " " + str(plumeFinalRise))
    return finalPlumeGradualRise,plumeFinalRise

def testCalculatePlumeRiseOfPollutant():
    cloudCoverage   = 5/8
    windRefSpeed       = 2 #m/s
    ambientTemprature  =280 #K
    gasExitTemprature   = 400 #K
    stackDiameter       = 1 #m
    stackHeight         = 25 #m
    exitGasSpeed        = 4 #m/s
    day = False
    terrain = 'rural'
    windRefHeight = 10 #m
    gravity = 9.8 #m2/s
    intervalOfObservations = 50 #m

    h,h1 = calculatePlumeRiseOfPollutant(cloudCoverage, windRefSpeed, day,terrain,gravity,windRefHeight,ambientTemprature, gasExitTemprature,
                                         intervalOfObservations,stackDiameter,stackHeight, exitGasSpeed)
    print("Final outcome " + str(h) + "," + str(h1))


def testCriticalTempratureCalculation():
    stabilityClass = 'A'
    tempratureOfReleaseGas = 400
    tempratureOfSurroundingAir = 283
    diameterofStack = 3
    stackVelocity = 19
    gravity = 9.8
    BuoyancyfluxParameter = calculateBuoyancyFluxParameter(gravity,stackVelocity,diameterofStack,tempratureOfReleaseGas, tempratureOfSurroundingAir)
    print(BuoyancyfluxParameter)
    print(calcualateCriticalTemprature(stabilityClass,tempratureOfReleaseGas,tempratureOfSurroundingAir,diameterofStack,stackVelocity,BuoyancyfluxParameter))
    print(isBuoyancyDominated(stabilityClass,tempratureOfReleaseGas,tempratureOfSurroundingAir,diameterofStack,stackVelocity))

def testDownWashtobeConsider():
    print(isthereDownWashtobeConsider(19,5.3))

def testCaseWindSpeed():
    U10m = 4 #m/s
    stackHeight = 67 #m
    stabilityClass = 'D'
    #Assuming it is a power plant so it will be in rural areas
    windSpeed = gdmuf.windSpeedAtStackHeight(stabilityClass,U10m,stackHeight,terrain='rural')
    print('windSpeed ' + str(windSpeed))

def testCaseAtmosphericStability():
    windSpeed = 5
    cloudCoverage = 5/8
    day = False
    print(gdmuf.getAtmospericStabilityClass(windSpeed, cloudCoverage, day))

def main():
    #testCaseWindSpeed()
    #testDownWashtobeConsider()
    #testCriticalTempratureCalculation()
    #testCaseAtmosphericStability()
    testCalculatePlumeRiseOfPollutant()

if __name__ == "__main__":
    main()






