#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *
from pulsarParser import pparser
import pandas as pd
import os, argparse, glob, sys

# runs, trange = [916, 920, 922, 924, 926], (200,240)
# runs, trange = [930, 932], (310,320)
# runs, trange = [959, 961, 963, 965, 967, 969, 971], (180,240)
# runs, trange = [930, 932, 965], (210,320)
# runs, trange = [930, 963, 967], (210,320)
# runs, trange = [959, 961, 963, 965, 967, 969, 930, 932], (180,330)
# runs, trange = [1000+ii for ii in [60, 64, 66, 70, 72, 74]], (280,330)
runs, trange = [1100+ii for ii in [8,2,6,12,53,55,57,59,61,63]], (280,330)

parser = argparse.ArgumentParser(description='DarkRoom plots - compare runs')
parser.add_argument('--run',         type=int,      default=runs, nargs='+')
parser.add_argument('--rng',         type=int,      default=trange, nargs='+')
parser.add_argument('--list',        type=int,      default=0)
parser.add_argument('--printdom',    type=int,      default=0)
parser.add_argument('--printmean',   type=int,      default=1)
parser.add_argument('--saveplot',    type=int,      default=1)
parser.add_argument('--saveexcel',   type=int,      default=1)
parser.add_argument('--tag',         type=str,      default='')
args = parser.parse_args()

runs = args.run
trange = args.rng
tag = '_' + args.tag if args.tag else ''

runformat = '../data/KM3NeT_00000168_%08d__LASER_PATCHED_PMT08_t73_464_L0__EXAMPLE.JPulsar.PMT08.root'
pantone = [kBlue, kBlack, kGreen, kOrange, kMagenta, kRed, kYellow+2, kCyan-2, kGray, kGreen+2]
infiles = [TFile(runformat%ii) for ii in runs] 
outpath = '/Users/dp/Downloads/'
plotout = ['%s.root', '%s.pdf', '%s.png']
excelout = '%s.xlsx'

if args.list:
    ll = glob.glob('/'.join(runformat.rsplit('/')[:-1]) + '/*.root')    
    for lll in ll:
        print(lll)
    sys.exit()

cc = TCanvas('cc','cc',1600,800)
cc.cd()
cc.SetGrid()

dd = pd.DataFrame()

for ii, ff in enumerate(infiles):
    histos, fitpars, graphs = pparser.parsefile(ff, runs[ii])
    gmeans, gsigmas = graphs[0], graphs[1]
    gmeans.SetStats(1)
    gmeans.SetName(F'nn{ii}')
    gmeans.SetTitle(gmeans.GetTitle().replace(' means', ''))
    gmeans.SetMarkerColor(pantone[ii%len(pantone)])
    gmeans.SetLineWidth(2)
    gmeans.SetMarkerSize(3)
    gmeans.SetMarkerStyle(35) #35
    gmeans.GetYaxis().SetLimits(trange[0], trange[1])      
    gmeans.GetYaxis().SetRangeUser(trange[0], trange[1])      
    gmeans.SetMinimum(trange[0])
    gmeans.SetMaximum(trange[1])
    gmeans.DrawClone('P ' + ('A' if ii == 0 else 'same'))
    
    dd.insert(ii, 'run%08d_mean'%runs[ii],  fitpars[:,0])
    dd.insert(ii+1, 'run%08d_err'%runs[ii],   fitpars[:,2])
     
    if args.printdom:        
        print(F'\nRun {runs[ii]} DOM means [ns]:')
        for vi, (vx,vy,ex,ey) in enumerate(fitpars):
            print(F'{vx:.2f}')   
    
    def getmeannan(aa):
        m = 2.0
        # mm = np.nanmedian(aa)
        # return np.nanmean(aa[np.abs(aa-mm) < m*mm])
        return np.nanmean(aa[np.abs(aa-np.nanmedian(aa))<m*np.nanstd(aa)])
    
    if args.printmean:        
        print(F'Run {runs[ii]} DOM means [ns]: {getmeannan(fitpars[:9,0]):.3f} (A) ,  {getmeannan(fitpars[9:,0]):.3f} (B)')

if args.saveexcel:
    dd.insert(0, 'DOM', np.arange(1,18+1))
    dd.to_excel(outpath + excelout%(F'pars__{"_".join(str(rrr) for rrr in runs)}'+tag), index=1, sheet_name='fit_pars')

if args.saveplot:
    # gStyle.SetOptTitle(0)
    pt  = gPad.FindObject("title")
    ptn = TPaveText(pt.GetX1(),pt.GetY1(),pt.GetX2(),pt.GetY2(),'')
    ptn.SetTextSize(0.05)
    ptn.AddText(F'means {", ".join(str(rrr) for rrr in runs)}')
    ptn.SetBorderSize(0)
    ptn.SetFillColor(0)
    ptn.SetTextFont(42)
    ptn.Draw('same')

    print()
    cc.BuildLegend(0.9,0.2,1.0,0.8)
    for oout in plotout:
        cc.SaveAs(outpath + oout%(F'medie__{"_".join(str(rrr) for rrr in runs)}'+tag))  
