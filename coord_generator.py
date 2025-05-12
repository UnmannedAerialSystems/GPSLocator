import sys
sys.path.append("../")
from MAVez.Coordinate import Coordinate
from .geo_image import GeoImage
import numpy as np
import math

def generate_geo_images():

    end_coord = Coordinate(38.31583202378429, -76.5527183058615, 0, use_int=False)
    start_coord = Coordinate(38.31552770581607, -76.5509148682147, 0, use_int=False)
    count = 13

    distance = start_coord.distance_to(end_coord)
    heading = start_coord.bearing_to(end_coord)


    keypoint_attitudes = {
        0: {'alt': 20, 'yaw': 0, 'pitch': 0, 'roll': 0},
        5: {'alt': 22.08, 'yaw': -5, 'pitch': 1, 'roll': 0.5},
        10: {'alt': 19.66, 'yaw': 1, 'pitch': -1, 'roll': -1},
        15: {'alt': 20.73, 'yaw': -5, 'pitch': 1, 'roll': 0.5},
        20: {'alt': 20, 'yaw': 0, 'pitch': 0, 'roll': 0},
    }

    attitude_list = []

    current_kp = 0
    next_kp = 5

    for i in range(count + 1):
        if i == next_kp and next_kp < 20:
            current_kp = next_kp
            if next_kp < 20:
                next_kp += 5
        alt_slope = (keypoint_attitudes[next_kp]['alt'] - keypoint_attitudes[current_kp]['alt']) / (next_kp - current_kp)
        yaw_slope = (keypoint_attitudes[next_kp]['yaw'] - keypoint_attitudes[current_kp]['yaw']) / (next_kp - current_kp)
        pitch_slope = (keypoint_attitudes[next_kp]['pitch'] - keypoint_attitudes[current_kp]['pitch']) / (next_kp - current_kp)
        roll_slope = (keypoint_attitudes[next_kp]['roll'] - keypoint_attitudes[current_kp]['roll']) / (next_kp - current_kp)
        alt = round(keypoint_attitudes[current_kp]['alt'] + (i - current_kp) * alt_slope, 3)
        yaw = round(keypoint_attitudes[current_kp]['yaw'] + (i - current_kp) * yaw_slope + heading, 3)
        pitch = round(keypoint_attitudes[current_kp]['pitch'] + (i - current_kp) * pitch_slope, 3)
        roll = round(keypoint_attitudes[current_kp]['roll'] + (i - current_kp) * roll_slope, 3)
        attitude_list.append({'alt': alt, 'yaw': yaw, 'pitch': pitch, 'roll': roll})




    step = distance / 20

    current_coord = start_coord

    focal_length = 3.83
    sensor_width = 6.29
    sensor_height = 4.71
    res_x = 4056
    res_y = 3040

    directory = "../GPSLocator/test_images/"

    geo_images = []

    for i in range(count + 1):
        new_geo_image = GeoImage(
            image_path=f"{directory}{i:04d}.png",
            latitude=current_coord.lat,
            longitude=current_coord.lon,
            altitude=attitude_list[i]['alt'],
            roll=attitude_list[i]['roll'],
            pitch=attitude_list[i]['pitch'],
            heading=attitude_list[i]['yaw'],
            res_x=res_x,
            res_y=res_y,
            focal_length=focal_length,
            sensor_width=sensor_width,
            sensor_height=sensor_height,
            fov=78.3
        )
        geo_images.append(new_geo_image)
        current_coord = current_coord.offset_coordinate(step, heading)

    return geo_images



if __name__ == "__main__":
    geo_images = generate_geo_images()
    print(geo_images[0].get_coordinates(2028, 3040))
    print(geo_images[-1].get_coordinates(2028, 0))
