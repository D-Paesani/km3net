#daniele.paesani@lns.infn.it

import numpy as np
from ROOT import *
from pulsarParser import pparser
import pandas as pd
import os, argparse, glob, sys
import pathlib

runformat = '../data/KM3NeT_%08d_%08d__LASER_PATCHED_PMT%02d_t74_463_L0__EXAMPLE.JPulsar.PMT%02d.root'
pantone = [kBlue, kRed, kBlack, kGreen, kOrange, kMagenta, kRed, kYellow+2, kCyan-2, kGray, kGreen+2]
outpath = '/Users/dp/Downloads/'
wildcard = ['x', '']

print()

def getmeannan(aa):
        m = 2.0
        # mm = np.nanmedian(aa)
        # return np.nanmean(aa[np.abs(aa-mm) < m*mm])
        vals = aa[np.abs(aa-np.nanmedian(aa))<m*np.nanstd(aa)]
        return np.nanmean(vals), np.nanstd(vals)

parser = argparse.ArgumentParser(description='DarkRoom plots - compare runs')
parser.add_argument('detrunpmt',     type=str,      default=[],         nargs='+')
parser.add_argument('--list',        type=int,      default=0)
parser.add_argument('--rng',         type=int,      default=[660,672],  nargs='+')
parser.add_argument('--printdom',    type=int,      default=0)
parser.add_argument('--printmean',   type=int,      default=1)
parser.add_argument('--tag',         type=str,      default='')
parser.add_argument('--marker',      type=int,      default=33)
parser.add_argument('--pmts',        type=int,      default=[], nargs='+')
parser.add_argument('--dets',        type=int,      default=[], nargs='+')
parser.add_argument('--clear',       type=int,      default=0)
parser.add_argument('--out',         type=str,      default=['png'], nargs='+')
parser.add_argument('--malpha',      type=float,    default=0.65)
parser.add_argument('--single',      type=int,      default=1)
parser.add_argument('--rsync',       type=int,      default=0)
parser.add_argument('--msg',         type=str,      default='', nargs='+')
parser.add_argument('--drawmean',    type=int,      default=0)
parser.add_argument('--saveexcel',   type=int,      default=0)
parser.add_argument('--plotdiag',    type=int,      default=0)

args = parser.parse_args()

tag = '_' + args.tag if args.tag else ''
ttag = F'({args.tag})' if args.tag else ''
trange = args.rng

if args.rsync:
    print()
    os.system('sh getfiles.sh')
    print()
    
if args.clear:
    print('clearing output')
    os.system('mv /Users/dp/Downloads/*  /Users/dp/.Trash/')
    # sys.exit()
    
if args.list:
    ll = glob.glob('/'.join(runformat.rsplit('/')[:-1]) + '/*.root')    
    for lll in ll:
        print(lll)
    sys.exit()
    
infiles, dets, runs, pmts = [],[],[],[]
for ii in args.detrunpmt:
    (idet, irun, ipmt) = ii.split(',')
    dets.append(dets[-1] if idet in wildcard else int(idet))
    runs.append(runs[-1] if irun in wildcard else int(irun))
    pmts.append(pmts[-1] if ipmt in wildcard else int(ipmt))
    infiles.append(TFile(runformat%(dets[-1],runs[-1],pmts[-1],pmts[-1])))
        
ssout1, ssout2 = '',''
for ii, ff in enumerate(infiles):

    idet, irun, ipmt = dets[ii], runs[ii], pmts[ii]
    histos, fpars, fparerrs, fchi2, (gnorm, gmean, gsigma, gbkg, gfitq) = pparser.parsefile(ff, irun)
        
    if args.printdom:        
        ssout1 += F'\nDET{idet:04d} RUN{irun:04d} PMT{ipmt:02d} -> DOM means [ns]:'
        for vi, vv in enumerate(fpars): ssout1 += F'{fpars[1]:.2f}\n'
                
    if args.printmean:  
        if not ii: ssout2 += '\n'
        ssout2 += F'DET{idet:04d} RUN{irun:04d} PMT{ipmt:02d} -> DOM means [ns]: {getmeannan(fpars[:9,1])[0]:.3f} (A) ,  {getmeannan(fpars[9:,1])[0]:.3f} (B)\n'
        
    if not args.single: continue
    
    # ccc = TCanvas(F'cc{ii}','cc', 1500*9, 2*300)
    ccc = TCanvas(F'cc{ii}','cc', 1500*3, 6*500)
    # ccc.Divide(9,2)
    ccc.Divide(3,6)
    ccc.cd()
    gStyle.SetOptStat(111111)
    gStyle.SetOptFit(111)

    for iii,hh in enumerate(histos):
        ccc.cd(iii+1)
        gPad.SetLogy(1)
        hh.GetXaxis().SetRangeUser(args.rng[0], args.rng[1]+8)
        hh.SetFillColorAlpha(kBlue, 0.4)
        hh.Draw()
        
    for oout in args.out: 
        
        ppath = F'doms/'
        try: os.mkdir(outpath+ppath)
        except: pass
        ccc.SaveAs(outpath + ppath + F'{idet:04d}_{ipmt:02d}_{irun:04d}.' + oout)

