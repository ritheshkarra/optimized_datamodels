import math
import pandas
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as GasChemicalConstantsUtilityFunction
#initialize the logger.
#from logbook import Logger, StreamHandler
import sys
#StreamHandler(sys.stdout).push_application()
#log = Logger('Logbook')
#import airDispersionOutflowModels

#calculation of initial flow of gas leak because of different reasons.
#outflow from a vessel


def outflowMassFlowRateForholeInVesselWall(initialVesselPressure,initialVesselTemprature,ambientPressure,
                                            holeDiameter,dischargeCoeff,molecularWeightofDischargeGas,poissonRatio,R):

    initialDensity = (initialVesselPressure * molecularWeightofDischargeGas ) / (R*initialVesselTemprature)
    #print(initialDensity)
    k = coefficientK(initialVesselPressure,ambientPressure,poissonRatio)
    #print(k)
    holeCrossSectionArea = math.pi * pow((holeDiameter/2),2)
    #print("holeCrossSectionArea " + str(holeCrossSectionArea))
    initialOutflowMass = dischargeCoeff*holeCrossSectionArea*initialVesselPressure*k* pow((molecularWeightofDischargeGas/(poissonRatio*R*initialVesselTemprature)),1/2)
    initialOutflowVolume = initialOutflowMass / initialDensity

    return initialOutflowMass,initialOutflowVolume,initialDensity

def outflowMassFlowRateForWholeInVesselWallNextState(vesselVolume,massFlowRate,timeStep,
                                molecularWeight,initialDensity,specificHeat,initialPressure,initialTemprature,R):
    #reduction in densoty and temprature.
    densityReduction = - (massFlowRate/vesselVolume) * timeStep
    #print("density Reduction " + str(densityReduction))
    tempratureReduction = ((initialPressure * densityReduction)/((initialDensity**2)*specificHeat))/(10**3)
    #print("temprature reduction " + str(tempratureReduction))
    #New initial conditions are
    newDensity = initialDensity + densityReduction
    newTemprature = initialTemprature + tempratureReduction
    newPressure = R * newTemprature*(newDensity/molecularWeight)
    return newDensity,newTemprature,newPressure

#Helper Function for outflowMassFlowRateForWholeInVesselWall
def isflowSuperSonic(initialPressure,ambientPressure,poissonRatio):

    ratio = initialPressure/ ambientPressure
    poissonRatio = pow(((poissonRatio+1)/2),(poissonRatio/(poissonRatio-1)))
    return ratio >= poissonRatio
#Helper Function for outflowMassFlowRateForWholeInVesselWall
def coefficientK(initialPressure,ambientPressure,poissonRatio):
    pressureRatio = ambientPressure/initialPressure
    poissonCoefficient = poissonRatio/(1-poissonRatio)
    kmultiplier = 1 - pow(pressureRatio,1/poissonCoefficient)

    kForSubSuperSonic = pow(((2*poissonRatio*poissonCoefficient)*pow(pressureRatio,(2/poissonRatio)))*kmultiplier,1/2)
    kForSuperSonic = poissonRatio * pow((2/(poissonRatio+1)),((poissonRatio+1)/(2*(poissonRatio-1))))

    if (isflowSuperSonic(initialPressure,ambientPressure,poissonRatio)):
        #log.info(" Gas flow is Supersonic")
        return kForSuperSonic
    else:
        #log.info(" Gas flow is Subsupersonic")
        return kForSubSuperSonic

#Function to calculate outflow of gas because of total pipeline rapture.
def gasMassFlowTotalPipeLineRapture(initialPressureInPipe,ambientPressure,initialTempratureOfPipe,pipeDiameter,pipeLengthUntilRapturePoint,
                            dischargeCoeff,molecularWeight,poissonRatio,R):
    initialDensity = (initialPressureInPipe * molecularWeight) / (R * initialTempratureOfPipe)
    #First need to calculate the gas leak from the whole
    k = coefficientK(initialPressureInPipe, ambientPressure, poissonRatio)
    #print(k)
    holeCrossSectionArea = math.pi * pow((pipeDiameter/2),2)
    #print("holeCrossSectionArea " + str(holeCrossSectionArea))
    initialOutflowMass = dischargeCoeff*holeCrossSectionArea*initialPressureInPipe*k* pow((molecularWeight/(poissonRatio*R*initialTempratureOfPipe)),1/2)

    #Initial Mass of the gas in the pipe. KG
    initialMass = initialDensity * pipeLengthUntilRapturePoint * holeCrossSectionArea
    #getting volume flow rate for the gas.
    initialOutflowVolume = initialOutflowMass / initialDensity
    initialVolume = initialMass / initialDensity
    #print("initialMass " + str(initialMass) + "initialOutflowMass " + str(initialOutflowMass) + " initialDensity" + str(initialDensity))
    return initialOutflowMass,initialOutflowVolume,initialDensity,initialMass,initialVolume

