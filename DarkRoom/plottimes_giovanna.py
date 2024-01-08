#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *
from pulsarParser import pparser

# EXAMPLE ################################################################################################################################################################################################################################################################################################################################################################################

runs = [(170, 3598, 15), (152, 3411, 15)] 
colorz = [kBlack, kBlue, kMagenta, kRed, kGreen]

plotout = './giovanna/%s.pdf'

diffs =  np.zeros(18)
medie = np.zeros((18,len(runs)))
diffinterdom = np.zeros((18-1, len(runs)))

runstag = '_'.join([str(ii[1]) for ii in runs])

gmeans, gdiffs = [], []

for ii, rr in enumerate(runs):
    
    tag = F'det{rr[0]:03}_run{rr[1]:04}_pmt{rr[2]:02}'
    fname = F'../data/KM3NeT_00000{rr[0]:03}_0000{rr[1]:04}__LASER_PATCHED_PMT{rr[2]:02}_L0.JPulsar.PMT{rr[2]:02}.root'
    infile = TFile(fname)
    histos, fitpars, graphs = pparser.parsefile(infile, runs[ii])
    
    medie[:,ii] = fitpars[:,0]
    diffinterdom[:,ii] =  medie[1:,ii] - medie[:-1,ii]
            
    gmean = graphs[0]
    gmean.SetNameTitle('mean__'+tag, tag)
    gmean.GetYaxis().SetRangeUser(-3500,1000)   
    gmean.GetYaxis().SetTitle('mean [ns]')
    gmean.GetXaxis().SetTitle('dom #')
    gmeans.append(gmean)
    
    gdiff = TGraphErrors(17, np.array(np.arange(1,18),dtype=float), np.array(diffinterdom[:,ii],dtype=float), np.array(np.zeros(17),dtype=float), np.array(np.zeros(17),dtype=float)) #aggiungere errori y
    gdiff.SetNameTitle('diff__'+tag, tag)
    gdiff.GetYaxis().SetRangeUser(-210,-190)    
    gdiff.GetYaxis().SetTitle('interdom dt [ns]')
    gdiff.GetXaxis().SetTitle('pair #')
    gdiffs.append(gdiff)
     
    print(F'################################ parsing run {tag}:')
    for ll in range(18):
        print(F'dom {ll:02} ---> {fitpars[ll][0]:.3f} +- {fitpars[ll][2]:.3f} [ns]')
    
    print(F'################################ differenze DOM_(ii+1)-DOM_(ii) run{rr} [ns]:')
    for ll in range(18-1):
        print(F'dom {ll:02} ---> {diffinterdom[ll,ii]:.3f}')
    
for ggs in [gmeans, gdiffs]:
    cc = TCanvas('cc', 'cc', 1600, 1800)
    cc.SetGrid()
    for igg, (gg, colo) in enumerate(zip(ggs, colorz)): 
        gg.SetMarkerSize(1.5)
        gg.SetMarkerStyle(110)
        gg.SetMarkerColor(colo)
        gg.DrawClone('P' + ('A' if not bool(igg) else 'same'))
    cc.BuildLegend(0.9,0.2,1.0,0.8)
    gStyle.SetOptTitle(0)
    cc.SaveAs(plotout%F'g_{gg.GetName().split("__")[0]}_{runstag}')  

print('\n\n', (plotout%'')[:-4], '\n')

    


