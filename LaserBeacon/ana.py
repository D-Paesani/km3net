#[10, 11, 14, 15, 16, 19, 20, 21, 22, 26]
# light vs distance
# dt vs distance
# mean time
# bodo
# tres vs npe after subtraction
# tidff vs npemean
# why dT binned 1 ns

from ROOT import *
from Roottols.Helper import *
from Roottols.RootHelper import FillGraph, FillGraphAsymmErrrors, MkBranch
from Roottols.Plotter import *
from Roottols.Plotter import Tplot as pl, tplotconf as pc
import Roottols.TreePlotHelper as ph
from Roottols.Functions import *
from Roottols.PyRootPlotManager import PyRootPlotManager as rpm

import argparse
import uproot
import pandas as pd
import itertools

def namerdu(nn, add=True): 
    return ('du' if add else '') + '{:03}'.format(nn)
def namerdom(nn, add=True): 
    return ('dom' if add else '') + '{:03}'.format(nn)
def namerdudom(val, du, dom): 
    return F'{val}_{namerdu(du)}{namerdom(dom)}'
def namerdudomx(val, du): 
    return F'{val}_{namerdu(du)}dom'

def preproc_namer(hb: rpm.hbox):
    tag1 = F'{hb.GetCurrentIdx()}' if (hb.GetSize() > 1) else ''
    tag2 =  F' [{hb.GetCurrentIdx()}]' if (hb.GetSize() > 1) else ''
    hb.SetCurrentName(hb.GetName() + tag1)
    hb.SetCurrentTitle(hb.GetTitle() + tag2)
    
def proc_skipempty100(hh: rpm.hbox):
        hh.hSkip = hh.GetCurrentEntries() < 50
        
parser = argparse.ArgumentParser(description='quickana')
parser.add_argument('--filein',       type=str,   default='../data/prova.root')
parser.add_argument('--fileout',      type=str,   default=None)
parser.add_argument('--treename',     type=str,   default='T')
parser.add_argument('--dus',          type=int,   default=[10, 11, 14, 15, 16, 19, 20, 21, 22, 26], nargs='+')
parser.add_argument('--beacon',       type=int,   default=2)
parser.add_argument('--parsedf',      type=int,   default=False)
args = parser.parse_args()
if args.fileout == None: args.fileout = args.filein.replace('.root', '_ana.root')

if args.parsedf:
    intfile = uproot.open(args.filein)
    intree = intfile[args.treename]
    data = intree.arrays(library='pd')
    data.rename(columns={'Trigger':'eve', 'Line':'du', 'DOM':'dom', 'PMT':'pmt', 'dT':'dt', 'D1':'d1', 'D2':'d2', 'npe':'npe'}, inplace=True)
    for ii in ['eve', 'du', 'dom', 'pmt']:
        data[ii] = data[ii].astype(int)
    data.sort_values(by=['eve', 'du', 'dom', 'pmt'], inplace=True)
    for ii in tqdm(range(3)):
        data = data.groupby(['eve','du','dom'][0:3-ii], sort=False, as_index=0*ii==2)[data.columns].agg(tuple)
    data.to_pickle(args.filein.replace('.root', '.pkl'), compression='gzip')
    sys.exit()
else : 
    data = pd.read_pickle(args.filein.replace('.root', '.pkl'), compression='gzip')
    
duused = len(args.dus)
dumax = 32
dommax = 20
rngq = (480,0,120)
rngqsmall = (120,0,40)
rngdom = (20,0,20)
rangepmt = (32,0,32)
rngdt = (1000,-1000,1000)
rngqsum = (1000,0,1000)
rngtdiff = (200,-50,50) 
rngy = (500,0,500)
rngx = (600,-300,300)
rngr = (600,0,600)
rngz = (700,0,700)
rngd = (100,0,600)

combpmts = [(int(ii),int(iii)) for ii,iii in itertools.combinations(np.arange(0,32,dtype=int),2)]
    
outfile = ROOT.TFile(args.fileout, 'recreate')
pm = rpm()
pm.SetOutFile(outfile)
pm.SetProcessor(rpm.proc_skipempty)

pm.SetOutDir(pm.GetOutFile().mkdir('dist','',True))
pm.Add(ROOT.TH2F, 'qsumVdist',     axs=(*rngd,*rngqsum),     num=3,      proc=[proc_skipempty100, rpm.proc_profx],  titl='dom qsum vs dist beacon ',  folder=False)
pm.Add(ROOT.TH2F, 'tmeanVdist',    axs=(*rngd,*rngdt),       num=3,      proc=[proc_skipempty100, rpm.proc_profx],  titl='dom tmean vs dist beacon ',  folder=False)