def liquidfiedGasMassFlowTotalRaptureOfVesselCloudExpansion(vapourEnthalpyInitial,vapourEnthalpyFinal,massFraction,initialPressure,
                    atmosphericPressure,massFractionInitial,vapourDensityInitial,liquidDensityInitial,
                                        initialHeatOfVaporization, finalHeatOfVaporization):

    inverseAverageDensity = ((1-massFractionInitial)/liquidDensityInitial) + \
                            (massFractionInitial/vapourDensityInitial)

    uf_t1 = vapourEnthalpyInitial - vapourEnthalpyFinal
    uf_t2 = (1-massFraction) *  finalHeatOfVaporization
    uf_t3 = (1- massFractionInitial) * initialHeatOfVaporization
    uf_t4 = (initialPressure-atmosphericPressure) * inverseAverageDensity

    uf = 0.8 * pow((2 * (uf_t1 - uf_t2 + uf_t3 + uf_t4)),1/2)

    return uf

def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step

def liquidfiedGasMassFlowTotalRaptureOfVessel(initialMassFraction,tempratureInVessel,BoilingTempratureAtStandardPressure,
                heatOfVapourizationInitialStage, heatOfVaporizationAtArmospericPressure, liquidHeatCapacity,
                liquidDensityAtBoilingPointAtmosphericPressure,vapourDensityAtBoilingPointAtmosphericPressure
                , massOfGasInVessel,vapourEnthalpyInitial, vapourEnthalpyFinal,initialPressure, atmosphericPressure,
                vapourDensityInitial, liquidDensityInitial,windVelocity):
    #First we will calculate the initial flashing
    #Assumeing final temprature Tb and Final Temprature Tf are equal.
    tempRatio = (BoilingTempratureAtStandardPressure/tempratureInVessel)
    finalMassFraction_T1 = (initialMassFraction * tempRatio)
    finalMassFraction_T2 =  (BoilingTempratureAtStandardPressure /heatOfVaporizationAtArmospericPressure) *\
                            liquidHeatCapacity * math.log(1/tempRatio)
    finalMassFraction = round(finalMassFraction_T1 + finalMassFraction_T2,3)

    if (finalMassFraction < 0.5):
        #log.info("Mass Fraction {0} as it is less than 0.5 Rain-out droplet is assumed", finalMassFraction )
        massRemainingInAtmosphere = 2 * finalMassFraction * massOfGasInVessel
        #mass fraction in atmosphere is assume to be 0.5 so we will calculate density volume etc accordingly.
        newMassFraction = 0.5
        densityInverse = ((1 - newMassFraction) / liquidDensityAtBoilingPointAtmosphericPressure) + \
                         (newMassFraction / vapourDensityAtBoilingPointAtmosphericPressure)
    else:
        #log.info("Mass Fraction {0} as it is greater than 0.5 no Rain-out droplet is assumed", finalMassFraction)
        densityInverse = ((1 - finalMassFraction) / liquidDensityAtBoilingPointAtmosphericPressure) + \
                     (finalMassFraction / vapourDensityAtBoilingPointAtmosphericPressure)
        #In this call all the mass will be in the air.
        massRemainingInAtmosphere = massOfGasInVessel
    #To calculate the radius and volume of the cloud its density is needed.
    volumeOfGasAtFinalStage = massRemainingInAtmosphere*densityInverse
    radiusOftheCloud = pow((3*volumeOfGasAtFinalStage/(2*math.pi)),1/3)

    #Let calculate velocity of cloud expansion.
    uf = liquidfiedGasMassFlowTotalRaptureOfVesselCloudExpansion(
        vapourEnthalpyInitial, vapourEnthalpyFinal, finalMassFraction,initialPressure, atmosphericPressure, initialMassFraction,
        vapourDensityInitial, liquidDensityInitial, heatOfVapourizationInitialStage,heatOfVaporizationAtArmospericPressure)

    #We will calculate the final cloud radius
    # we will also calculate the final cloud

    tf =0
    Rt = 0
    ut = 0
    time = 0
    for t in frange(0,20,.50):
        Rt = pow((4*uf*(radiusOftheCloud**3)*(t-tf) + (radiusOftheCloud**4)),1/4)
        ut = uf * pow((radiusOftheCloud / Rt), 3)
        #log.info("speed {0} radius {1}",ut,Rt)
        if (ut < windVelocity):
            time = t
            break
            #log.info("Speed of air {0} and cloud rate {1}",windVelocity,ut)

    return massRemainingInAtmosphere,1/densityInverse,volumeOfGasAtFinalStage,radiusOftheCloud,uf,Rt

