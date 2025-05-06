import math
import sys
import cv2
sys.path.append("../")
from MAVez.Coordinate import Coordinate

EARTH_RADIUS = 6378137  # Earth's radius in meters


class GeoImage:
    def __init__(self, image_path, latitude, longitude, altitude, roll, pitch, heading, res_x, res_y, focal_length, sensor_width, sensor_height, index=-1, logger=None, fov=None):
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
        self.roll = math.radians((-roll)%360) # Convert from degrees to radians
        self.heading = math.radians((heading)%360) # Convert from degrees to radians
        self.pitch = math.radians((pitch)%360) # Convert from degrees to radians
        self.res_x = res_x
        self.res_y = res_y
        self.focal_length = focal_length / 1000  # Convert from mm to meters
        self.sensor_width = sensor_width / 1000  # Convert from mm to meters
        self.sensor_height = sensor_height / 1000  # Convert from mm to meters
        self.shape = self.image.shape
        self.logger = logger
        self.index = index
        if fov is not None:
            self.focal_length = self.focal_length_from_fov(fov)


    def get_coordinates(self, x, y):
        '''
        Convert pixel coordinates to geographical coordinates.
        Input:  x, y - pixel coordinates
        Output: latitude, longitude - coordinates in degrees
        '''

        # convert pixel coordinate basis to bottom left of the sensor
        #y = self.res_y - y

        # Convert pixel coordinates to physical distances from the bottom left of the sensor
        physical_y = (self.res_y - y) * (self.sensor_height / self.res_y)
        physical_x = x * (self.sensor_width / self.res_x)
        print(f"physical_x: {physical_x}, physical_y: {physical_y}")
        
        # convert absolute distances to displacement from center
        x_from_center = physical_x - (self.sensor_width / 2)
        y_from_center = physical_y - (self.sensor_height / 2)
        print(f"x_from_center: {x_from_center}, y_from_center: {y_from_center}")
        
        # Convert to angles across the sensor
        angle_x = math.atan((x_from_center) / self.focal_length)
        angle_y = math.atan((y_from_center) / self.focal_length)
        print(f"angle_x: {angle_x}, angle_y: {angle_y}")
        
        # Fire ray out from sensor assuming level ground.
        x_offset = self.altitude / math.cos(angle_y + self.pitch) * math.tan(angle_x + self.roll)
        y_offset = self.altitude / math.cos(angle_x + self.roll) * math.tan(angle_y + self.pitch)
        print(f"x_offset: {x_offset}, y_offset: {y_offset}")
        
        # Align the offsets with the heading
        north_offset = y_offset * math.cos(self.heading) - x_offset * math.sin(self.heading)
        east_offset = y_offset * math.sin(self.heading) + x_offset * math.cos(self.heading)
        print(f"north_offset: {north_offset}, east_offset: {east_offset}")
        
        # Calculate the new latitude and longitude
        new_latitude = self.latitude + (north_offset / EARTH_RADIUS) * (180 / math.pi)
        new_longitude = self.longitude + (east_offset / EARTH_RADIUS) * (180 / math.pi) / math.cos(math.radians(self.latitude))


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
        
        distance = coordinate.distance_to(Coordinate(self.latitude, self.longitude, 0))
        bearing = coordinate.bearing_to(Coordinate(self.latitude, self.longitude, 0))
        bearing = math.radians(bearing)

        # Align bearing with the heading
        theta = (bearing - self.heading) % (2 * math.pi)

        # offsets in the x and y directions
        y_offset = -distance * math.cos(bearing)
        x_offset = -distance * math.sin(bearing)

        #alpha = 
        
        




        # logging
        if self.logger:
            self.logger.info(f"Pixel coordinates of {coordinate} in image {self.index}: ({x_pixel}, {y_pixel})")

        return x_pixel, y_pixel


    def focal_length_from_fov(self, fov):

        # get diagonal sensor size
        d = math.sqrt((self.sensor_width) ** 2 + (self.sensor_height) ** 2)

        fov_rad = math.radians(fov)

        # calculate focal length
        focal_length = (d / 2) / math.tan(fov_rad / 2)
        return focal_length
    
    def __contains__(self, coordinate):
        '''
        Check if the given coordinate is within the image bounds.
        Input:  coordinate - a tuple of (latitude, longitude)
        '''
        x_pixel, y_pixel = self.get_pixels(coordinate)
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
        image_path="test_images/0000.png",
        latitude=0,
        longitude=0,
        altitude=20,
        roll=0,
        pitch=5,
        heading=0,
        res_x=4056,
        res_y=3040,
        focal_length=3.83,
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
            lat, lon = image.get_coordinates(i, j)
            tl_coords[0].append(lat)
            tl_coords[1].append(lon)

    for i in range(2028, 4056, 100):
        for j in range(0, 1520, 100):
            lat, lon = image.get_coordinates(i, j)
            tr_coords[0].append(lat)
            tr_coords[1].append(lon)

    for i in range(0, 2028, 100):
        for j in range(1520, 3040, 100):
            lat, lon = image.get_coordinates(i, j)
            bl_coords[0].append(lat)
            bl_coords[1].append(lon)

    for i in range(2028, 4056, 100):
        for j in range(1520, 3040, 100):
            lat, lon = image.get_coordinates(i, j)
            br_coords[0].append(lat)
            br_coords[1].append(lon)
    
    import matplotlib.pyplot as plt
    plt.scatter(tl_coords[1], tl_coords[0], c='red', label='Top Left')
    plt.scatter(tr_coords[1], tr_coords[0], c='blue', label='Top Right')
    plt.scatter(bl_coords[1], bl_coords[0], c='green', label='Bottom Left')
    plt.scatter(br_coords[1], br_coords[0], c='yellow', label='Bottom Right')
    plt.title("Geographical Coordinates")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()
    

def main():
    image = GeoImage(
        image_path="test_images/0000.png",
        latitude=0,
        longitude=0,
        altitude=20,
        roll=0,
        pitch=45,
        heading=0,
        res_x=4056,
        res_y=3040,
        focal_length=3.83,
        sensor_width=6.29,
        sensor_height=4.71,
        fov=78.3
    )
    lat, lon = image.get_coordinates(1234, 1234)
    print(f"Coordinates of pixel (1234, 1234): ({lat}, {lon})")
    
    x_pixel, y_pixel = image.get_pixels(Coordinate(lat, lon, 0))
    print(f"Pixel coordinates of ({lat}, {lon}): ({x_pixel}, {y_pixel})")




if __name__ == "__main__":
    main2()
        
    
