'''
geo_image.py
PSU UAS
Authors: Ted Tasman, Vlad Roiban
Date: 2025-05-16
Description: This module provides spatial data for UAS images, and enables conversion between pixel coordinates and geographical coordinates.
Version: v1.0.0
'''

import math
import sys
import cv2
sys.path.append("../")
from MAVez.Coordinate import Coordinate


class GeoImage:
    def __init__(self, image, coordinate, roll, pitch, heading, res_x, res_y, sensor_width, sensor_height, fov, index=-1, logger=None):
        '''
        image: cv2 image object
        latitude: latitude of the sensor in degrees
        longitude: longitude of the sensor in degrees
        altitude: altitude of the sensor in meters
        roll: roll of the sensor in degrees
        pitch: pitch of the sensor in degrees
        heading: heading of the sensor in degrees
        res_x: resolution of the sensor in the x direction (pixels)
        res_y: resolution of the sensor in the y direction (pixels)
        focal_length: focal length of the sensor in mm
        sensor_width: width of the sensor in mm
        sensor_height: height of the sensor in mm
        index: index of the image in the list of images
        logger: logger object for logging
        '''

        self.image = image
        self.coordinate = coordinate
        self.roll = math.radians((-roll)%360) # Convert from degrees to radians
        self.heading = math.radians((heading)%360) # Convert from degrees to radians
        self.pitch = math.radians((pitch)%360) # Convert from degrees to radians
        self.res_x = res_x
        self.res_y = res_y
        self.res_diagonal = (res_x ** 2 + res_y ** 2) ** 0.5
        self.sensor_width = sensor_width
        self.sensor_height = sensor_height
        self.sensor_diagonal = math.sqrt(self.sensor_width ** 2 + self.sensor_height ** 2)
        self.shape = self.image.shape
        self.logger = logger
        self.index = index

        # convert fov to radians
        if fov > math.pi*2: # if fov is in degrees
            self.fov = math.radians(fov)
            if self.logger:
                self.logger.info(f"Converted fov from degrees to radians: {self.fov}")
        else:
            self.fov = fov


    def get_coordinates(self, x, y):
        '''
        Convert pixel coordinates to geographical coordinates.
        Input:  x, y - pixel coordinates
        Output: Coordinate object with latitude, longitude, and altitude for the pixel
        '''

        # center the coordinates to convert to polar coordinates
        x = x - self.res_x / 2 # pixels
        y = self.res_y / 2 - y # pixels

        # convert pixel coordinates to meters
        x = x * (self.sensor_diagonal / self.res_diagonal) # meters
        y = y * (self.sensor_diagonal / self.res_diagonal)

        # radius is the distance from the center of the image to the pixel
        radius = math.sqrt(x ** 2 + y ** 2) # meters
        print(radius)
        # theta is the angle from the x-axis to the pixel (counter-clockwise)
        theta = math.atan2(x, y) # radians

        # phi is the angle from the z-axis to the pixel (direction of the camera)
        phi = radius / (self.sensor_diagonal) * self.fov # radians, assuming linear projection/pinhole camera model
        print("Phi out:", phi)
        # factor in vehicle attitude
        point_bearing = theta + self.heading # radians
        point_pitch = phi + self.pitch # radians

        # calculate the distance to the point
        distance = (self.coordinate.alt * 1000) * math.tan(point_pitch) # convert altitude to mm
        print("Distance out", distance)

        # calculate the latitude and longitude of the point
        target_coordinate = self.coordinate.offset_coordinate(distance / 1000, math.degrees(point_bearing)) # convert distance to meters

        if self.logger:
            self.logger.info(f"Converted pixel coordinates ({x}, {y}) to geographical coordinates ({target_coordinate.lat}, {target_coordinate.lon})")

        return target_coordinate


    def get_pixels(self, target_coordinate):
        '''
        Convert geographical coordinates to pixel coordinates.
        Input:  latitude, longitude - coordinates in degrees
        Output: x, y - pixel coordinates
        '''
        
        # get the distance and bearing to the target coordinate
        distance = self.coordinate.distance_to(target_coordinate) * 1000 # convert distance to mm
        print("Distance in:", distance)
        bearing = self.coordinate.bearing_to(target_coordinate)
        bearing = math.radians(bearing)

        # calculate the angle from the z-axis to the target coordinate, accounting for the pitch of the camera
        phi = math.atan2(distance, self.coordinate.alt * 1000) - self.pitch # radians, convert altitude to mm
        print("Phi in:", phi)
        # align the bearing with the camera heading
        theta = bearing - self.heading # radians
        # calculate the radius of the pixel
        radius = phi * (self.sensor_diagonal) / self.fov # meters
        print(radius)
        # calculate the pixel distance from the center of the image
        x = radius * math.sin(theta)
        y = radius * math.cos(theta)
        # convert distance to pixels
        x = x * (self.res_diagonal / self.sensor_diagonal)
        y = y * (self.res_diagonal / self.sensor_diagonal)
        # reset origin to top left corner of the image
        x = int(x + self.res_x / 2)
        y = int(self.res_y / 2 - y)

        if self.logger:
            self.logger.info(f"Converted geographical coordinates ({target_coordinate.lat}, {target_coordinate.lon}) to pixel coordinates ({x}, {y})")

        return x, y


    def __contains__(self, coordinate):
        '''
        Check if the given coordinate is within the image bounds.
        Input:  coordinate - a tuple of (latitude, longitude)
        '''
        x_pixel, y_pixel = self.get_pixels(coordinate)
        #print(f"Checking if pixel ({x_pixel}, {y_pixel}) is within image bounds ({self.res_x}, {self.res_y})")
        if 0 <= x_pixel < self.res_x and 0 <= y_pixel < self.res_y:
            # logging
            if self.logger:
                self.logger.info(f"Coordinate {coordinate} is within image {self.index}.")
            return True
        else:
            # logging
            if self.logger:
                self.logger.info(f"Coordinate {coordinate} is outside image {self.index}.")
            return False

