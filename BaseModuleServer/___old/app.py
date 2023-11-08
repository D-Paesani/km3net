
from flask import Flask, Response, request, render_template, abort
import jsc
import utils
import pandas as pd

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)    
    
@app.route('/help', methods = ['GET'])
@app.route('/', methods = ['GET'])
def f_help(): 
    return render_template('help.html')
    
@app.route('/sensors', methods = ['GET', 'POST'])
def f_sensors(): 
    templ = 'sensors.html'
    lastdu = '1'
    dd, ddt = [], []

    if request.method == 'POST':
        
        try:
            ss = request.form.get('du').rstrip(' ,').replace(', ', ',').replace(' ', ',')
            du = [int(ii) for ii in ss.split(',')]
        except:
            return render_template(templ, msg='Error retrieving DU list', table='', prefilldu=lastdu, datajson='', talbe='') 
        lastdu = ss
        
        for ii in du:
            try: 
                resp = jsc.read_sensors(int(ii))
                ddt.append(int(resp["du"]))
                resp.pop("du")
                dd.append(pd.DataFrame(resp, columns=[ii for ii in resp], index=['ADC', 'VALUE', 'UNIT']))
            except:
                return render_template(templ, msg=F'Error reading DU {ii}', table='', prefilldu=lastdu, datajson='') 
                              
        ddout = '\n\n\n'.join(['<br>' + '-'*50 + F'   DU{ddt[iii]:04d}   ' + '-'*50 + dd[iii].to_html(index=True) for iii in range(len(dd))])
        return render_template(templ, msg=F'Reading sensors on DU={du} with response:', table=ddout, prefilldu=lastdu)
                
    else:
        return render_template(templ, datajson='', msg='Waiting for user input', table='', prefilldu=lastdu)

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
    dd = pd.DataFrame()
    state = 2
    
    if request.method == 'POST':
        
        try:
            du = int(request.form.get('du'))
        except:
            return render_template(templ, msg='Error retrieving DU number', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
        lastdu = du
        
        try:
            swsss = request.form.get('sws').rstrip(' ,').replace(', ', ',').replace(' ', ',')
            sws = [int(ii) for ii in swsss.split(',')]
        except:
            return render_template(templ, msg='Error retrieving SW list', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate) 
        lastsws = swsss
        
        if request.form['submit'] == 'WRITE':
            try:
                state = int(request.form.get('state'))
            except:
                return render_template(templ, msg='Error retrieving STATE value', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
            laststate = state
            
        for ii in sws:
            try: 
                resp = jsc.write_switches(du,ii,state)
                resp.pop('du')
                resp['switch'] = ii
                dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
            except:
                return render_template(templ, msg=F'Error {("writing to" if state<2 else "reading").lower()} SW {ii} ', table=dd.to_html(index=False), prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)  
                         
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:04d} switch{"es" if len(sws) > 1 else ""} {sws} {F"to STATE={state}" if state<2 else ""} with response:'
        return render_template(templ, msg=msg, table=dd.to_html(index=False), prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)
                    
    else:
        return render_template(templ, msg='Waiting for user input', table='', prefilldu=lastdu, prefillsws=lastsws, prefillstate=laststate)


@app.route('/rescue', methods = ['GET', 'POST'])
def f_rescue(): 
    templ = 'rescue.html'
    lastdu, laststate = 1, '1'
    dd = pd.DataFrame()
    state = 2
    
    if request.method == 'POST':
        
        try:
            du = int(request.form.get('du'))
        except:
            return render_template(templ, msg='Error retrieving DU number', table='', prefilldu=lastdu, prefillstate=laststate)
        lastdu = du
            
        if request.form['submit'] == 'WRITE':
            try:
                state = int(request.form.get('state'))
            except:
                return render_template(templ, msg='Error retrieving STATE value', table='', prefilldu=lastdu, prefillstate=laststate)
            laststate = state
            
        try: 
            resp = jsc.write_rescueenable(du,state)
            resp.pop('du')
            dd = pd.concat([dd, pd.DataFrame(resp, index=[''])])
        except:
            return render_template(templ, msg=F'Error {("writing" if state<2 else "reading").lower()}', table=dd.to_html(index=False), prefilldu=lastdu, prefillstate=laststate)  
                         
        msg = F'{"Writing" if state<2 else "Reading"} DU{du:04d} rescue enable {F"to STATE={state}" if state<2 else ""} with response:'
        return render_template(templ, msg=msg, table=dd.to_html(index=False), prefilldu=lastdu, prefillstate=laststate)
                    
    else:
        return render_template(templ, msg='Waiting for user input', table='', prefilldu=lastdu, prefillstate=laststate)
