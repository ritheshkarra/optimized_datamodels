import math

class bmmCurveApproximation:
    def getBMModelCurveApproxForPlumes(self,concentrationRatio,xValue):
        loggedXValue = math.log10(xValue)
        #print("xvalue " + str(xValue) +" logged " + str(loggedXValue))
        returnValue = 0
        if (concentrationRatio == 0.1):
            if (loggedXValue <= -0.55):
                returnValue = 10**1.75
            elif ( -0.55 < loggedXValue <= -0.14):
                returnValue  = 10 ** ((0.24 * loggedXValue) + 1.88)
            elif (-0.14 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.50 * loggedXValue) + 1.78)
        elif(concentrationRatio == 0.05):
            if (loggedXValue <= -0.68):
                returnValue = 10**1.92
            elif ( -0.68 < loggedXValue <= -0.29):
                returnValue  = 10 ** ((0.36 * loggedXValue) + 2.16)
            elif (-0.29 < loggedXValue <= -0.18):
                returnValue = 10 ** 2.06
            elif ( -0.18 < loggedXValue <= 1.0):
                returnValue  = 10 ** ((-0.56 * loggedXValue) + 1.96)
        elif (concentrationRatio == 0.02):
            if (loggedXValue <= -0.69):
                returnValue = 10**2.08
            elif ( -0.69 < loggedXValue <= -0.31):
                returnValue  = 10 ** ((0.45 * loggedXValue) + 2.39)
            elif (-0.31 < loggedXValue <= -0.16):
                returnValue = 10 ** 2.25
            elif ( -0.16 < loggedXValue <= 1.0):
                returnValue  = 10 ** ((-0.54 * loggedXValue) + 2.16)
        elif (concentrationRatio == 0.01):
            if (loggedXValue <= -0.70):
                returnValue = 10 ** 2.25
            elif (-0.70 < loggedXValue <= -0.29):
                returnValue = 10 ** ((0.49 * loggedXValue) + 2.59)
            elif (-0.29 < loggedXValue <= -0.20):
                returnValue = 10 ** 2.45
            elif (-0.20 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.52 * loggedXValue) + 2.35)
        elif (concentrationRatio == 0.005):
            if (loggedXValue <= -0.67):
                returnValue = 10 ** 2.40
            elif (-0.67 < loggedXValue <= -0.28):
                returnValue = 10 ** ((0.59 * loggedXValue) + 2.80)
            elif (-0.28 < loggedXValue <= -0.15):
                returnValue = 10 ** 2.63
            elif (-0.15 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.49 * loggedXValue) + 2.56)
        elif (concentrationRatio == 0.002):
            if (loggedXValue <= -0.69):
                returnValue = 10 ** 2.60
            elif (-0.69 < loggedXValue <= -0.25):
                returnValue = 10 ** ((0.39 * loggedXValue) + 2.87)
            elif (-0.25 < loggedXValue <= -0.13):
                returnValue = 10 ** 2.77
            elif (-0.13 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.50 * loggedXValue) + 2.71)

        return  returnValue

    def getBMModelCurveApproxForPuffs(self,concentrationRatio,xValue):
        loggedXValue = math.log10(xValue)
        returnValue = -1
        if (concentrationRatio == 0.1):
            if (loggedXValue <= -0.44):
                returnValue = 10**0.70
            elif ( -0.44 < loggedXValue <= -0.43):
                returnValue  = 10 ** ((0.26 * loggedXValue) + 0.81)
            elif (-0.43 < loggedXValue <= 1.0):
                returnValue = 10 ** 0.93
        elif(concentrationRatio == 0.05):
            if (loggedXValue <= -0.56):
                returnValue = 10**0.85
            elif ( -0.56 < loggedXValue <= 0.31):
                returnValue  = 10 ** ((0.26 * loggedXValue) + 1.0)
            elif (0.31 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.12 * loggedXValue) + 1.12)
        elif (concentrationRatio == 0.02):
            if (loggedXValue <= -0.66):
                returnValue = 10**0.95
            elif ( -0.66 < loggedXValue <= 0.32):
                returnValue  = 10 ** ((0.36 * loggedXValue) + 1.19)
            elif (0.32 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.26 * loggedXValue) + 1.38)
        elif (concentrationRatio == 0.01):
            if (loggedXValue <= -0.71):
                returnValue = 10**1.15
            elif ( -0.71 < loggedXValue <= 0.37):
                returnValue  = 10 ** ((0.34 * loggedXValue) + 1.39)
            elif (0.37 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.38 * loggedXValue) + 1.66)
        elif (concentrationRatio == 0.005):
            if (loggedXValue <= -0.52):
                returnValue = 10**1.48
            elif ( -0.52 < loggedXValue <= 0.24):
                returnValue  = 10 ** ((0.26 * loggedXValue) + 1.62)
            elif (0.24 < loggedXValue <= 1.0):
                returnValue = 10 ** ((-0.30 * loggedXValue) + 1.75)
        elif (concentrationRatio == 0.002):
            if (loggedXValue <= -0.27):
                returnValue = 10**1.83
            elif ( -0.27 < loggedXValue <= 1.0):
                returnValue  = 10 ** ((-0.32 * loggedXValue) + 1.92)
        elif (concentrationRatio == 0.001):
            if (loggedXValue <= -0.10):
                returnValue = 10**2.075
            elif ( -0.10 < loggedXValue <= 1.0):
                returnValue  = 10 ** ((-0.27 * loggedXValue) + 2.05)
        print("concentrationRatio " + str(concentrationRatio) + "return value " + str(returnValue))
        return  returnValue
