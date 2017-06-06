#!/usr/bin/python
import config
import math
import app.models.toxic_heavy_gas_dispersion.GasChemicalConstantsUtilityFunction as idlh
import config
from numpy import *
from pandas import *

def getAtmospericStabilityClass(windSpeed,cloudCoverage,day=True):
    stabilityClass=""
    if (windSpeed < 2):
        if (day):
            if (cloudCoverage < 5/8):
                stabilityClass = 'A'
            else:
                stabilityClass = 'B'
        else:
            stabilityClass = 'F'
    elif ((windSpeed >= 2) and (windSpeed < 3)):
        if (day):
            if (cloudCoverage <= 2/8):
                stabilityClass = 'A'
            elif ((cloudCoverage >= 3/8) and (cloudCoverage <= 5/8)):
                stabilityClass = 'B'
            elif ((cloudCoverage >= 6/8)):
                stabilityClass = 'C'
        else:
            if (cloudCoverage <= 3/8):
                stabilityClass = 'E'
            elif (cloudCoverage >= 4/8):
                stabilityClass = 'F'
    elif ((windSpeed >= 3) and (windSpeed < 5)):
        if (day):
            if (cloudCoverage <= 2/8):
                stabilityClass = 'B'
            elif ((cloudCoverage >= 3/8) and (cloudCoverage <= 5/8)):
                stabilityClass = 'B'
            elif ((cloudCoverage >= 6/8)):
                stabilityClass = 'D'
        else:
            if (cloudCoverage <= 3/8):
                stabilityClass = 'D'
            elif (cloudCoverage >= 4/8):
                stabilityClass = 'E'
    elif ((windSpeed >= 5) and (windSpeed < 6)):
        if (day):
            if (cloudCoverage <= 2/8):
                stabilityClass = 'C'
            elif ((cloudCoverage >= 3/8) and (cloudCoverage <= 5/8)):
                stabilityClass = 'C'
            elif ((cloudCoverage >= 6/8)):
                stabilityClass = 'D'
        else:
            if (cloudCoverage <= 3/8):
                stabilityClass = 'D'
            elif (cloudCoverage >= 4/8):
                stabilityClass = 'D'
    elif (windSpeed >=6) :
        if (day):
            if (cloudCoverage <= 2/8):
                stabilityClass = 'C'
            elif ((cloudCoverage >= 3/8) and (cloudCoverage <= 5/8)):
                stabilityClass = 'D'
            elif ((cloudCoverage >= 6/8)):
                stabilityClass = 'D'
        else:
            if (cloudCoverage <= 3/8):
                stabilityClass = 'D'
            elif (cloudCoverage >= 4/8):
                stabilityClass = 'D'
    return stabilityClass


def getWindProfileExponentRural(stabilityClass):
    windProfileExponentRural = {'A':0.07,'B':0.07,'C':0.10,'D':0.15,'E':0.35,'F':0.55}
    return windProfileExponentRural[stabilityClass]

def getWindProfileExponentUrban(stabilityClass):
    windProfileExponentUrban = {'A': 0.15, 'B': 0.15, 'C': 0.20, 'D': 0.25, 'E': 0.30, 'F': 0.30}
    return windProfileExponentUrban[stabilityClass]

def getWindProfileExponent(stabilityClass,terrain='urban'):
    if (terrain == 'urban'):
        p = getWindProfileExponentUrban(stabilityClass)
    else:
        p = getWindProfileExponentRural(stabilityClass)
    return p

#Deacon power law for calculating wind speed at stack height
def calculateWindSpeedAtStackHeight(stabilityClass,windRefSpeed,stackHeight,WindRefHeight=10,terrain='urban'):
    windProfileExponent = getWindProfileExponent(stabilityClass,terrain)
    #print(WindRefHeight)
    windSpeed = windRefSpeed * pow((stackHeight/WindRefHeight),windProfileExponent)
    return config.customRounding(windSpeed)

def caluclatesFactorForStability(stabilityClass,tempratureOfSurroundingAir):
    if (stabilityClass in ['E']):
        changeInTempratureWithHeight = 0.02
    elif (stabilityClass in ['F']):
        changeInTempratureWithHeight = 0.035

    g = 9.8
    s = (g / tempratureOfSurroundingAir ) * changeInTempratureWithHeight
    #print("Ambient temprature " + str(tempratureOfSurroundingAir))
    return s


def calculateIsoplethConcentration( gas,unit):
    return idlh.getGasLethalConcentration(gas, unit)


def calculateIsoplethsHelper( sigma_y, isoplethConcentration, c_x_0_0_t):
    # print("sigma " + str(sigma_y) + "c_x_0_0_t " + str(c_x_0_0_t) + 'isoplethConcentration' + str(isoplethConcentration))
    if c_x_0_0_t == 0:
        # given concentration is zero then y axis will be zero as well.
        y = 0
    elif (isoplethConcentration < c_x_0_0_t):

        y = sigma_y * pow((2 * math.log((c_x_0_0_t / isoplethConcentration))), 1 / 2)
    else:
        y = 0
    return y


def calculateIsopleths(sigma_y, gas, c_x_0_0_t,unit):
    lc50, ldhl, loc = calculateIsoplethConcentration(gas,unit)
    y_loc = calculateIsoplethsHelper(sigma_y, loc, c_x_0_0_t)
    y_ldhl = calculateIsoplethsHelper(sigma_y, ldhl, c_x_0_0_t)
    y_lc50 = calculateIsoplethsHelper(sigma_y, lc50, c_x_0_0_t)
    return config.customRounding(y_lc50), config.customRounding(y_ldhl), config.customRounding(y_loc)
