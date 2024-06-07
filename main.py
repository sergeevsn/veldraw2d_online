from utils import *

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from io import BytesIO
from pathlib import Path

import os
import shutil

import json

UPLOAD_FOLDER = 'uploads'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
def on_shuttdown():
    for fname in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, fname))

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
    fname =  os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy')
    if request_body['data_type'] == 'sgy':                    
        save_segy(vel_array.T, step_x, step_z, fname)            
    else:
        fname = os.path.join(UPLOAD_FOLDER, f'{request.client.host}.bin')
        save_bin(vel_array, fname)

    
    return FileResponse(Path(fname))
         
@app.post('/closed')
async def on_closed(request: Request):
    if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.bin')):
        os.remove(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.bin'))
    if os.path.exists(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy')):
        os.remove(os.path.join(UPLOAD_FOLDER, f'{request.client.host}.sgy'))