if args.printdom:  print(ssout1)     
if args.printmean: print(ssout2)     
    

for iii, gg in enumerate(['norm', 'mean', 'sigma', 'backg', 'chi2norm']):
    isnorm = iii == 0
    ismean = iii == 1
    issigma = iii == 2
    ischi2 = iii == 4
    if (not ismean) and (not args.plotdiag): continue
    
    dims = (1600,800)
    cc = TCanvas(F'ccc_{iii}',F'ccc_{iii}',dims[0],dims[1])
    cc.cd()
    cc.SetGrid(1)
    
    for ii, ff in enumerate(infiles):        
        idet, irun, ipmt = dets[ii], runs[ii], pmts[ii]
        histos, fpars, fparerrs, fchi2, graphs = pparser.parsefile(ff, irun)
        igg = graphs[iii]
        
        igg.SetStats(1)
        igg.SetName(F'{igg.GetName()}_{irun}')
        igg.SetTitle(F'{idet:04d}_{ipmt:02d}_{irun:04d}')
        igg.SetMarkerColor(pantone[ii%len(pantone)])
        igg.SetMarkerColorAlpha(pantone[ii%len(pantone)], args.malpha)
        igg.SetMarkerSize(3)
        igg.SetMarkerStyle(args.marker)
        
        if ismean:
            igg.SetMinimum(trange[0])
            igg.SetMaximum(trange[1])
        if issigma:
            igg.SetMinimum(0)
            igg.SetMaximum(2)
        if ischi2:
            cc.SetLogy(1)
            igg.SetMinimum(0)
            igg.SetMaximum(3000)
        if isnorm:
            cc.SetLogy(1)
            igg.SetMinimum(0)
            igg.SetMaximum(1e6)
        
        igg.DrawClone('P ' + ('A' if ii == 0 else 'same'))

    pt  = gPad.FindObject("title")
    try:
        ptn = TPaveText(pt.GetX1(),pt.GetY1(),pt.GetX2(),pt.GetY2(),'')
        ptn.SetTextSize(0.04)
        msg = ' '.join(args.msg) if args.msg else F'run {",".join(str(rrr) for rrr in set(runs))} {ttag}'
        ptn.AddText(msg)
        ptn.SetBorderSize(0)
        ptn.SetFillColor(0)
        ptn.SetTextFont(42)
        ptn.Draw('same')
    except: 
        gStyle.SetOptTitle(0)

    ll = cc.BuildLegend(0.9,0.2,1.0,0.8)
    ll.SetTextFont(62)
    ll.SetHeader('DET_PMT_RUN','C')
    ll.SetTextSize(0.022)

    if args.drawmean and ismean:
        for ii, ff in enumerate(infiles):        
            idet, irun, ipmt = dets[ii], runs[ii], pmts[ii]
            histos, fpars, fparerrs, fchi2, (gnorm, gmean, gsigma, gbkg, gfitq) = pparser.parsefile(ff, irun)
                        
            for ivv, vv in enumerate([getmeannan(fpars[:9,1]), getmeannan(fpars[9:,1])]):
                for vlli, vll, vlls in zip([1,2,3], [vv[0], vv[0]-vv[1], vv[0]+vv[1]],[7,3,3]):
                    if args.drawmean < 2 and vlli > 1: break
                    ll = TLine(ivv*9+1, vll, 9*(ivv+1), vll)
                    ll.SetLineColor(pantone[ii])
                    ll.SetLineStyle(vlls)
                    ll.DrawClone('same')
                
    for oout in args.out:
        cc.SaveAs(outpath + (F'{gg}_{"_".join(F"{rrr:04d}" for rrr in set(runs))}'+tag) + '.' + oout)  

print()



