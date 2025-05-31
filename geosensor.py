"""
DEPRECATED MODULE, USE geo_image.py INSTEAD


PSU UAS GEOSENSOR
Authors: Ted Tasman, Vlad Roiban
Date: 2024-09-26
Description: This module converts sensor coordinates to geospatial displacement.
Version: v2.1.0
"""

from math import atan, tan, cos, sin, hypot

class GeoSensor:
    # CONSTANTS -- Depending on the sensor, these values may change
    RESOLUTION_X = 1920         # resolution of the sensor in the x direction
    RESOLUTION_Y = 1080         # resolution of the sensor in the y direction
    FOCAL_LENGTH = 0.015        # focal length of the sensor in meters
    SENSOR_WIDTH = 0.036       # width of the sensor in meters
    SENSOR_HEIGHT = 0.0203      # height of the sensor in meters
    

    def pixelToPhysical(self, x: int, y: int) -> tuple:
        '''
        Input:  x, y - pixel coordinates
        Output: physicalX, physicalY - physical distance from the bottom left of the sensor in meters

        This method converts pixel coordinates to physical distances across the sensor.

        TESTS BUILT FOR 0.015 FOCAL LENGTH, 0.036 SENSOR WIDTH, 0.0203 SENSOR HEIGHT

        >>> geoSensor = GeoSensor()
        >>> geoSensor.pixelToPhysical(0, 0)
        (0.0, 0.0)
        >>> x1, y1 = geoSensor.pixelToPhysical(1440, 540)
        >>> math.isclose(x1, 0.027, rel_tol=1e-4)
        True
        >>> math.isclose(y1, 0.01015, rel_tol=1e-4)
        True
        >>> x2, y2 = geoSensor.pixelToPhysical(960, 810)
        >>> math.isclose(x2, 0.018, rel_tol=1e-4)
        True
        >>> math.isclose(y2, 0.015225, rel_tol=1e-4)
        True
        '''
        physicalY = y * (GeoSensor.SENSOR_HEIGHT / GeoSensor.RESOLUTION_Y)
        physicalX = x * (GeoSensor.SENSOR_WIDTH / GeoSensor.RESOLUTION_X)

        return physicalX, physicalY
    
    def physicalToAngle(self, physicalX: float | int, physicalY: float | int, roll: float | int) -> tuple:
        '''
        Input:  physicalX, physicalY - physical distance from the bottom left of the sensor in meters
                roll - roll of the sensor in radians
        Output: angleX, angleY - angle in radians from the center of the sensor

        This method converts physical distances to angles from the center of the sensor.

        TESTS BUILT FOR 0.015 FOCAL LENGTH, 0.036 SENSOR WIDTH, 0.0203 SENSOR HEIGHT

        >>> geoSensor = GeoSensor()
        >>> geoSensor.physicalToAngle(0.018, 0.01015, 0)
        (0.0, 0.0)
        >>> physicalX, physicalY = geoSensor.pixelToPhysical(1120, 540)
        >>> x1, y1 = geoSensor.physicalToAngle(physicalX, physicalY, 0)
        >>> math.isclose(x1, 0.1974, rel_tol=1e-4)
        True
        >>> math.isclose(y1, 0.0, rel_tol=1e-4)
        True
        >>> physicalX, physicalY = geoSensor.pixelToPhysical(1440, 540)
        >>> x2, y2 = geoSensor.physicalToAngle(physicalX, physicalY, 0)
        >>> math.isclose(x2, 0.54042, rel_tol=1e-4)
        True
        >>> math.isclose(y2, 0.0, rel_tol=1e-4)
        True
        '''
        # Convert physical x and y coordinates to be relative to center of sensor instead of bottom left of sensor
        xRelToCenter = physicalX - (GeoSensor.SENSOR_WIDTH / 2)
        yRelToCenter = physicalY - (GeoSensor.SENSOR_HEIGHT / 2)
        # Compensate for roll by rotating the point around the center of the sensor
        rollAdjustedRelToCenterX = cos(roll) * xRelToCenter - sin(roll) * yRelToCenter
        rollAdjustedRelToCenterY = sin(roll) * xRelToCenter + cos(roll) * yRelToCenter

        angleX = atan((rollAdjustedRelToCenterX) / hypot(GeoSensor.FOCAL_LENGTH, rollAdjustedRelToCenterY))
        angleY = atan((rollAdjustedRelToCenterY) / GeoSensor.FOCAL_LENGTH)

        return angleX, angleY
    
    def getYOffset(self, altitude: int | float, pitch: int | float, angleY: int | float) -> float:
        '''
        Input:  height - height of the sensor from the ground in meters
                pitch - pitch of the sensor in radians
                angleY - angle in the y direction in radians
        Output: yOffset - offset in the y direction in meters

        This method calculates the offset in the forwards (y) direction from the point directly below the sensor.

        >>> geoSensor = GeoSensor()
        >>> geoSensor.getYOffset(100, 0, 0)
        0.0
        '''
        yOffset = altitude * tan(angleY + pitch)
        return yOffset
    
    def getXOffset(self, altitude: float | int, pitch: int | float, angleX: float | int, angleY: float | int) -> float:
        '''
        Input:  height - height of the sensor from the ground in meters
                angleX - angle in the x direction in radians
                angleY - angle in the y direction in radians
                pitch - pitch of the sensor in radians
        Output: xOffset - offset in the x direction in meters

        This method calculates the offset in the sideways (x) direction from the point directly below the sensor.
        >>> geoSensor = GeoSensor()
        >>> geoSensor.getXOffset(100, 0, 0, 0)
        0.0
        '''
        xOffset = altitude / cos(angleY + pitch) * tan(angleX)
        return xOffset
    
    def geoSensorIO(self, x: int, y: int, height: int | float, roll: int | float, pitch: int | float) -> tuple:
        '''
        Input:  x, y - pixel coordinates
                height - height of the sensor from the ground in meters
                roll - roll of the sensor in radians
                pitch - pitch of the sensor in radians
        Output: xOffset, yOffset - offsets in the x and y directions in meters

        This is the main IO method for the GeoSensor module.
        It takes pixel coordinates and height as input and returns the offsets in the x and y directions.

        TESTS BUILT FOR 0.015 FOCAL LENGTH, 0.036 SENSOR WIDTH, 0.0203 SENSOR HEIGHT

        >>> geoSensor = GeoSensor()
        >>> geoSensor.geoSensorIO(960, 540, 100, 0, 0)
        (0.0, 0.0)
        >>> x1, y1 = geoSensor.geoSensorIO(1120, 540, 100, 0, 0)
        >>> math.isclose(x1, 20.0, rel_tol=1e-4)
        True
        >>> x2, y2 = geoSensor.geoSensorIO(1440, 540, 100, 0, 0)
        >>> math.isclose(x2, 60, rel_tol=1e-4)
        True
        >>> math.isclose(y2, 0.0, rel_tol=1e-4)
        True
        >>> x3, y3 = geoSensor.geoSensorIO(1440, 60, 100, 0, 0)
        >>> math.isclose(x3, 60, rel_tol=1e-4)
        True
        >>> math.isclose(y3, -60.148148148, rel_tol=1e-4)
        True
        >>> x4, y4 = geoSensor.geoSensorIO(960, 400, 100, 0, 0.1745)
        >>> math.isclose(x4, 0.0, rel_tol=1e-4)
        True
        >>> math.isclose(y4, 0.083511, rel_tol=1e-4)
        True
        >>> x5, y5 = geoSensor.geoSensorIO(1400, 844, 100, 0, 0.1745)
        >>> math.isclose(x5, 59.86873, rel_tol=1e-4)
        True
        >>> math.isclose(y5, 59.73472, rel_tol=1e-4)
        True
        >>> x6, y6 = geoSensor.geoSensorIO(1400, 236, 100, 0.1745, 0)
        >>> math.isclose(x6, 60.77843, rel_tol=1e-4)
        True
        >>> math.isclose(y6, -27.96645, rel_tol=1e-4)
        True
        >>> x7, y7 = geoSensor.geoSensorIO(1400, 236, 100, 0.1745, 0.1745)
        >>> math.isclose(x7, 58.81588, rel_tol=1e-4)
        True
        >>> math.isclose(y7, -9.85144, rel_tol=1e-4)
        True
        '''
        physicalX, physicalY = self.pixelToPhysical(x, y)
        angleX, angleY = self.physicalToAngle(physicalX, physicalY, roll)
        yOffset = self.getYOffset(height, pitch, angleY)
        xOffset = self.getXOffset(height, pitch, angleX, angleY)
        return xOffset, yOffset
    


if __name__ == "__main__":
    import doctest
    import math
    doctest.testmod()
    print("Doctests passed!")