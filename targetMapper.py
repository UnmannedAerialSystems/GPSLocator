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

    def __init__(self, lat: float=0, lon: float=0, alt: float=0, heading: float=0):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.heading = heading
        self.geosensor = geosensor.GeoSensor()
        self.targetList: List[Target] = []


    def update(self, lat: float, lon: float, alt: float, heading: float):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.heading = heading

    def getDisplacement(self, x: int, y: int) -> tuple:
        '''
        Input:  x, y - pixel coordinates
        Output: xOffset, yOffset - displacement from the center of the sensor in meters

        This method converts pixel coordinates to physical distances across the sensor.
        '''
        xOffset, yOffset = self.geosensor.geoSensorIO(x, y, self.alt)

        # Convert the heading to radians
        heading = self.heading * pi / 180

        # Calculate the target offset latitude and longitude
        targetX = yOffset * cos(heading) + xOffset * sin(heading)
        targetY = xOffset * cos(heading) - yOffset * sin(heading)

        return targetX, targetY
    
    def getTarget(self, x: int, y: int):

        # get the target displacement
        dx, dy = self.getDisplacement(x, y)

        # get the target latitude and longitude
        latTarget  = self.lat  + (dy / EARTH_RADIUS) * (180 / pi);
        lonTarget = self.lon + (dx / EARTH_RADIUS) * (180 / pi) / cos(self.lat * pi/180);

        return Target(latTarget, lonTarget)


class Target:

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def update(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
