#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *
from pulsarParser import pparser

runs = [916, 920, 922, 924, 926]
trange = (200,240)
colorz = [kMagenta, kRed, kBlue, kGreen, kBlack, kOrange, ]
infiles = [TFile(F'../data/KM3NeT_00000168_00000{ii}__LASER_PATCHED_PMT08_t73_464_L0__EXAMPLE.JPulsar.PMT08.root') for ii in runs] 
plotout = ['./out/%s.pdf', './out/%s.root']
plotout = ['/Users/dp/Downloads/%s.root', '/Users/dp/Downloads/%s.pdf']

cc = TCanvas('cc','cc',1600,800)
cc.cd()
cc.SetGrid()

for ii, ff in enumerate(infiles):
    histos, fitpars, graphs = pparser.parsefile(ff, runs[ii])
    gmeans, gsigmas = graphs[0], graphs[1]
    gmeans.SetName(F'nn{ii}')
    gmeans.SetTitle(gmeans.GetTitle().replace(' means', ''))
    gmeans.SetMarkerColor(colorz[ii%len(colorz)])
    gmeans.SetMarkerSize(2)
    gmeans.SetMarkerSize(3)
    gmeans.SetMarkerStyle(35)
    gmeans.GetYaxis().SetLimits(trange[0], trange[1])      
    gmeans.GetYaxis().SetRangeUser(trange[0], trange[1])      
    gmeans.SetMinimum(trange[0])
    gmeans.SetMaximum(trange[1])
    gmeans.DrawClone('P text ' + ('A' if ii == 0 else 'same'))
     
    # print(F'\nRun {runs[ii]} DOM means [ns]:')
    # for vi, (vx,vy,ex,ey) in enumerate(fitpars):
    #     print(F'{vx:.2f}')   
    
    print(F'\nRun {runs[ii]} DOM means [ns]: {np.nanmean(fitpars[:9,0]):.2f} (A) ,  {np.nanmean(fitpars[9:,0]):.2f} (B)')
    
# gStyle.SetOptTitle(0)
pt  = gPad.FindObject("title")
ptn = TPaveText(pt.GetX1(),pt.GetY1(),pt.GetX2(),pt.GetY2(),'')
ptn.AddText(F'means {", ".join(str(rrr) for rrr in runs)}')
ptn.SetBorderSize(0)
ptn.SetFillColor(0)
ptn.SetTextFont(42)
ptn.Draw('same')

print()
cc.BuildLegend(0.9,0.2,1.0,0.8)
for oout in plotout:
    cc.SaveAs(oout%F'medie__{"_".join(str(rrr) for rrr in runs)}')  
