from utils import *

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from io import BytesIO
from pathlib import Path

import json

SEGY_FNAME = 'uploads/temp.sgy'
BINARY_FNAME = 'uploads/temp.dat'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/update')
async def hello(request: Request):
    print('Hello')

@app.post('/update')
async def draw_shape(request: Request):
    request_body = await request.json()
    shape_type = request_body['shape_type']           
    step_x = request_body['step_x']
    step_z = request_body['step_z']
    shape_vel = request_body['shape_vel']
    shape_data = request_body['shape_data']
    vel_array = np.array(request_body['vel_array'], dtype=np.int32) 
    
    if shape_type == 'point':
        draw_circle(vel_array, shape_vel, shape_data['pointX'], shape_data['pointZ'], shape_data['radius'], step_x, step_z)
    if shape_type == 'rectangle':
        x0 = shape_data['x0']
        x1 = shape_data['x1']
        y0 = shape_data['y0']
        y1 = shape_data['y1']        
        draw_rect(vel_array, [[x0, y0], [x0, y1], [x1, y1], [x1, y0]], shape_vel, step_x, step_z)
    if shape_type == 'path':
        draw_path(vel_array, shape_data['path'], shape_vel, step_x, step_z)                   
   
    return vel_array.tolist()

@app.post('/save')
async def save_model(request: Request):
    request_body = await request.json()
    vel_array = np.array(request_body['vel_array'])
    step_x = request_body['step_x']
    step_z = request_body['step_z']
    fname = SEGY_FNAME
    if request_body['data_type'] == 'sgy':                    
        save_segy(vel_array.T, step_x, step_z, fname)            
    else:
        fname = BINARY_FNAME
        save_bin(vel_array, fname)    
        
        
    #with open(fname, 'rb') as binary_file:
    #    file_contents = binary_file.read()            

    
    return FileResponse(Path(fname))
         