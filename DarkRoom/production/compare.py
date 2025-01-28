#daniele.paesani@lns.infn.it

import numpy as np
import ROOT
from pulsarParser import pparser
import pandas as pd
import os, argparse, glob, sys


# usage ###########################################################################################################################################################
# python3 compare.py 99,123,1 x,x,2 x,124,x         --> plots from DU=99: run123 (pmts 1 and 2) and run 124 (pmt2)
# python3 compare.py 99,123,1 ,,2 ,124,             --> same as above
# python3 compare.py 99,123,1 99,123,2 99,124,2     --> same as above
###################################################################################################################################################################

# options #########################################################################################################################################################
# --list            --> globs files in data directory
# --rng xxx,yyy     --> sets time range between xxx and yyy
# --printdom 1      --> prints information per DOM
# --tag "mytag"     --> adds "_mytag" to output
# --marker xx       --> ROOT plot marker 
# --out pdf,png     --> sets out format to png and pdf
# --single 1        --> add single plots per PMT
# --singlelog 1     --> plots above with logy
# --msg "my text"   --> adds "my text" on top of ROOT canva
# --drawmean 1      --> draws mean line per WWRS
# --plotdiag 1      --> plot fit diagnostics
###################################################################################################################################################################

# configure plots here ############################################################################################################################################
runformat = '../data/KM3NeT_%08d_%08d__LASER_PATCHED_PMT%02d_t74_463_L0__EXAMPLE.JPulsar.PMT%02d.root'
runformat = '../data2/KM3NeT_%08d_%08d__PMT%02d_L0.JPulsar.PMT%02d.root'
pantone = [ROOT.kBlue, ROOT.kRed, ROOT.kBlack, ROOT.kGreen, ROOT.kOrange, ROOT.kMagenta, ROOT.kRed, ROOT.kYellow+2, ROOT.kCyan-2, ROOT.kGray, ROOT.kGreen+2]
outpath = '/Users/dp/Downloads/'
wildcard = ['x', '']
##################################################################################################################################################################

print()

def getmeannan(aa):
        try:
            m = 2.0
            # mm = np.nanmedian(aa)
            # return np.nanmean(aa[np.abs(aa-mm) < m*mm])
            vals = aa[np.abs(aa-np.nanmedian(aa))<m*np.nanstd(aa)]
            return np.nanmean(vals), np.nanstd(vals)
        except:
            return np.nan

parser = argparse.ArgumentParser(description='DarkRoom plots - compare runs')
parser.add_argument('detrunpmt',     type=str,      default=[],         nargs='+')
parser.add_argument('--list',        type=int,      default=0)
parser.add_argument('--rng',         type=int,      default=[610,630],  nargs='+')
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
parser.add_argument('--singlelogy',  type=int,      default=0)
parser.add_argument('--rsync',       type=int,      default=0)
parser.add_argument('--msg',         type=str,      default='', nargs='+')
parser.add_argument('--drawmean',    type=int,      default=1)
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
    infiles.append(ROOT.TFile(runformat%(dets[-1],runs[-1],pmts[-1],pmts[-1])))
        
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
    ccc = ROOT.TCanvas(F'cc{ii}','cc', 1500*3, 6*500)
    # ccc.Divide(9,2)
    ccc.Divide(3,6)
    ccc.cd()
    ROOT.gStyle.SetOptStat(111111)
    ROOT.gStyle.SetOptFit(111)

    for iii,hh in enumerate(histos):
        ccc.cd(iii+1)
        ROOT.gPad.SetLogy(args.singlelogy)
        hh.GetXaxis().SetRangeUser(args.rng[0], args.rng[1]+8)
        hh.SetFillColorAlpha(ROOT.kBlue, 0.4)
        hh.Draw()
        
    for oout in args.out: 
        
        ppath = F'doms/'
        try: os.mkdir(outpath+ppath)
        except: pass
        ccc.SaveAs(outpath + ppath + F'{idet:04d}_{ipmt:02d}_{irun:04d}.' + oout)

if args.printdom:  print(ssout1)     
if args.printmean: print(ssout2)     
    

for iii, gg in enumerate(['norm', 'mean', 'sigma', 'backg', 'chi2norm']):
    ismean = iii == 1

    if (not ismean) and (not args.plotdiag): continue
    isnorm = iii == 0
    issigma = iii == 2
    ischi2 = iii == 4
    
    dims = (1600,800)
    
    cc = ROOT.TCanvas(F'ccc_{iii}',F'ccc_{iii}',dims[0],dims[1])
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

    pt  = ROOT.gPad.FindObject("title")
    try:
        ptn = ROOT.TPaveText(pt.GetX1(),pt.GetY1(),pt.GetX2(),pt.GetY2(),'')
        ptn.SetTextSize(0.04)
        msg = ' '.join(args.msg) if args.msg else F'run {",".join(str(rrr) for rrr in set(runs))} {ttag}'
        ptn.AddText(msg)
        ptn.SetBorderSize(0)
        ptn.SetFillColor(0)
        ptn.SetTextFont(42)
        ptn.Draw('same')
    except: 
        ROOT.gStyle.SetOptTitle(0)

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
                    ll = ROOT.TLine(ivv*9+1, vll, 9*(ivv+1), vll)
                    ll.SetLineColor(pantone[ii])
                    ll.SetLineStyle(vlls)
                    ll.DrawClone('same')
                
    for oout in args.out:
        cc.SaveAs(outpath + (F'{gg}_{"_".join(F"{rrr:04d}" for rrr in set(runs))}'+tag) + '.' + oout)  

print()



