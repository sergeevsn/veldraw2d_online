    const update_endpoint = 'https://sergeevsergei.ru/veldraw_api/update';
    const save_endpoint = 'https://sergeevsergei.ru/veldraw_api/save';
    const closed_endpoint = 'https://sergeevsergei.ru/veldraw_api/closed';
  
    var z_num = 501;
    var x_num = 501;
    var step_x = 5;
    var step_z = 5;
    var background_vel = 2000;
    var first_time = true;
    var current_path = "current path";
    var delete_state = false;
    var mode = 'rectangle';
    

    background_vel_array = [[]];

    function reset_graph(fetched=false) {                 
        if (!fetched) {
          console.log(typeof background_vel_array)
          background_vel_array = Array(z_num).fill(background_vel).map(() => Array(x_num).fill(background_vel));
          }
        else {
          console.log(typeof background_vel_array);
        }
          
        dragmode = 'drawrect'; 
        if (mode=='path') {
          dragmode = 'drawclosedpath';
        }
        if (mode=='point') {
          dragmode = 'selected';
        }
        xvl = Array.from({ length: x_num }, (v, i) =>  i * step_x);
        zvl = Array.from({ length: z_num }, (v, i) =>  i * step_z);        

        var data = [
        {
          z: background_vel_array,
          x: xvl,
          y: zvl,
          type: 'heatmap',
          hoverongaps: false,
        }
        ];     

        

        var layout = {
            title: {text: 'Глубинно-скоростная модель среды',  y:0.98, yanchor:'top', font: {weight: 'bold', color: 'rgb(0, 160, 138)'}},
            annotations: [],
            xaxis: {
                ticks: '',
                side: 'top',
                autosize: true,
                title: 'X, м',
                mirror: 'ticks',
                rangeslider: {visible:false},
            },
            yaxis: {
                ticks: '',
                ticksuffix: ' ',
                autorange: 'reversed',    
                       
                autosize: false,
                title: 'Z, м',
                mirror: 'ticks',
                rangeslider: {visible:false},
            },
            
            dragmode : dragmode,
            newshape : {
                fillcolor: "rgba(55,95,55,1)",
            },
            width: 900,
            height: 700,
            
        };     

        var config = {
          modeBarButtonsToRemove:['pan2d','select2d','lasso2d','resetScale2d', 'zoom2d', 'zoomin2d', 'zoomout2d', 'autoscale2d'],
          displayModeBar: true,
          showAxisDragHandles : false,
        }

        if (first_time) {
            
            Plotly.newPlot('heatmapDiv', data, layout,config);
          
            first_time = false;
          }
        else {
      
       
          Plotly.react('heatmapDiv', data, layout, config);          
        }  

    }    
    
    reset_graph();

    var modeSelector = document.getElementById('selMode');
    modeSelector.addEventListener('change', function(){
        if (this.value=='point') mode = 'point';                      
        if (this.value=='rectangle') mode = 'rectangle';
        if (this.value=='path') mode = 'path';
        reset_graph(fetched=true)
    })

    var heatmapPlot = document.getElementById('heatmapDiv');

    heatmapPlot.on('plotly_click', function(data){        
       
        document.getElementById('trDiffRadius').style.removeProperty('display');
        diff_x_ind = Number(data.points[0].pointIndex[1]);
        diff_z_ind = Number(data.points[0].pointIndex[0]);
        update_data = {
                  'shapes' : [ {
                    type: 'circle',
                    xref: 'x',
                    yref: 'y',
                    x0: (diff_x_ind-1)*step_x,
                    y0: (diff_z_ind-1)*step_z,
                    x1: (diff_x_ind)*step_x,
                    y1: (diff_z_ind)*step_z,          
                    fillcolor: 'blue',
                    line: {
                        color: 'white'
                          }
                  },],    
        }
       
        Plotly.relayout(heatmapPlot, update_data);
        document.getElementById('tblAddFigure').style.removeProperty('display');
       
    });

    heatmapPlot.on('plotly_relayout', function(data){ 
      if (!delete_state) {
        if (mode=='rectangle' || mode=='path'){
        
          if (data.shapes){
            const shape = data.shapes[data.shapes.length - 1]
            if (data.shapes.length > 1) {
              
                update_data = {
                    'shapes' : [shape],
                }
                Plotly.relayout(heatmapPlot, update_data)
            }   
            else {                 
                document.getElementById('tblAddFigure').style.removeProperty('display');          
                delete_state = false;                
            }
          }
        }     
      } 
      else {      
          document.getElementById('tblAddFigure').style.display = "none";
          delete_state = false;
      }
      
    })   
    
   
    const buttonNewModel = document.getElementById('btnNewModel');
    const buttonAddFigure = document.getElementById('btnAddFigure');
    const buttonRemoveFig = document.getElementById('btnRemoveFigure');
    const buttonSaveSegy = document.getElementById('btnSaveSegy');
    const buttonSaveBin = document.getElementById('btnSaveBin');
   

    buttonNewModel.addEventListener('click', function() { 
    
      const x_samples = Number(document.getElementById('xSamples').value);
      const z_samples = Number(document.getElementById('zSamples').value);
      const x_step = Number(document.getElementById('xStep').value);
      const z_step = Number(document.getElementById('zStep').value);
      const vel = Number(document.getElementById('bckgVel').value);         
      x_num = x_samples;
      z_num = z_samples;
      step_x = x_step;
      step_z = z_step;
      background_vel = vel;
      document.getElementById('tblAddFigure').style.display = "none";
      reset_graph();
         
    });

    
    buttonAddFigure.addEventListener('click', function() { 

        
      document.getElementById('tblAddFigure').style.display = "none";

      const shape = heatmapPlot.layout.shapes[0];      
      let shape_data = {x0 : shape.x0,
                        x1 : shape.x1,
                        y0 : shape.y0,
                        y1 : shape.y1,}
      
  
       
      if (mode == 'path') {
         
          shape_data = {              
              path : shape.path            
          }
      }

      if (mode == 'point') {
          
          shape_data = {
            pointX : (shape['x1'] + shape['x0'])/2,
            pointZ : (shape['y1'] + shape['y0'])/2,
            radius: Number(document.getElementById('diffRadius').value),
          }
      }    


      data_to_send = {
              shape_type : mode,    
              shape_data : shape_data,         
              step_x: step_x,
              step_z: step_z,              
              vel_array: background_vel_array,
              shape_vel: Number(document.getElementById('shapeVel').value)
          
       }  
       fetch(update_endpoint, {
                                method: 'POST',                                 
                                body: JSON.stringify(data_to_send),
                                headers: {'Content-Type':'application/json'} })
                                .then(response => response.json())
                                .then(data => 
                                  {
                                    background_vel_array = data;                              
                                    
                                    reset_graph(fetched=true);
                                  })       
       
    });

    buttonRemoveFig.addEventListener('click', function() { 
      update_data = {
                'shapes' : [],
            }
      delete_state = true;        
      Plotly.relayout(heatmapPlot, update_data)
        
    });

    buttonSaveSegy.onclick =  function() {save_data('sgy')};
    buttonSaveBin.onclick =  function() {save_data('dat')};

    function save_data(data_type) {
    
      data_to_send = {
            vel_array: background_vel_array,
            data_type: data_type,
            step_x: step_x,
            step_z: step_z,
      } 
      fetch(save_endpoint, {method: 'POST', body: JSON.stringify(data_to_send),
                                headers: {'Content-Type':'application/json'} })
                                .then(response => response.blob())
                                .then(blob => {
                                    var url = window.URL.createObjectURL(blob);
                                    var a = document.createElement('a');
                                    a.href = url;
                                    a.download = "velmodel."+data_type;
                                    document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
                                    a.click();    
                                    a.remove();  //afterwards we remove the element again         
                                });
    };

  window.addEventListener('beforeunload', function(e) {
     fetch(closed_endpoint, {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({'event': 'tab_closed'})
     });
  });