def testliquidfiedGasMassFlowTotalRaptureOfVessel():
    BoilingTempratureAtStandardPressure = 230.9 #K
    pressure = 0.1 * (10**6) #Pa
    liquidDensityAtInitialStage = 505 #Kg/m3
    vapourDensityAtIntialStage = 14.3 #kg/m3
    liquidDensityAtBoilingPointAtmosphericPressure = 584 #Kg/m3
    vapourDensityAtBoilingPointAtmosphericPressure = 2.33 #kg/m3
    vapourEnthalpyAtInitialStage = 483000 #j/kg
    vapourEnthalpyAtBoilingPointAtmosphericPressure = 383000 #j/kg
    heatOfVapourizationInitialStage = 342000 #kj/g
    heatOfVaporizationAtArmospericPressure = 426000 #j/kg
    liquidHeatCapacity                  = 2410 #j/kg K
    windVelocity                        = 3.5 #m/s
    initialMassFraction   = 0.05
    massOfGasInVessel = 5000 #kg
    tempratureInVessel = 291 #k
    pressureInVessel = 0.78 * (10**6) #Pa

    m,d,v,r,uf,Rt = liquidfiedGasMassFlowTotalRaptureOfVessel(initialMassFraction,tempratureInVessel,BoilingTempratureAtStandardPressure,
                heatOfVapourizationInitialStage,heatOfVaporizationAtArmospericPressure, liquidHeatCapacity,
                liquidDensityAtBoilingPointAtmosphericPressure,vapourDensityAtBoilingPointAtmosphericPressure
                , massOfGasInVessel,vapourEnthalpyAtInitialStage, vapourEnthalpyAtBoilingPointAtmosphericPressure,pressureInVessel, pressure,
                vapourDensityAtIntialStage, liquidDensityAtInitialStage,windVelocity)
    print(m,d,v,r,uf)

#We will use the outflow model and estimate the volume of different gases and the initial radius. Method will return the
#75% and 25% for volume and radius calculations.



def enumerateAllPossibleValuesforSetOfGivenToxicGasVolumes(gasName,windSpeed):
    if gasName in GasChemicalConstantsUtilityFunction.compressedGases:
        #log.info("Given chemical {0} is compressed gas",gasName)
        return enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName)
    elif gasName in GasChemicalConstantsUtilityFunction.liqufiedGases:
        #log.info("Given chemical {0} is liquified gas", gasName)
        return enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName)
    else:
        #log.info("Given chemical {0} is not supported currently", gasName)
        return None
#Objective is to find the max values of initialOutflowVolume and corresponding radius
def enumerateAllPossibleValuesforSetOfGivenToxicCompressedGasVolumes(gasName):
    type = 'CG'
    initialVesselPressure = GasChemicalConstantsUtilityFunction.typicalStoragePresure[gasName]
    ambientPressure = 101325 # pa
    initialVesselTemprature = GasChemicalConstantsUtilityFunction.typicalStorageTemp[gasName]
    holeDiameters = [0.025,0.075,0.11,0.15]  # m
    columnName = [ 'gasName','holeDiameter', 'initialOutFlowMass', 'initialOutflowVolume', 'initialDensity']
    volumeOfGas = pandas.DataFrame(columns=columnName)
    #Get Chemical properties
    gasName, molecularWeight, poissonRatio, R, airDensity, gravity, gasDensity, specificHeat, lc50, ldhl, loc = \
        GasChemicalConstantsUtilityFunction.getChemicalPropertiseofGivenGas(gasName)
    liquidHeatCapacity, Hvap, boilingTemprature, liquidDensity, gasDensity, criticalTemprature, criticalPressure = \
        GasChemicalConstantsUtilityFunction.getChemicalPropertiesForAGivenGasAtGivenTempandPressure(gasName, initialVesselTemprature, initialVesselPressure)
    molecularWeightOfGivenGas = molecularWeight /1000  # kg/mol
    dischargeCoeff = 0.62
    maxoutflow = 0
    corespondingRadius = 0
    for holeDiameter in holeDiameters:
        initialOutflowMass, initialOutflowVolume, initialDensity = outflowMassFlowRateForholeInVesselWall(initialVesselPressure,
                                                                          initialVesselTemprature, ambientPressure,
                                                                          holeDiameter, dischargeCoeff,
                                                                          molecularWeightOfGivenGas, poissonRatio, R)
        if (maxoutflow < initialOutflowVolume):
            maxoutflow = initialOutflowVolume
            corespondingRadius = holeDiameter
        tuplesValues =[gasName,holeDiameter,initialOutflowMass, initialOutflowVolume, initialDensity]
        volumeOfGas = volumeOfGas.append(
        pandas.DataFrame([tuplesValues], columns=columnName), ignore_index=True)

    volumeOfGas.to_csv("volumeOfCompressedGas.csv")
    return type,maxoutflow,corespondingRadius



