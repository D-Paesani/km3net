import utils as uu
import subprocess
import re


def parse_sensors(sss, param):
    ss = re.search(F'MON_{param}_VALUE = (.*)', sss).group(1).split(' ')
    adc = int(ss[0])
    val = float(ss[1].split('(')[1])
    unit = str(ss[2]).replace(')', '')
    return adc, val, unit

def parse_generic(sss, param):
    return re.search(F'{param} = (.*)', sss).group(1)

def execandparse(du, jc):
    cc = jc.command.format(ip=uu.getbaseip(int(du)), args=jc.cmd)
    print('--> JSC --> command --> ' +  cc)
    resp = subprocess.check_output(cc, shell=True).decode('utf-8')
    pp = {}
    pp['du'] = du
    for ii in jc.params:
        pp[ii] = jc.parser(resp, ii)
    return pp

class jcmd:
    
    command = 'python2 jsendcommand_dummy.py {ip} {args}'
    
    def __init__(self, cmd, parser, params, index=None):
        self.cmd = cmd
        self.parser = parser
        self.params = params
        self.index = index

    def exec(self, du, opts=None):
        return execandparse(du, self)
    
commands = dict(
    sensors    = jcmd(cmd='SENSOR_VALUES_GETALL', parser=parse_sensors,   params=['5V_I', 'LBL_I', 'DU_I', 'DU_IRTN', 'BPS_V', 'HYDRO_I', 'THEATSINK', 'TBOARD'], index=['ADC', 'VALUE', 'UNIT']),
    switch     = jcmd(cmd='SWITCH_CONTROL',       parser=parse_generic,   params=['SWITCHNUM', 'SWITCHSTATE']),
    rescue     = jcmd(cmd='RESCUE_ENABLE',        parser=parse_generic,   params=['ENABLESTATE']),
)

#Stato allarmi / rescue enable / alarm flag / alarm reset

