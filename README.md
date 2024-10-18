# GPSLocator



## Introduction
GPSLocator is a project for the PSU UAS club. The goal of this project is to accurately record GPS coordinates of targets detected in the field by our computer vision model. Once detected, the GPSLocator will convert the pixel coordinate to a GPS location based on the aircraft's current position, heading, and altitude. 

## Contents Overview
This project consists of multiple parts:
- [GeoSensor](#geosensor): Calculates position offset from pixel coordinates.
- **TODO**: Calculate actual positions based on current GPS location and heading.
- **TODO**: Record and map object locations.

## TargetMapper

**Latest Version: v1.0.0**
#### Future Additions:
- ID Functionality for targets
- TESTING

### Classes:
- Craft: Maintains craft position and target list
    - Init: (lat: float=0, lon: float=0, alt: float=0, heading: float=0)
    - Creates a GeoSensor object
    #### Methods:
    - update(lat: float, lon: float, alt: float, heading: float)
        - *Input:  lat - craft GPS latitude*
        - *Input:  lon - craft GPS longitude*
        - *Input:  alt - craft altitude in meters*
        - *Input:  heading - craft compass heading in degrees from North*
        - *Output: None*
        - *Updates the craft position and attitude*
    - getDisplacement(x: int, y: int) -> tuple
        - *Input:  x, y - pixel coordinates*
        - *Output: targetX, targetY - displacement in X and Y direction to target in meters*
        - *Uses the GeoSensor module to convert pixel coordinates into a physical displacement aligned to compass North.*
    - getTarget(x: int, y: int)
        - *Input:   x, y - pixel coordinates*
        - *Output:  Target object*
        - *Calls getDisplacement and converts the x and y displacement into GPS coordinates, then creates a Target object at that location. This target is also added to the craft's target list.*
- Target: Holds target GPS coordinates
    - Init: (lat: float, lon: float)
    #### Methods:
    - update(lat: float, lon: float)
        - *Input:  lat - craft GPS latitude*
        - *Input:  lon - craft GPS longitude*
        - *Output: None*
        - *Updates target GPS coordinates*

## GeoSensor

**Latest Version: v1.0.0**
#### Future Additions:
- TESTING

### Classes: 
- GeoSensor: Contains constants used in calculation and methods for calculations.
    #### Methods:
    - pixelToPhysical(int x, int x) -> tuple
        - *Input:  x, y - pixel coordinates*
        - *Output: physicalX, physicalY - physical distance from the bottom left of the sensor in meters*
        - *Converts pixel coordinates to physical distances across the sensor.*
    - physicalToAngle(float physicalX, float physicalY) -> tuple
        - *Input:  physicalX, physicalY - physical distance from the bottom left of the sensor in meters*
        - *Output: angleX, angleY - angle in radians from the center of the sensor*
        - *Converts physical distances to angles from the center of the sensor.*
    - getYOffset(float height, float angleY) -> float
        - *Input:  height - height of the sensor from the ground in meters*
        - *Input:  angleY - angle in the y direction in radians*
        - *Output: yOffset - offset in the y direction in meters*
        - *Calculates the offset in the forwards (y) direction from the point directly below the sensor.*
    - getXOffset(float height, float angleX, float angleY) -> float
        - *Input:  height - height of the sensor from the ground in meters*
        - *Input:  angleX - angle in the x direction in radians*
        - *Input:  angleY - angle in the y direction in radians*
        - *Output: xOffset - offset in the x direction in meters*
        - *Calculates the offset in the sideways (x) direction from the point directly below the sensor.*
    - geoSensorIO(int x, int y) -> tuple
        - *Input:  x, y - pixel coordinates*
        - *height - height of the sensor from the ground in meters*
        - *Output: xOffset, yOffset - offsets in the x and y directions in meters*
        - *Main IO method for the GeoSensor module. Takes pixel coordinates and height as input and returns the offsets in the x and y directions.*

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