def enumerateAllPossibleValuesforSetOfGivenToxicLiquifiedGasVolumes(gasName,windVelocity):
    type = 'LG'
    #Let collect the various parameters for the given gas.
    Ti = GasChemicalConstantsUtilityFunction.typicalStorageTemp[gasName]
    Pi = GasChemicalConstantsUtilityFunction.typicalStoragePresure[gasName]
    massOfGasInVessel = GasChemicalConstantsUtilityFunction.typicalTransportationMaxContainerSize[gasName]

    # Get Chemical properties at the initial stage when the gas is inside the tank.
    liquidHeatCapacity, Hvap_i, boilingTemprature, liquidDensity_i, gasDensity_i, criticalTemprature, criticalPressure = \
        GasChemicalConstantsUtilityFunction.getChemicalPropertiesForAGivenGasAtGivenTempandPressure(gasName, Ti, Pi)
    Tf = boilingTemprature
    Pf = 101325  # Ambient pressure. Pa
    # Get the checmical properties at final stage that ambient pressure.
    liquidHeatCapacity, Hvap_f, boilingTemprature, liquidDensity_f, gasDensity_f, criticalTemprature, criticalPressure = \
        GasChemicalConstantsUtilityFunction.getChemicalPropertiesForAGivenGasAtGivenTempandPressure(gasName, Tf, Pf)

    BoilingTempratureAtStandardPressure = Tf  # K
    # pressure = 0.1 * (10**6) #Pa
    liquidDensityAtInitialStage = liquidDensity_i
    vapourDensityAtIntialStage = gasDensity_i
    liquidDensityAtBoilingPointAtmosphericPressure = liquidDensity_f
    vapourDensityAtBoilingPointAtmosphericPressure = gasDensity_f
    vapourEnthalpyAtInitialStage = 483000  # j/kg not sure how to calculate automatically
    vapourEnthalpyAtBoilingPointAtmosphericPressure = 383000  # j/kg not sure how to calculate automatically
    heatOfVapourizationInitialStage = Hvap_i
    heatOfVaporizationAtArmospericPressure = Hvap_f
    liquidHeatCapacity = liquidHeatCapacity
    # windVelocity                        = 3.5 #m/s Gather above using the wounderground API
    initialMassFraction = 0.05
    #massOfGasInVessel = 5000  # kg
    tempratureInVessel = Ti
    pressureInVessel = Pi
    columnName = ['windSpeed','MassInVessel','density','volume','radius','VelocityOfExpansion','finalRadius']
    volumeOfGas = pandas.DataFrame(columns=columnName)

    for massOfGasInVessel in range(100,10000,100):
        m, d, v, r, uf, Rt = liquidfiedGasMassFlowTotalRaptureOfVessel(initialMassFraction,
                                                                                          tempratureInVessel,
                                                                                          BoilingTempratureAtStandardPressure,
                                                                                          heatOfVapourizationInitialStage,
                                                                                          heatOfVaporizationAtArmospericPressure,
                                                                                          liquidHeatCapacity,
                                                                                          liquidDensityAtBoilingPointAtmosphericPressure,
                                                                                          vapourDensityAtBoilingPointAtmosphericPressure
                                                                                          , massOfGasInVessel,
                                                                                          vapourEnthalpyAtInitialStage,
                                                                                          vapourEnthalpyAtBoilingPointAtmosphericPressure,
                                                                                          pressureInVessel,
                                                                                          Pf,
                                                                                          vapourDensityAtIntialStage,
                                                                                          liquidDensityAtInitialStage,
                                                                                          windVelocity)
        tupleValues = [windVelocity,massOfGasInVessel,d,v,r,uf,Rt]
        volumeOfGas = volumeOfGas.append(
            pandas.DataFrame([tupleValues], columns=columnName), ignore_index=True)
    object = volumeOfGas.describe(percentiles=[0.25,0.75])
    #print(type(object))
    #print(object)
    #print(object.loc['75%']['finalRadius'])

    volumeOfGas.to_csv("volumeOfLiquifiedGases.csv")
    finalRadius75 =object.loc['75%']['finalRadius']
    finalVolume75 = object.loc['75%']['volume']
    finalRadius25 = object.loc['25%']['finalRadius']
    finalVolume25 = object.loc['25%']['volume']

    return type,finalRadius75,finalVolume75,finalRadius25,finalVolume25