pm.SetOutDir(pm.GetOutFile().mkdir('du','',True))
pm.Add(ROOT.TH2F, 'qsumVdom',      axs=(*rngdom,*rngqsum),     num=dumax,      proc=[proc_skipempty100],   titl='qsum vs dom for du =')
pm.Add(ROOT.TH2F, 'tmeanVdom',     axs=(*rngdom,*rngdt),       num=dumax,      proc=[proc_skipempty100],   titl='tmean vs dom for du =')
pm.Add(ROOT.TH2F, 'tdiffsVnpe',    axs=(*rngqsmall, *rngtdiff),                proc=[proc_skipempty100],   titl=F'all pair pmt tdiff vs npemean', folder=False)

dusdir = pm.SetOutDir(pm.GetOutFile().mkdir('dus','',True))
for ii in args.dus:
    ttag = F'for du={ii}  dom='          
    pm.SetUseFolders(0)    
    pm.Add(ROOT.TH2F, namerdudomx('npeVpmt',ii),    axs=(*rangepmt,*rngq),        num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('npeVpmt','',True),      titl=F'npe vs pmtid {ttag}')
    pm.Add(ROOT.TH1F, namerdudomx('npepmt0',ii),    axs=rngq,                     num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('npepmt0','',True),      titl=F'npe of pmt0 {ttag}')
    pm.Add(ROOT.TH1F, namerdudomx('dtpmt0',ii),     axs=rngdt,                    num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('dtpmt0','',True),       titl=F'dt of pmt0 {ttag}')
    pm.Add(ROOT.TH2F, namerdudomx('dtVpmt',ii),     axs=(*rangepmt,*rngdt),       num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('dtVpmt','',True),       titl=F'dt vs pmt {ttag}')
    pm.Add(ROOT.TH2F, namerdudomx('dtVnpe',ii),     axs=(*rngq,*rngdt),           num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('dtVnpe','',True),       titl=F'dt vs npe {ttag}')
    pm.Add(ROOT.TH1F, namerdudomx('tdiffs',ii),     axs=rngtdiff,                 num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('tdiffs','',True),       titl=F'all pair pmt tdiff {ttag}')
    pm.Add(ROOT.TH2F, namerdudomx('tdiffsVnpe',ii), axs=(*rngqsmall, *rngtdiff),  num=dommax,     proc=[proc_skipempty100],  dire=dusdir.mkdir('tdiffsVnpe','',True),   titl=F'all pair pmt tdiff vs npemean {ttag}')
    pm.SetUseFolders(1)    

for eve in tqdm(data.itertuples(), total=data.shape[0], colour='blue'):
    
    for idu, du in enumerate(eve.du):
        
        for idom, dom in enumerate(eve.dom[idu]):
            
            pmts = eve.pmt[idu][idom]
            npes = eve.npe[idu][idom]
            dts =  eve.dt[idu][idom]
            domdists = [eve.d1[idu][idom][0], eve.d2[idu][idom][0]]
            
            domqsum, domtmean = 0,0  
            
            for (ii1,ii2) in combpmts[0:len(pmts)-1]:
                ttt = dts[ii1]-dts[ii2]
                qqq = 0.5*(npes[ii1]+npes[ii2])
                pm.Fill(namerdudomx('tdiffs',  du),             ttt,    idx=dom)
                pm.Fill(namerdudomx('tdiffsVnpe',  du),   qqq,  ttt,    idx=dom)    
                pm.Fill('tdiffsVnpe',   qqq,  ttt)    

            for ipmt, (pmt,npe,dt) in enumerate(zip(pmts, npes, dts)):

                domqsum += npe
                domtmean += dt*npe
                
                pm.Fill(namerdudomx('npeVpmt',  du),    pmt, npe,   idx=dom)
                pm.Fill(namerdudomx('dtVpmt',   du),    pmt, dt,    idx=dom)
                pm.Fill(namerdudomx('npepmt0',  du),         npe,   idx=dom, condition=pmt==0)
                pm.Fill(namerdudomx('dtVpmt',   du),         dt,    idx=dom, condition=pmt==0)
                pm.Fill(namerdudomx('dtVpmt',   du),         dt,    idx=dom, condition=pmt==0)
                pm.Fill(namerdudomx('dtVnpe',   du),    npe, dt,    idx=dom)
                
            domtmean *= 1.0/domqsum
            
            pm.Fill('qsumVdom',    dom, domqsum,       idx=du)
            pm.Fill('tmeanVdom',   dom, domtmean,      idx=du)
            
            for ii, dd in enumerate(domdists):
                pm.Fill('qsumVdist',  dd, domqsum, idx=ii)
                pm.Fill('tmeanVdist', dd, domtmean, idx=ii)
            
            
    
    
    


pm.ProcessBoxes(closefile=True)

