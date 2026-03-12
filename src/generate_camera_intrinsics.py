import math

def real_fov(fov_full_frame, crop_factor):
    return fov_full_frame / crop_factor

def crop_factor(sensor_width, sensor_length):
    full_frame_sensor_diagonal = math.sqrt(36*36 + 24*24)
    actual_frame_sensor_diagonal = math.sqrt(sensor_width * sensor_width + sensor_length * sensor_length)
    return full_frame_sensor_diagonal / actual_frame_sensor_diagonal

def get_sensor_size_from_area(area, aspectX, aspectY):
    # width * height = area
    # width / height = 2/3
    # height = 2*width / 3
    # area = (aspectY*width / aspectX) * width
    # aspectY * width*width = area*aspectX
    # width*width = (area*aspectX) / aspectY
    # width = sqrt((area*aspectX) / aspectY)
    width = math.sqrt((area*aspectX) / aspectY)
    height = area / width
    return width, height

def pixel_fov(resX, resY, CF, sensor_area, aspectX, aspectY):
    fov_x = resX * (real_fov(13, CF) / get_sensor_size_from_area(sensor_area, aspectX, aspectY)[0])
    fov_y = resY * (real_fov(13, CF) / get_sensor_size_from_area(sensor_area, aspectX, aspectY)[1])

    return fov_x, fov_y

def calculate(img_size, sensor_aspect, sensor_area):
    CF = crop_factor(get_sensor_size_from_area(sensor_area, sensor_aspect[0], sensor_aspect[1])[0], get_sensor_size_from_area(sensor_area, sensor_aspect[0], sensor_aspect[1])[1])
    fov = pixel_fov(img_size[0], img_size[1], CF, sensor_area, sensor_aspect[0], sensor_aspect[1])
    return fov

fov_calculated = calculate([3840, 2160], [3, 2], 12.2)
print("Pixel FOV:", fov_calculated)