def testCaseOutFlowOfMassForTotalPipeRapture():
    initialPressureInPipe = 0.5 * (10**6) # Pa
    initialTempratureOfPipe = 288.15 #K
    ambientPressure = 1 * (10**5) #mpa
    pipeDiameter = 1 #K
    pipeLengthUntilRapturePoint = 10000 #m
    molecularWeightOfPropane = GasChemicalConstantsUtilityFunction.getGasMolecularWeight("LPG")
    poissonRatio = 1.19
    dischargeCoeff = 1
    R = GasChemicalConstantsUtilityFunction.getUniversalGasConstant()
    timeStep = 1

    massFlowRate,initialOutflowVolume,initialDensity,initialMass, initialVolume = gasMassFlowTotalPipeLineRapture(initialPressureInPipe,ambientPressure,initialTempratureOfPipe,pipeDiameter,pipeLengthUntilRapturePoint,
                            dischargeCoeff,molecularWeightOfPropane,poissonRatio,R)
    print(massFlowRate)
    print(initialOutflowVolume)
    print(initialDensity)
    print(initialMass)
    print(initialVolume)

def testCaseOutFlowOfMassForholeInAVessel():

    vesselVolume = 50 #m3
    initialVesselPressure = 5 * (10**6) #pa
    ambientPressure = 1 * (10**5) #mpa
    initialVesselTemprature = 288.15 #K
    holeDiameter = 0.1 #m
    molecularWeightOfHydrogen = 0.002 #kg/mol
#    mw = GasChemicalConstantsUtilityFunction.getGasMolecularWeight("H2")
    specificHeat = 10.24
    poissonRatio = 1.4
    dischargeCoeff = 0.62
    R = GasChemicalConstantsUtilityFunction.getUniversalGasConstant()
    timeStep = 1

    massFlowRate,initialDensity = outflowMassFlowRateForholeInVesselWall(initialVesselPressure,initialVesselTemprature,ambientPressure,
                                            holeDiameter,dischargeCoeff,molecularWeightOfHydrogen,poissonRatio,R)
    newDensity, newTemprature, newPressure = outflowMassFlowRateForWholeInVesselWallNextState(vesselVolume, massFlowRate, timeStep,
                                                     molecularWeightOfHydrogen, initialDensity, specificHeat, initialVesselPressure,
                                                     initialVesselTemprature, R)
    print(massFlowRate)
    print(initialDensity)
    print(newDensity)
    print(newTemprature)
    print(newPressure)

def testenumerateAllPossibleValuesforSetOfGivenGasVolumes(gasName,windSpeed):
    return enumerateAllPossibleValuesforSetOfGivenToxicGasVolumes(gasName, windSpeed)


def main():
    #testCaseBhopal()
    #testCaseOutFlowOfMassForWholeInAVessel()
    #testCaseOutFlowOfMassForTotalPipeRapture()
    #testliquidfiedGasMassFlowTotalRaptureOfVessel()
    type, finalRadius75, finalVolume75, finalRadius25, finalVolume25 = testenumerateAllPossibleValuesforSetOfGivenGasVolumes('Cl2',3)
    #log.info("CL2 type {0}, o1 {1}, o2 {2}, o3 {3}, 04 {4}",type, finalRadius75, finalVolume75, finalRadius25, finalVolume25 )
    testenumerateAllPossibleValuesforSetOfGivenGasVolumes('SO2', 3)
    #log.info(" SO2 type {0}, o1 {1}, o2 {2}, o3 {3}, 04 {4}", type, finalRadius75, finalVolume75, finalRadius25, finalVolume25)



if __name__ == "__main__":
    main()




