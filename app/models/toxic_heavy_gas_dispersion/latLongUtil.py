#!/usr/bin/python
import numpy as np
import math

#expect input in lat long
def endPointLatLong(lat1, long1, d, bearing):
    R = 6371000  # m radius of the earth
    #convert to radians
    lat1_radians = to_radians(lat1)
    long1_radians = to_radians(long1)
    bearing_radians = to_radians(bearing)
    lat2 = math.asin(math.sin(lat1_radians) * math.cos(d / R) +
                     math.cos(lat1_radians) * math.sin(d / R) * math.cos(bearing_radians));

    long2 = long1_radians + math.atan2(math.sin(bearing_radians) * math.sin(d / R) * math.cos(lat1_radians),
                               math.cos(d / R) - math.sin(lat1_radians) * math.sin(lat2))
    return to_degrees(lat2), to_degrees(long2)

def displace(self, theta, distance):
    """
    Displace a LatLng theta degrees counterclockwise and some
    meters in that direction.
    Notes:
        http://www.movable-type.co.uk/scripts/latlong.html
        0 DEGREES IS THE VERTICAL Y AXIS! IMPORTANT!
    Args:
        theta:    A number in degrees.
        distance: A number in meters.
    Returns:
        A new LatLng.
    """
    theta = np.float32(theta)

    delta = np.divide(np.float32(distance), np.float32(E_RADIUS))

def to_radians(theta):
    return np.divide(np.dot(theta, np.pi), np.float32(180.0))

def to_degrees(theta):
    return np.divide(np.dot(theta, np.float32(180.0)), np.pi)

    theta = to_radians(theta)
    lat1 = to_radians(self.lat)
    lng1 = to_radians(self.lng)

    lat2 = np.arcsin(np.sin(lat1) * np.cos(delta) +
                     np.cos(lat1) * np.sin(delta) * np.cos(theta))

    lng2 = lng1 + np.arctan2(np.sin(theta) * np.sin(delta) * np.cos(lat1),
                             np.cos(delta) - np.sin(lat1) * np.sin(lat2))

    lng2 = (lng2 + 3 * np.pi) % (2 * np.pi) - np.pi

    return to_degrees(lat2), to_degrees(lng2)
def main():
    #testCaseBhopal()
    #testCaseRichardsonNumber()
    #testCase2()
    bearing = 300
    lat1 = 19.43000031
    long1 = -99.09999847
    d = 300
    print(bearing)
    print(lat1)
    print(long1)
    lat2, long2 = endPointLatLong(lat1, long1, d, bearing)
    print(lat2)
    print(long2)
    bearing1 = bearing + 90
    lat3,long3 = endPointLatLong(lat2, long2, d, bearing1)
    print(bearing1)
    print(lat3)
    print(long3)
    bearing2 = bearing + 90
    lat4, long4 = endPointLatLong(lat2, long2, -d, bearing2)
    print(bearing2)
    print(lat4)
    print(long4)



if __name__ == "__main__":
    main()
