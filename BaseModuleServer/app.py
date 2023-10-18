
from flask import Flask, Response, request, render_template
import jsc
import utils
import pandas as pd

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)
    
    
@app.route('/help', methods = ['GET'])
def help(): 
    return render_template('help.html')
    
@app.route('/sensors', methods = ['GET', 'POST'])
def sensors(): 
    resp = 'none'
    msg = 'none'
    table = 'none'
    try:
        du = int(request.form.get('du'))
        msg = F'Reading sensors from DU_{du}'
        resp = jsc.read_sensors(int(du)) 
        resp2 = resp.copy()
        resp2.pop('du')
        table = pd.DataFrame(resp, columns=[ii for ii in resp2], index=['ADC', 'VALUE', 'UNIT'])
        table = table.to_html(index=True)
    except:
        pass 
    return render_template('sensors.html', resp=resp, msg=msg, table=table)

@app.route('/dumpsensor/<duid>', methods = ['GET'])
def sensorsjson(duid):
    resp = {}
    try:
        resp = jsc.read_sensors(int(duid)) 
    except:
        pass 
    return resp
        
@app.route('/swcontrol', methods = ['GET', 'POST'])
def swcontrol(): 
    msg, table = 'none', 'none'
    dd = pd.DataFrame()
    try:
        du = (request.form.get('du'))
        sws = [int(ii) for ii in request.form.get('sws').split(' ')]
        state = int(request.form.get('state'))
        msg = F'Setting switch{"es" if len(sws) > 1 else ""} {sws} on DU_{du} to {state}'
        for ii in sws:
            resp = jsc.write_switches(du,ii,state)
            resp.pop('du')
            resp['switch'] = ii
            dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
        print(dd)
        table = dd.to_html(index=False)
    except:
        pass 
    return render_template('swcontrol.html', msg=msg, table=table)