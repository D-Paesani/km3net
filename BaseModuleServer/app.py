
from flask import Flask, Response, request, render_template, abort
import jsc
import utils
import pandas as pd

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)    
    
@app.route('/help', methods = ['GET'])
def f_help(): 
    return render_template('help.html')
    
@app.route('/sensors', methods = ['GET', 'POST'])
def f_sensors(): 
    templ = 'sensors.html'
    lastdu = 1
    du, resp = None, None

    if request.method == 'POST':
        try:
            du = int(request.form.get('du'))
            resp = jsc.read_sensors(int(du))
        except: 
            pass
    
        if None in [du, resp]:
            msg = 'Error reading DU'
            datajson = ''
            table = ''
        else:
            lastdu = du
            msg = F'Reading sensors from DU {du}'
            datajson = resp.copy()
            resp.pop('du')
            table = pd.DataFrame(resp, columns=[ii for ii in resp], index=['ADC', 'VALUE', 'UNIT'])
            table = table.to_html(index=True)
            
    elif request.method == 'GET':
        datajson = ''
        table = ''
        msg = 'Waiting for user input'
        
    return render_template(templ, datajson=datajson, msg=msg, table=table, prefilldu=lastdu)

@app.route('/dumpsensor/<duid>', methods = ['GET'])
def f_dumpsensor(duid):
    resp = {}
    try:
        resp = jsc.read_sensors(int(duid)) 
    except:
        abort(404)
    return resp
        
@app.route('/swcontrol', methods = ['GET', 'POST'])
def f_swcontrol(): 
    templ = 'swcontrol.html'
    lastdu, laststate, lastsws = 1, 1, '1'
    du, resp = None, None
    dd = pd.DataFrame()
    
    if request.method == 'POST':
        
        try:
            du = int(request.form.get('du'))
        except:
            return render_template(templ, msg='Error retrieving DU number', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
        lastdu = du
        
        try:
            sws = [int(ii) for ii in request.form.get('sws').replace(' ', ',').split(',')]
        except:
            return render_template(templ, msg='Error retrieving SW list', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate) 
        lastsws = request.form.get('sws').replace(' ', ',')
        
        if request.form['submit'] == 'WRITE':
            writem, action = True, 'WRITING to'
            try:
                state = int(request.form.get('state'))
            except:
                return render_template(templ, msg='Error retrieving STATE value', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
            laststate = state
        else:
            writem, action = False, 'READING'
            
        for ii in sws:
            try: 
                resp = jsc.write_switches(du,ii,state) if writem else jsc.read_switches(du,ii)
                resp.pop('du')
                resp['switch'] = ii
                dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
            except:
                return render_template(templ, msg=F'Error {("writing to" if writem else "reading").lower()} SW {ii} ', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)  
                         
            msg = F'{action} switch{"es" if len(sws) > 1 else ""} {sws} on DU {du} to with response:'
        return render_template(templ, msg=msg, table=dd.to_html(index=False), prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
                    
    else:
        
        return render_template(templ, msg='Waiting for user input', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
