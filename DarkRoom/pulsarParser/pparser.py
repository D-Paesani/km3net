#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *

def FillGraph(gra, x, y, ex, ey): 
    n = gra.GetN() #for backwards compatibility
    gra.SetPoint(n, x,y)
    gra.SetPointError(n, ex, ey)
    return n+1

def parsefile(infile, runid=None):
    fpars = np.empty((18,4))
    fpars[:] = np.nan
    histos = []
    
    runtag = F'{"" if runid==None else F"run{runid}"}'
    gmeans, gsigmas = TGraphErrors(), TGraphErrors()
    for ggg, gtitl, ytitl in zip([gmeans, gsigmas], ['means', 'sigmas'], ['mean [ns]', 'sigmas [ns]']):
        ggg.GetXaxis().SetTitle('DOM #')
        ggg.SetMarkerStyle(20)
        ggg.SetTitle(runtag+' '+gtitl)
        ggg.GetYaxis().SetTitle(ytitl)

    for hidx, ihist in enumerate(infile.GetListOfKeys()):
        nn = ihist.GetName()
        if nn in ['h0', 'h1', 'META']: continue
        nam = F'{"" if runid==None else F"run{runid}_"}dom{nn[6:8]}'
        num = int(nn[6:8])
        hh = infile.Get(nn).Clone()
        hh.SetName(nam)
        hh.SetTitle(nam)
        hh.GetXaxis().SetTitle(nam + ' [ns]')
        histos.append(hh)
        for ff in hh.GetListOfFunctions():
            if ff.GetName() != 'f1': continue
            fpars[num-1] = np.array([ff.GetParameter(1),ff.GetParameter(2),ff.GetParError(1),ff.GetParError(2)])
            FillGraph(gmeans, num, fpars[num-1,0], 0, fpars[num-1,2])
            FillGraph(gsigmas, num, fpars[num-1,1], 0, fpars[num-1,3])
        # ff = hh.GetListOfFunctions().FindObject('f1')

    return histos, fpars, (gmeans,gsigmas)     
