# GPSLocator



## Introduction
GPSLocator is a project for the PSU UAS club. The goal of this project is to accurately record GPS coordinates of targets detected in the field by our computer vision model. Once detected, the GPSLocator will convert the pixel coordinate to a GPS location based on the aircraft's current position, heading, and altitude. 

## Contents Overview
This project consists of multiple parts:
- [GeoSensor](#geosensor): Calculates position offset from pixel coordinates.
- **TODO**: Calculate actual positions based on current GPS location and heading.
- **TODO**: Record and map object locations.

## GeoSensor
**Latest Version: v1.0.0**
*TODO:*
- Add test cases to verify equations
- Perform small scale real-world test to check accuracy
### Classes: 
- GeoSensor: Contains constants used in calculation and methods for calculations.
    #### Methods
    - pixelToPhysical
        - *Input:  x, y - pixel coordinates*
        - *Output: physicalX, physicalY - physical distance from the bottom left of the sensor in meters*
        - *This method converts pixel coordinates to physical distances across the sensor.*
    - physicalToAngle
        - *Input:  physicalX, physicalY - physical distance from the bottom left of the sensor in meters*
        - *Output: angleX, angleY - angle in radians from the center of the sensor*
        - *This method converts physical distances to angles from the center of the sensor.*
    - getYOffset
        - *Input:  height - height of the sensor from the ground in meters*
        - *Input:  angleY - angle in the y direction in radians*
        - *Output: yOffset - offset in the y direction in meters*
        - *This method calculates the offset in the forwards (y) direction from the point directly below the sensor.*
    - getXOffset
        - *Input:  height - height of the sensor from the ground in meters*
        - *Input: angleX - angle in the x direction in radians*
        - *Input: angleY - angle in the y direction in radians*
        - *Output: xOffset - offset in the x direction in meters*
        - *This method calculates the offset in the sideways (x) direction from the point directly below the sensor.*
    - geoSensorIO
        - *Input:  x, y - pixel coordinates*
        - *height - height of the sensor from the ground in meters*
        - *Output: xOffset, yOffset - offsets in the x and y directions in meters*
        - *This is the main IO method for the GeoSensor module. It takes pixel coordinates and height as input and returns the offsets in the x and y directions.*

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
