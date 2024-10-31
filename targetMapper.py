"""
PSU UAS ...
Author: Ted Tasman
Date: 2024-10-17
Description:    This module converts craft GPS coordinates and heading, 
                along with a geosensor displacement into a target GPS coordinate
Version: v1.0.0
"""

from math import sin, cos, pi
import geosensor
from typing import List

EARTH_RADIUS = 6371000  # Earth's radius in meters

class Craft:

    def __init__(self, lat: float=0, lon: float=0, alt: float=0, roll: float=0, pitch: float=0, heading: float=0):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.pitch = pitch
        self.roll = roll
        self.heading = heading
        self.geosensor = geosensor.GeoSensor()
        self.targetList: List[Target] = []


    def update(self, lat: float, lon: float, alt: float, roll: float, pitch: float, heading: float):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.pitch = pitch
        self.roll = roll
        self.heading = heading

    def getDisplacement(self, xOffset: int, yOffset: int) -> tuple:
        '''
        Input:  xOffset, yOffset - pixel coordinates
        Output: targetX, targetY - displacement from the center of the sensor in meters

        Normalizes the target displacement to North and East distances
        '''

        # Convert the heading to radians
        heading = self.heading * pi / 180

        # Calculate the target offset latitude and longitude
        targetX = yOffset * cos(heading) + xOffset * sin(heading)
        targetY = xOffset * cos(heading) - yOffset * sin(heading)

        return targetX, targetY
    
    def getTargetPosition(self, dx: float, dy: float) -> tuple:
        '''
        Input:  dx, dy - displacement from the center of the sensor in meters
        Output: lat, lon - target latitude and longitude

        Converts displacement from meters to degrees latitude and longitude.
        >>> craft = Craft(40.798214, -77.859909, 0, 0, 0, 0)
        '''
        # Calculate the target latitude and longitude
        latTarget  = self.lat  + (dy / EARTH_RADIUS) * (180 / pi);
        lonTarget = self.lon + (dx / EARTH_RADIUS) * (180 / pi) / cos(self.lat * pi/180);

        return latTarget, lonTarget

    def getTarget(self, x: int, y: int):
        '''
        Input:  x, y - pixel coordinates
        Output: target - Target object

        This method returns a Target object with the latitude and longitude of the target.
        '''
        # get the sensor displacement
        xOffset, yOffset = self.geosensor.geoSensorIO(x, y, self.alt, self.roll, self.pitch)

        # get the target displacement
        dx, dy = self.getDisplacement(xOffset, yOffset)

        # get the target latitude and longitude
        latTarget, lonTarget = self.getTargetPosition(dx, dy)

        return Target(latTarget, lonTarget)


class Target:

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def update(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon


