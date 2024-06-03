from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import re
import cv2
import segyio
import io
import json

def parse_path(pathstr, sx, sz):
    new_string = re.sub("[A-Za-z]", ",", pathstr)
    coord_list = [round(float(x)) for x in new_string.split(",") if x]
    coupled_coord_list = []
    for i in range(len(coord_list)//2):        
        coupled_coord_list.append([coord_list[i*2]//sx, coord_list[i*2+1]//sz])
    return coupled_coord_list


app = Flask(__name__)
app.config['SEGY_FNAME'] = 'uploads/temp.sgy'
app.config['BINARY_FNAME'] = 'uploads/temp.dat'

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/update", methods=['POST'])
def fill_poly():
    if request.method == 'POST':
        #data = request.json
        #with open("request.json", "w") as file:
        #    json.dump(data, file)
           
        step_x = request.json['step_x']
        step_z = request.json['step_z']
        shape_vel = request.json['shape_vel']
        vel_array = np.array(request.json['vel_array'], dtype=np.int32)         
        if request.json['shape_type'] == "rectangle":
           x0 = int(request.json['shape_data']['x0']//step_x)
           y0 = int(request.json['shape_data']['y0']//step_z)
           y1 = int(request.json['shape_data']['y1']//step_z)
           x1 = int(request.json['shape_data']['x1']//step_x)
           

           if x0 > x1:
               x0, x1 = x1, x0
           if y0 > y1:
               y0, y1 = y1, y0
           if x0 < 0:
               x0 = 0
           if x1 < 0:
               x1 = 1
           if y0 < 0:
               y0 = 0
           if y1 <= 0:
               y0 = 1
           point_array = np.array([[x0, y0], [x0, y1], [x1, y1], [x1, y0]], dtype = np.int32)
           
               
           cv2.fillPoly(vel_array, [point_array], shape_vel)
           

        if request.json['shape_type'] == "path":
            path = request.json['shape_data']['path']
            unsorted_poly = np.array(parse_path(path, step_x, step_z), dtype=np.int32) 
            for point in unsorted_poly:
                if point[0] < 0:
                    point[0] = 0
                if point[1] < 0:
                    point[1] = 0
            cv2.fillPoly(vel_array, [unsorted_poly], shape_vel) 

        if request.json['shape_type'] == "point":
            radius = request.json['shape_data']['radius']//min([step_x, step_z])
            if radius == 0:
                radius = 1
            pointX = np.int32(round(request.json['shape_data']['pointX']/step_x))
            pointZ = np.int32(round(request.json['shape_data']['pointZ']/step_z))
            cv2.circle(vel_array, (pointX, pointZ), radius, shape_vel, -1)        
        
        return jsonify(vel_array.tolist())    


def save_segy(data, dx, dz):
    spec = segyio.spec()
    spec.samples=np.arange(data.shape[0])
    spec.ilines=[1]
    spec.xlines=range(data.shape[1])
    spec.sorting=2
    spec.format=1
    with segyio.create(app.config['SEGY_FNAME'], spec) as f:
        for i in spec.xlines:
            f.trace[i] = data[:, i]
            f.header[i][17] = i
            f.header[i][21] = i
            f.header[i][73] = i*dx
            f.header[i][77] = 0
        f.bin[segyio.BinField.Interval] = dz*1000

def save_bin(data):
    data.tofile(app.config['BINARY_FNAME'])       



@app.route("/save", methods=['POST'])
def save_file():
    if request.method == 'POST':
        vel_array = np.array(request.json['vel_array'])
        step_x = request.json['step_x']
        step_z = request.json['step_z']
        fname = app.config['SEGY_FNAME']
        if request.json['data_type'] == 'sgy':            
            save_segy(vel_array, step_x, step_z)            
        else:
            save_bin(vel_array)    
            fname = app.config['BINARY_FNAME']
        
        with open(fname, 'rb') as binary_file:
            file_contents = binary_file.read()            

        # Passing the file contents to send_file to provide for download
        return send_file(
            io.BytesIO(file_contents),
            as_attachment=True,
            download_name='velmodel'+ request.json['data_type'],
            mimetype='application/octet-stream'
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
