import re
import cv2
import numpy as np
import segyio
from typing import Union, List

SHAPE_JSON_COMMON_FIELD = ['shape_type', 'shape_vel', 'step_x', 'step_z']

def parse_path(pathstr : str, sx : float = 1, sz : float = 1) -> list :
    ''' Парсит SVG-путь из Plotly в список координат в формате [[x0, y0], [x1, y1] ... [xn, yn]] '''
    new_string = re.sub("[A-Za-z]", ",", pathstr)
    coord_list = [round(float(x)) for x in new_string.split(",") if x]
    coupled_coord_list = []
    for i in range(len(coord_list)//2):        
        coupled_coord_list.append([coord_list[i*2]//sx, coord_list[i*2+1]//sz])
    return coupled_coord_list


def validate_shape_json(json : str) -> bool:
    ''' Проверяет входящий json на наличие нужных полей и адекватность значений '''

    return True

def draw_rect(matrix : np.ndarray, coordinates : Union[List[List], np.ndarray], velocity : float, step_x : float, step_z : float) -> bool:
    ''' Рисует прямоугольник по 2-м точкам '''
    for i in range(4):
        coordinates[i][0] = np.int32(round(coordinates[i][0]/step_x))
        coordinates[i][1] = np.int32(round(coordinates[i][1]/step_z))  
    point_array = np.array(coordinates, dtype = np.int32)
    print(point_array)
    cv2.fillPoly(matrix, [point_array], velocity)
    return True

def draw_path(matrix : np.ndarray, path : str, velocity : float, step_x : float, step_z : float) -> bool:
    coord_list = parse_path(path, step_x, step_z)
    if not coord_list:
        return False
    unsorted_poly = np.array(coord_list, dtype=np.int32) 
    for point in unsorted_poly:
        if point[0] < 0:
            point[0] = 0
        if point[1] < 0:
            point[1] = 0
    cv2.fillPoly(matrix, [unsorted_poly], velocity) 
    return True

def draw_circle(matrix : np.ndarray, velocity : float, center_x : Union[float, int], center_z : Union[float, int], 
                radius : Union[int, float], step_x : float, step_z : float)  -> bool:
    radius = np.int32(round(radius/max(step_x, step_z)))
    if radius == 0:
        radius = 1
    pointX = np.int32(round(center_x/step_x))
    pointZ = np.int32(round(center_z/step_z))

    cv2.circle(matrix, (pointX, pointZ), radius, velocity, -1)  
    return True

def save_segy(data : np.ndarray, dx : Union[float, int], dz : Union[float, int], fname : str):
    spec = segyio.spec()
    spec.samples=np.arange(data.shape[1])
    spec.ilines=[1]
    spec.xlines=range(data.shape[0])
    spec.sorting=2
    spec.format=1
    with segyio.create(fname, spec) as f:
        for i in spec.xlines:
            f.trace[i] = data[i]
            f.header[i][17] = i
            f.header[i][21] = i
            f.header[i][73] = i*dx
            f.header[i][77] = 0
        f.bin[segyio.BinField.Interval] = dz*1000

def save_bin(data : np.ndarray, fname : str):
    data.tofile(fname)            



