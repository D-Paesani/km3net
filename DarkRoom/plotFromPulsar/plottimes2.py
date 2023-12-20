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

runs = [(170, 3598, 15), (152, 3411, 15)] 
salvacome= 'giovanna'

colorz = [kMagenta, kRed, kBlue, kGreen, kBlack]

plotout = './out/%s.pdf'

cc = TCanvas('cc','cc',1600,800)
cc.cd()

diffs =  np.zeros(18)


for ii, rr in enumerate(runs):
    
    fname = F'../data/KM3NeT_00000{rr[0]:03}_0000{rr[1]:04}__LASER_PATCHED_PMT{rr[2]:02}_L0.JPulsar.PMT{rr[2]:02}.root'
    infile = TFile(fname)
    histos, fitpars, graphs = parsefile(infile, runs[ii])
        
    gmeans, gsigmas = graphs[0], graphs[1]
    
    tag = F'det{rr[0]:03}_run{rr[1]:04}_pmt{rr[2]:02}'
    gmeans.SetNameTitle(tag, tag)
    gmeans.SetMarkerColor(colorz[ii])
    gmeans.GetYaxis().SetRangeUser(-3500,1000)      
    gmeans.DrawClone('AP' if ii == 0 else 'P same')
    
    cc.BuildLegend(0.9,0.2,1.0,0.8)
    cc.SaveAs(plotout%salvacome)  
    
    print()
    
    for ll in range(18):
        print(tag, F'_dom{ll:02} ---->  {fitpars[ll][0]:.3f} +- {fitpars[ll][2]:.3f} [ns]')

    print()
    
    diffs += (fitpars[:,0]) * float([-1.0, 1.0][ii]) 
    
print(F'differenze run{runs[1]}-run{runs[0]} [ns]:', '\n')

for ll in range(18):
    print(F'dom ', ll, '   ', diffs[ll])
    