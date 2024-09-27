"""
PSU UAS GEOSENSOR
Author: Ted Tasman
Date: 2024-09-26
Description: This module converts sensor coordinates to geospatial coordinates.
Version: v1.0.0
"""

from math import atan, tan, cos, pi

class GeoSensor:
    # CONSTANTS -- Depending on the sensor, these values may change
    MOUNTING_ANGLE = pi / 4    # mounting angle of the sensor in radians (0 is down, pi/2 is horizontal)
    RESOLUTION_X = 1332             # resolution of the sensor in the x direction
    RESOLUTION_Y = 990              # resolution of the sensor in the y direction
    FOCAL_LENGTH = 0.015            # focal length of the sensor in meters
    SENSOR_WIDTH = 0.006287         # width of the sensor in meters
    SENSOR_HEIGHT = 0.004712        # height of the sensor in meters
    

    def pixelToPhysical(self, x: int, y: int) -> tuple:
        '''
        Input:  x, y - pixel coordinates
        Output: physicalX, physicalY - physical distance from the bottom left of the sensor in meters

        This method converts pixel coordinates to physical distances across the sensor.
        '''
        physicalY = y * (GeoSensor.SENSOR_HEIGHT / GeoSensor.RESOLUTION_Y)
        physicalX = x * (GeoSensor.SENSOR_WIDTH / GeoSensor.RESOLUTION_X)

        return physicalX, physicalY
    
    def physicalToAngle(self, physicalX: float | int, physicalY: float | int) -> tuple:
        '''
        Input:  physicalX, physicalY - physical distance from the bottom left of the sensor in meters
        Output: angleX, angleY - angle in radians from the center of the sensor

        This method converts physical distances to angles from the center of the sensor.
        '''
        angleX = atan((physicalX - (GeoSensor.SENSOR_WIDTH / 2)) / GeoSensor.FOCAL_LENGTH)
        angleY = atan((physicalY - (GeoSensor.SENSOR_HEIGHT / 2)) / GeoSensor.FOCAL_LENGTH)

        return angleX, angleY
    
    def getYOffset(self, height: int | float, angleY: int | float) -> float:
        '''
        Input:  height - height of the sensor from the ground in meters
                angleY - angle in the y direction in radians
        Output: yOffset - offset in the y direction in meters

        This method calculates the offset in the forwards (y) direction from the point directly below the sensor.
        '''
        yOffset = height * tan(angleY + GeoSensor.MOUNTING_ANGLE)
        return yOffset
    
    def getXOffset(self, height: float | int, angleX: float | int, angleY: float | int) -> float:
        '''
        Input:  height - height of the sensor from the ground in meters
                angleX - angle in the x direction in radians
                angleY - angle in the y direction in radians
        Output: xOffset - offset in the x direction in meters

        This method calculates the offset in the sideways (x) direction from the point directly below the sensor.
        '''
        xOffset = height / cos(angleY + GeoSensor.MOUNTING_ANGLE) * tan(angleX)
        return xOffset
    
    def geoSensorIO(self, x: int, y: int, height: int | float) -> tuple:
        '''
        Input:  x, y - pixel coordinates
                height - height of the sensor from the ground in meters
        Output: xOffset, yOffset - offsets in the x and y directions in meters

        This is the main IO method for the GeoSensor module.
        It takes pixel coordinates and height as input and returns the offsets in the x and y directions.
        '''
        physicalX, physicalY = self.pixelToPhysical(x, y)
        angleX, angleY = self.physicalToAngle(physicalX, physicalY)
        yOffset = self.getYOffset(height, angleY)
        xOffset = self.getXOffset(height, angleX, angleY)
        return xOffset, yOffset
    


