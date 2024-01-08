#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *
        hh.SetTitle(nam)
from pulsarParser import pparser

# EXAMPLE ################################################################################################################################################################################################################################################################################################################################################################################

runs = [(170, 3598, 15), (152, 3411, 15)] 
salvacome= 'giovanna'

colorz = [kMagenta, kRed, kBlue, kGreen, kBlack]

plotout = './out/%s.pdf'

runstag = '_'.join([str(ii[1]) for ii in runs])

cc, ccc = TCanvas('cc','cc',1600,800), TCanvas('ccc','ccc',1600,800)

diffs =  np.zeros(18)

medie = np.zeros((18,len(runs)))
diffinterdom = np.zeros((18-1, len(runs)))

for ii, rr in enumerate(runs):
    
    fname = F'../data/KM3NeT_00000{rr[0]:03}_0000{rr[1]:04}__LASER_PATCHED_PMT{rr[2]:02}_L0.JPulsar.PMT{rr[2]:02}.root'
    infile = TFile(fname)
    histos, fitpars, graphs = pparser.parsefile(infile, runs[ii])
    
    medie[:,ii] = fitpars[:,0]
    diffinterdom[:,ii] =   medie[1:,ii] - medie[:-1,ii]
        
    gmeans, gsigmas = graphs[0], graphs[1]
    gg = TGraphErrors()

    tag = F'det{rr[0]:03}_run{rr[1]:04}_pmt{rr[2]:02}'

    gmeans.GetYaxis().SetRangeUser(-3500,1000)       
    gg.GetYaxis().SetRangeUser(150,250)    
    gg.GetYaxis().SetTitle('interdom dt [ns]')
    gg.GetXaxis().SetTitle('pair #')
        
    for gggg in [gg, gmeans, gsigmas]:
        gmeans.SetNameTitle(tag, tag)
        gmeans.SetMarkerColor(colorz[ii])
            
    print(F'parsing run {tag}:')
    for ll in range(18):
        print(F'dom {ll:02} ---> {fitpars[ll][0]:.3f} +- {fitpars[ll][2]:.3f} [ns]')
    print()
    
    print(F'differenze DOM_(ii+1)-DOM_(ii) run{rr} [ns]:')
    for ll in range(18-1):
        print(F'dom {ll:02} ---> {diffinterdom[ll,ii]:.3f}')
        pparser.FillGraph(gg, ll+1, diffinterdom[ll,ii], 0.0, 0.0) #poi aggiungere ey
        
    print()
   
    cc.cd()
    gmeans.DrawClone('AP' if ii == 0 else 'P same')
    
    ccc.cd()
    gg.DrawClone('AP' if ii == 0 else 'P same')
    
     
cc.BuildLegend(0.9,0.2,1.0,0.8)
ccc.BuildLegend(0.9,0.2,1.0,0.8)
gStyle.SetOptTitle(0)
cc.SaveAs(plotout%F'giov_{runstag}_means')  
ccc.SaveAs(plotout%F'giov_{runstag}_interdom')  

print('\n\n', (plotout%'')[:-4], '\n')

    

