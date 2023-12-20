#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *

def FillGraph(gra, x, y, ex, ey):
    gra.AddPoint(x, y)
    n = gra.GetN()
    gra.SetPointError(n-1, ex, ey)
    return n

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

    return histos, fpars, (gmeans,gsigmas)     


# EXAMPLE ################################################################################################################################################################################################################################################################################################################################################################################

runs = [768,770,785,787,789]
colorz = [kMagenta, kRed, kBlue, kGreen, kBlack]
infiles = [TFile(F'../data/KM3NeT_00000168_00000{ii}__LASER_PATCHED_PMT08_t73_464_L0__EXAMPLE.JPulsar.PMT08.root') for ii in runs] 
plotout = './out/%s.pdf'

cc = TCanvas('cc','cc',1600,800)
cc.cd()

for ii, ff in enumerate(infiles):
    histos, fitpars, graphs = parsefile(ff, runs[ii])
    gmeans, gsigmas = graphs[0], graphs[1]
    gmeans.SetName(F'nn{ii}')
    gmeans.SetMarkerColor(colorz[ii])
    gmeans.GetYaxis().SetRangeUser(200,230)      
    gmeans.DrawClone('AP' if ii == 0 else 'P same')
    
cc.BuildLegend(0.9,0.2,1.0,0.8)
cc.SaveAs(plotout%F'prova__{"_".join(str(rrr) for rrr in runs)}')  