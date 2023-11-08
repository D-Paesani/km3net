#Stato allarmi / rescue enable / alarm flag / alarm reset
import utils
import os
import subprocess
import re

command = 'python2 jsendcommand_dummy.py {ip} {args}'
sensors_toparse = ['5V_I', 'LBL_I', 'DU_I', 'DU_IRTN', 'BPS_V', 'HYDRO_I', 'THEATSINK', 'TBOARD']

def cmd_exec(du, args):
    cc = command.format(ip=utils.getbaseip(int(du)), args=args)
    print("--> JSC --> command --> " +  cc)
    return subprocess.check_output(cc, shell=True).decode('utf-8')

def parse_sensors(sss, param):
    ss = re.search(F'MON_{param}_VALUE = (.*)', sss).group(1).split(' ')
    adc = int(ss[0])
    val = float(ss[1].split('(')[1])
    unit = str(ss[2]).replace(')', '')
    return adc, val, unit

def parse_resp(sss, param):
    return re.search(F'{param} = (.*)', sss).group(1)

def execandparse(du, cmd, params, parser):
    resp = cmd_exec(du=du, args=cmd)
    pp = {}
    pp["du"] = du
    for ii in params:
        pp[ii] = parser(resp, ii)
    return pp

def read_sensors(du):
    return execandparse(du=du, cmd='SENSOR_VALUES_GETALL', params=sensors_toparse, parser=parse_sensors)

def write_switches(du, swn, sws):
    return execandparse(du=du, cmd=F'SWITCH_CONTROL {swn} {sws}', params=['SWITCHNUM', 'SWITCHSTATE'], parser=parse_resp)

def write_rescueenable(du, state):
    return execandparse(du=du, cmd=F'RESCUE_ENABLE {state}', params=['ENABLESTATE'], parser=parse_resp)