def main2():
    image = GeoImage(
        image=cv2.imread("test_images/0000.png"),
        coordinate=Coordinate(-34, 76, 20, use_int=False),
        roll=0,
        pitch=0,
        heading=45,
        res_x=4056,
        res_y=3040,
        sensor_width=6.29,
        sensor_height=4.71,
        fov=78.3
    )
    tl_coords = [[],[]]
    tr_coords = [[],[]]
    br_coords = [[],[]]
    bl_coords = [[],[]]

    for i in range(0, 2028, 100):
        for j in range(0, 1520, 100):
            coord = image.get_coordinates(i, j)
            tl_coords[0].append(coord.lat)
            tl_coords[1].append(coord.lon)

    for i in range(2028, 4056, 100):
        for j in range(0, 1520, 100):
            coord = image.get_coordinates(i, j)
            tr_coords[0].append(coord.lat)
            tr_coords[1].append(coord.lon)

    for i in range(0, 2028, 100):
        for j in range(1520, 3040, 100):
            coord = image.get_coordinates(i, j)
            bl_coords[0].append(coord.lat)
            bl_coords[1].append(coord.lon)

    for i in range(2028, 4056, 100):
        for j in range(1520, 3040, 100):
            coord = image.get_coordinates(i, j)
            br_coords[0].append(coord.lat)
            br_coords[1].append(coord.lon)
    
    import matplotlib.pyplot as plt
    plt.scatter(tl_coords[1], tl_coords[0], c='red', label='Front Left')
    plt.scatter(tr_coords[1], tr_coords[0], c='blue', label='Front Right')
    plt.scatter(bl_coords[1], bl_coords[0], c='green', label='Back Left')
    plt.scatter(br_coords[1], br_coords[0], c='yellow', label='Back Right')
    plt.title("Geographical Coordinates")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()


    bl_pixels = [[],[]]
    for lat, lon in zip(bl_coords[0], bl_coords[1]):
        pixels = image.get_pixels(Coordinate(lat, lon, 0))
        bl_pixels[0].append(pixels[0])
        bl_pixels[1].append(pixels[1])
    
    br_pixels = [[],[]]
    for lat, lon in zip(br_coords[0], br_coords[1]):
        pixels = image.get_pixels(Coordinate(lat, lon, 0))
        br_pixels[0].append(pixels[0])
        br_pixels[1].append(pixels[1])
    
    tl_pixels = [[],[]]
    for lat, lon in zip(tl_coords[0], tl_coords[1]):
        pixels = image.get_pixels(Coordinate(lat, lon, 0))
        tl_pixels[0].append(pixels[0])
        tl_pixels[1].append(pixels[1])
    
    tr_pixels = [[],[]]
    for lat, lon in zip(tr_coords[0], tr_coords[1]):
        pixels = image.get_pixels(Coordinate(lat, lon, 0))
        tr_pixels[0].append(pixels[0])
        tr_pixels[1].append(pixels[1])
    
    plt.scatter(tl_pixels[0], tl_pixels[1], c='red', label='Front Left')
    plt.scatter(tr_pixels[0], tr_pixels[1], c='blue', label='Front Right')
    plt.scatter(bl_pixels[0], bl_pixels[1], c='green', label='Back Left')
    plt.scatter(br_pixels[0], br_pixels[1], c='yellow', label='Back Right')
    plt.title("Geographical Coordinates")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.show()
    

def main():
    image = GeoImage(
        image=cv2.imread("test_images/0000.png"),
        coordinate=Coordinate(-34, 76, 20, use_int=False),
        roll=0,
        pitch=0,
        heading=0,
        res_x=4056,
        res_y=3040,
        sensor_width=6.29,
        sensor_height=4.71,
        fov=78.3
    )
    x = 4056
    y = 0
    coord = image.get_coordinates(x, y)
    print(f"To Coordinates ({x}, {y}): ({coord.lat}, {coord.lon})")
    
    x_pixel, y_pixel = image.get_pixels(coord)
    print(f"To Pixels ({coord.lat}, {coord.lon}): ({x_pixel}, {y_pixel})")




if __name__ == "__main__":
    main2()
        
    
