#daniele.paesani@lns.infn.it

import numpy as np
import ROOT

def FillGraph(gra, x, y, ex, ey): 
    n = gra.GetN() #for backwards compatibility
    gra.SetPoint(n, x,y)
    gra.SetPointError(n, ex, ey)
    return n+1

def parsefile(infile, runid=None):

    nparfit = 4
    nfloor = 18
    fpars =     np.empty((nfloor,nparfit))
    fparerrs =  np.empty((nfloor,nparfit))
    fchi2 = np.empty(nfloor)
    fpars[:] = np.nan
    fparerrs[:] = np.nan
    fchi2[:] = np.nan
    histos = []
    
    runtag = F'{"" if runid==None else F"run{runid}"}'
    graphs = [ROOT.TGraphErrors()]*(nparfit+1)
    graphs = [ROOT.TGraphErrors(),ROOT.TGraphErrors(),ROOT.TGraphErrors(),ROOT.TGraphErrors(),ROOT.TGraphErrors()]
    
    for ggg, ytitl in zip(graphs, ['norm [entries]', 'mean [ns]', 'sigma [ns]', 'backg [entries]', 'chi2red']):
        ggg.GetXaxis().SetTitle('DOM #')
        ggg.SetMarkerStyle(20)
        ggg.SetTitle(runtag + ' ' + ytitl.split(' [')[0])
        ggg.SetName(ytitl.split(' [')[0])
        ggg.GetYaxis().SetTitle(ytitl)

    for hidx, ihist in enumerate(infile.GetListOfKeys()):

        nn = ihist.GetName()
        if nn in ['h0', 'h1', 'META']: continue
        nam = F'{"" if runid==None else F"run{runid}_"}dom{nn[6:8]}'
        num = int(nn[6:8])
        hh = infile.Get(nn).Clone()
        hh.SetName(nam)
        hh.SetTitle(nam)
        hh.GetXaxis().SetTitle('t [ns]')
        hh.GetYaxis().SetTitle('Entries')
        histos.append(hh)
                
        for ff in hh.GetListOfFunctions():
            if ff.GetName() != 'f1': continue
            #norm, media, sigma, flat 
            fchi2[num-1] =      ff.GetChisquare() / ff.GetNDF()
            fpars[num-1] =      np.array([ff.GetParameter(ii) for ii in range(nparfit)])
            fparerrs[num-1] =   np.array([ff.GetParError(ii) for ii in range(nparfit)])
            for itofill, tofill in enumerate(graphs): 
                if itofill == 4 and (not np.isnan(fchi2[num-1])):
                    FillGraph(tofill, num, fchi2[num-1], 0, 0)   
                    break
                FillGraph(tofill,  num, fpars[num-1,itofill], 0, fparerrs[num-1,itofill])

    return histos, fpars, fparerrs, fchi2, graphs     
