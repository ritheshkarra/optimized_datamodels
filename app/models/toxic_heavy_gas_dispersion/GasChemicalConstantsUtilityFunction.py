from thermo.chemical import Chemical

#Note - need to find a way to support No2 and NO
listOfSupprtedGases = {'LPG', 'CH4', 'CO', 'Cl2','SO2','NO'}
#CO2 Need to find more info
liqufiedGases = {'LPG','Cl2'}
compressedGases = ['SO2','NO']
#K
typicalStorageTemp = {'LPG':291,'CH4':328,'CO': 325,'Cl2':328,'SO2':348,'NO2':325,'NO':325}
#Pa
typicalStoragePresure = {'LPG':780000,'CH4':103421,'CO':13789500,'Cl2':1379000,'SO2':150000,'NO2':120000,'NO':120000}
#in KG
typicalTransportationMaxContainerSize = {'LPG':15000,'CH4':25000,'CO':1000,'Cl2':20000,'SO2':1000,'NO2':20000,'NO':20000}
#unit for gas density below kg/m3 at normal tempration NTP 20 degree centigrade
gasDensity = {'LPG':1.898, 'CH4': 0.668, 'CO': 1.165, 'Cl2': 2.994,'MIC': 923,'SO2':2.279,'NO':1.34,'NO2':1.88}
#source https://www.cdc.gov/niosh/idlh/intridl4.html
IDLHPPM = {'LPG': 2000, 'CH4': 1000, 'CO': 1200, 'Cl2': 10,'SO2':100,'NO':100,'NO2':20}
#unit kg/m3
IDLHKGM3 = {'LPG': 3.6, 'CH4': 0.7603, 'CO': 0.00148, 'Cl2': 0.00003,'SO2':0.00025,'NO':0.000132,'NO2':0.000036}
#unit g/m3
IDLHGM3 = {'LPG': 3600, 'CH4': 760.3, 'CO': 1.48, 'Cl2': 0.03,'SO2':0.25,'NO':0.132,'NO2':0.036}

IDLHMICROGM3 = {'LPG': 3600000000, 'CH4': 760300000, 'CO': 1480000, 'Cl2': 30000,'SO2':250000,'NO':132000,'NO2':36000}

#Moecular weight g/mole
gasMolecularWeight = {'LPG': 44.1, 'CH4': 16.043, 'CO': 28.011, 'Cl2': 70.906,'MIC':57.051,'SO2':48.1,'NO':30.006,'NO2':46}

#Specific Heat JKG-1K-1
gasSpecificHeatAtConstantVolume = {'LPG': 1480, 'CH4': 1700, 'CO': 720, 'Cl2': 360,'SO2':510,'NO':718,'NO2':690}
gasPoissonRatio = {'LPG': 1.19, 'CH4': 1700, 'CO': 720, 'Cl2': 360,'SO2':510,'NO':718,'NO2':690}
#gasViscosity    = {'LPG': , 'CH4': 1700, 'CO': 720, 'Cl': 360,'SO2':510,'NO':718,'NO2':690}

concentrationThresoldRatio = 0.1
airDensity = 1.21 #kg/m3
gravity = 9.81 #m/s2
KG = 'KGM3'
G = 'GM3'
PPM = 'ppm'
MICROG = 'MICROGM3'
universalGasConstant = 8.314
#LP, Methane, CO, Chlorine heavey gages
#light gases
#SO2, NO2, NO, CO, PM 1.0, PM 2.5
#Air density
def getAirDensity():
    return airDensity

def getGravity():
    return gravity

def getGasDensity(gas):
    return gasDensity[gas]

def getGasPoissonRatio(gasName):
    return gasPoissonRatio[gasName]

def getGasMolecularWeight(gas,unit='Kg'):
    if (unit == 'Kg'):
        return gasMolecularWeight[gas] / 1000
    else:
        return gasMolecularWeight[gas]



def getGasSpecificHeat(gas):
    return gasSpecificHeatAtConstantVolume[gas]

def getGasLethalConcentration(gas,unit):
    if (unit == PPM):
        idlhVal =  IDLHPPM[gas]
    elif (unit == KG):
        idlhVal = IDLHKGM3[gas]
    elif (unit == G):
        idlhVal = IDLHGM3[gas]
    elif (unit == MICROG):
        idlhVal = IDLHMICROGM3[gas]
    else:
        idlhVal = -1
    ldhl = idlhVal
    loc = 0.1 * idlhVal
    lc50 = 10 * idlhVal
    return lc50,ldhl,loc

def getUniversalGasConstant():
    return universalGasConstant

def getChemicalPropertiesForAGivenGasAtGivenTempandPressure(chemical,Temp,Pressure):
    if chemical == 'LPG':
        chemical = 'propane'
    chemicalObject = Chemical(chemical,T=Temp,P=Pressure)
    liquidHeatCapacity = chemicalObject.Cpl
    Hvap = chemicalObject.Hvap
    boilingTemprature = chemicalObject.Tb
    criticalTemprature = chemicalObject.Tc
    criticalPressure = chemicalObject.Pc
    liquidDensity = chemicalObject.rhol
    gasDensity = chemicalObject.rhog
    #obj = chemicalObject.EnthalpyVaporization
    return liquidHeatCapacity,Hvap,boilingTemprature,liquidDensity,gasDensity,criticalTemprature,criticalPressure

def getChemicalPropertiesForAGivenGasAtStnadardTempandPressure(chemical):
    if chemical == 'LPG':
        chemical = 'propane'
    elif chemical == 'No2':
        chemical = 'Nitrite'

    chemicalObject = Chemical(chemical)
    liquidHeatCapacity = chemicalObject.Cpl
    Hvap = chemicalObject.Hvap
    boilingTemprature = chemicalObject.Tb
    criticalTemprature = chemicalObject.Tc
    criticalPressure = chemicalObject.Pc
    liquidDensity = chemicalObject.rhol
    gasDensity = chemicalObject.rhog
    #obj = chemicalObject.EnthalpyVaporization
    return liquidHeatCapacity,Hvap,boilingTemprature,liquidDensity,gasDensity,criticalTemprature,criticalPressure



def getChemicalPropertiseofGivenGas(gasName):
    molecularWeight = getGasMolecularWeight(gasName)
    poissonRatio = getGasPoissonRatio(gasName)
    R = getUniversalGasConstant()
    airDensity = getAirDensity()
    gravity = getGravity()
    gasDensity = getGasDensity(gasName)
    specificHeat = getGasSpecificHeat(gasName)
    lc50, ldhl, loc = getGasLethalConcentration(gasName, MICROG)
    return gasName,molecularWeight,poissonRatio,R,airDensity,gravity,gasDensity,specificHeat,lc50, ldhl, loc

def testgetChemicalPropertiesForAGivenGasAtGivenTempandPressure():
    T= 291
    P = 0.78 * 10**6
    #{'LPG', 'CH4', 'CO', 'Cl2', 'SO2', 'NO', 'NO2'}
    liquidHeatCapacity, Hvap, boilingTemprature, liquidDensity, gasDensity,tc,pc = \
        getChemicalPropertiesForAGivenGasAtGivenTempandPressure('NO',T,P)


def main():
    #testCaseBhopal()
    #testCaseOutFlowOfMassForWholeInAVessel()
    #testCaseOutFlowOfMassForTotalPipeRapture()
    testgetChemicalPropertiesForAGivenGasAtGivenTempandPressure()


if __name__ == "__main__":
    main()