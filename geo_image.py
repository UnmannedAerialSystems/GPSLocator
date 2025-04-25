import math
import sys
import cv2
sys.path.append("../")
from MAVez.Coordinate import Coordinate

EARTH_RADIUS = 6378137  # Earth's radius in meters


class GeoImage:
    def __init__(self, image_path, latitude, longitude, altitude, roll, pitch, heading, res_x, res_y, focal_length, sensor_width, sensor_height, index=-1, logger=None):
        '''
        image_path: path to the image file
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

        self.image = cv2.imread(image_path)
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.roll = math.radians(roll) # Convert from degrees to radians
        self.heading = math.radians(heading) # Convert from degrees to radians
        self.pitch = math.radians(pitch) # Convert from degrees to radians
        self.res_x = res_x
        self.res_y = res_y
        self.focal_length = focal_length / 1000  # Convert from mm to meters
        self.sensor_width = sensor_width / 1000  # Convert from mm to meters
        self.sensor_height = sensor_height / 1000  # Convert from mm to meters
        self.shape = self.image.shape
        self.logger = logger
        self.index = index


    def get_coordinates(self, x, y):
        '''
        Convert pixel coordinates to geographical coordinates.
        Input:  x, y - pixel coordinates
        Output: latitude, longitude - coordinates in degrees
        '''
        # Convert pixel coordinates to physical distances from the bottom left of the sensor
        physical_y = y * (self.sensor_height / self.res_y)
        physical_x = x * (self.sensor_width / self.res_x)
        
        # Convert physical distances to angles from the center of the sensor
        x_from_center = physical_x - (self.sensor_width / 2)
        y_from_center = physical_y - (self.sensor_height / 2)

        # Compensate for roll by rotating the point around the center of the sensor
        x_rotated = (x_from_center * math.cos(self.roll)) - (y_from_center * math.sin(self.roll))
        y_rotated = (x_from_center * math.sin(self.roll)) + (y_from_center * math.cos(self.roll))

        # Convert to angles across the sensor
        angle_x = math.atan((x_rotated) / math.hypot(self.focal_length, y_rotated))
        angle_y = math.atan((y_rotated) / self.focal_length)

        # Calculate offsets in the x and y directions
        x_offset = self.altitude / math.cos(angle_y + self.pitch) * math.tan(angle_x)
        y_offset = self.altitude * math.tan(angle_y + self.pitch)
        

        # Align the offsets with the heading
        lat_offset = x_offset * math.cos(self.heading) + y_offset * math.sin(self.heading)
        lon_offset = y_offset * math.cos(self.heading) - x_offset * math.sin(self.heading)

        # Calculate the new latitude and longitude
        new_latitude = self.latitude + (lat_offset / EARTH_RADIUS) * (180 / math.pi)
        new_longitude = self.longitude + (lon_offset / EARTH_RADIUS) * (180 / math.pi) / math.cos(self.latitude * math.pi / 180)

        # logging
        if self.logger:
            self.logger.info(f"Coordinates of pixel ({x}, {y}) in image {self.index}: ({new_latitude}, {new_longitude})")

        return new_latitude, new_longitude
    

    def get_pixels(self, coordinate):
        '''
        Convert geographical coordinates to pixel coordinates.
        Input:  latitude, longitude - coordinates in degrees
        Output: x, y - pixel coordinates
        '''
        latitude = coordinate.lat
        longitude = coordinate.lon

        # Calculate the offsets in meters
        lat_offset = (latitude - self.latitude) * (math.pi / 180) * EARTH_RADIUS
        lon_offset = (longitude - self.longitude) * (math.pi / 180) * EARTH_RADIUS * math.cos(self.latitude * math.pi / 180)

        # Reverse the heading alignment
        x_offset = lat_offset * math.cos(-self.heading) - lon_offset * math.sin(-self.heading)
        y_offset = lon_offset * math.cos(-self.heading) + lat_offset * math.sin(-self.heading)

        # Calculate the angles
        angle_x = math.atan(x_offset / (self.altitude / math.cos(self.pitch)))
        angle_y = math.atan(y_offset / self.altitude)

        # Convert angles to physical distances
        x_from_center = self.focal_length * math.tan(angle_x)
        y_from_center = self.focal_length * math.tan(angle_y)

        # Convert physical distances to pixel coordinates
        physical_x = x_from_center + (self.sensor_width / 2)
        physical_y = y_from_center + (self.sensor_height / 2)

        x_pixel = int(physical_x * (self.res_x / self.sensor_width))
        y_pixel = int(physical_y * (self.res_y / self.sensor_height))

        # logging
        if self.logger:
            self.logger.info(f"Pixel coordinates of ({latitude}, {longitude}) in image {self.index}: ({x_pixel}, {y_pixel})")

        return x_pixel, y_pixel
    
    
    def __contains__(self, coordinate):
        '''
        Check if the given coordinate is within the image bounds.
        Input:  coordinate - a tuple of (latitude, longitude)
        '''
        latitude = coordinate.lat
        longitude = coordinate.lon
        x_pixel, y_pixel = self.get_pixels(latitude, longitude)
        if 0 <= x_pixel < self.res_x and 0 <= y_pixel < self.res_y:
            # logging
            if self.logger:
                self.logger.info(f"Coordinate ({latitude}, {longitude}) is within image {self.index}.")
            return True
        else:
            # logging
            if self.logger:
                self.logger.info(f"Coordinate ({latitude}, {longitude}) is outside image {self.index}.")
            return False

def main():
    image = GeoImage(
        image_path="path/to/image.jpg",
        latitude=0,
        longitude=0,
        altitude=100,
        roll=0,
        pitch=0,
        heading=0,
        res_x=1920,
        res_y=1080,
        focal_length=15,
        sensor_width=36,
        sensor_height=20.3
    )


    test = image.get_coordinates(1919, 920)
    print(f"Coordinates: {test}")
    print(test in image)



if __name__ == "__main__":
    main()
        
    
