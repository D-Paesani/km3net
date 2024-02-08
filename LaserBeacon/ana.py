# NOTES ################################################################################################################################################################################################################################################################################################################################################################################################

# [10, 11, 14, 15, 16, 19, 20, 21, 22, 26]
# light vs distance
# dt vs distance
# mean time
# bodo
# tres vs npe after subtraction
# tidff vs npemean
# why dT binned 1 ns
# /pbs/home/b/baret/sps/CU
# /pbs/home/b/baret/sps/data/CU
# correzione T0
# aggiungere plot mappa
# +fit gaus picco all channels
# prepulse laser
# inbter dom t peak
# plot vs radius
# paired tofs 
# lobes
# orientation data
# add pointing (direction)

# push code 

# save as roottople and plot with other macro

# IMPORTS ################################################################################################################################################################################################################################################################################################################################################################################################

import ROOT
from Roottols.RootHelper import MkBranch, TreeManager
import Roottols.RootPlotManager as rpm
import argparse
import uproot
import pandas as pd
import numpy as np
from tqdm import tqdm
import itertools
import sys

# PROCESSORS ################################################################################################################################################################################################################################################################################################################################################################################################

def namerdudomx(val, du): 
    return F'{val}_{du:02}_'

def preproc_namer(hb: rpm.HistBox):
    tag1 =  F'{hb.GetCurrentIdx():02}' if (hb.GetSize() > 1) else ''
    tag2 =  F' [{hb.GetCurrentIdx():02}]' if (hb.GetSize() > 1) else ''
    hb.SetCurrentName(hb.GetName()   + tag1)
    hb.SetCurrentTitle(hb.GetTitle() + tag2)
    
def proc_skip100(hh: rpm.HistBox):
    hh.SetCurrentSkip(hh.GetCurrentEntries() < 100)
            
# ARGS ################################################################################################################################################################################################################################################################################################################################################################################################
        
parser = argparse.ArgumentParser(description='Quick diagnostics for LaserBeacon runs')
parser.add_argument('--filein',       type=str,   default='../data/prova.root')
parser.add_argument('--fileout',      type=str,   default=None)
parser.add_argument('--treename',     type=str,   default='T')
parser.add_argument('--dus',          type=int,   default=[10, 11, 14, 15, 16, 19, 20, 21, 22, 26], nargs='+')
parser.add_argument('--beacon',       type=int,   default=2)
parser.add_argument('--parsedf',      type=int,   default=False)
parser.add_argument('--sortdf',       type=int,   default=False)
parser.add_argument('--evlimit',      type=int,   default=-1)
args = parser.parse_args()
if args.fileout == None: args.fileout = args.filein.replace('.root', '_ana.root')

# LUT ################################################################################################################################################################################################################################################################################################################################################################################################

pmtangles = pd.read_excel('../data/pmtlut.xlsx')
pmtangles.sort_values('pmt', inplace=True)

# RESHAPE ################################################################################################################################################################################################################################################################################################################################################################################################

if args.parsedf:
    intfile = uproot.open(args.filein)
    intree = intfile[args.treename]
    data = intree.arrays(library='pd')
    data.rename(columns={'Trigger':'eve', 'Line':'du', 'DOM':'dom', 'X':'x', 'Y':'y', 'Z':'z', 'D1':'d1', 'D2':'d2', 'PMT':'pmt', 'ToT':'tot', 'npe':'npe', 'dT':'dt'}, inplace=True)
    for ii in ['eve', 'du', 'dom', 'pmt']: data[ii] = data[ii].astype(int)
    if 1 or args.sortdf: data.sort_values(by=['eve', 'du', 'dom', 'pmt'], inplace=True)
    ddd = dict()
    for ii in data.columns: ddd[ii] = 'first'
    for ii in tqdm(range(3), colour='magenta'):
        for iii in [['pmt','tot','npe','dt'], ['dom','x','y','z','d1','d2'],['du']][ii]: ddd[iii] = tuple
        if ii==1:
            coltargets = ['npesum', 'npesqrtsum', 'npemean', 'tmean', 'theta', 'phi'] 
            colfuns = [
                       lambda x: np.sum(x.npe), 
                       lambda x: np.sum(np.sqrt(x.npe)), 
                       lambda x: np.mean(x.npe),
                       lambda x: np.sum(x['dt']*np.sqrt(x.npe))/x.npesqrtsum,
                       lambda x: np.sum(pmtangles.iloc[list(x.pmt)].theta * x.npe) / np.sum(x.npe),
                       lambda x: np.sum(pmtangles.iloc[list(x.pmt)].phi   * x.npe) / np.sum(x.npe),
                       ]                
            for coltarget, colfun in zip(coltargets, colfuns):
                data[coltarget] = data.apply(colfun, axis=1)
                ddd[coltarget] = tuple
        data = data.groupby(['eve','du','dom'][0:3-ii], sort=False, as_index=0)[data.columns].agg(ddd)
    print(data.iloc[0])
    data.to_pickle(args.filein.replace('.root', '.pkl'), compression='gzip')
    sys.exit()
else: 
    data = pd.read_pickle(args.filein.replace('.root', '.pkl'), compression='gzip')
    print(data.iloc[0])
    
# RANGES ################################################################################################################################################################################################################################################################################################################################################################################################
     
duused = len(args.dus)
dumax, dommax, pmtmax = 32, 20, 31
combpmts = [(int(ii),int(iii)) for ii,iii in itertools.combinations(np.arange(0,pmtmax,dtype=int),2)]   

ax_q =          ('Q/pe',        480,0,120)
ax_qsmall =     ('Q/pe',        120,0,40)
ax_dom =        ('DOM ID',      dommax,0,dommax)
ax_pmt =        ('PMT ID',      dumax,0,dumax)
ax_dt =         ('dT/ns',       1000,-1000,1000)
ax_qsum =       ('Qsum/ns',     2000,0,2000)
ax_tdiff =      ('Tdiff/ns',    200,-100,100) 
ax_y =          ('Y/m',         500,0,500)
ax_x =          ('X/m',         600,-300,300)
ax_r =          ('R/m',         600,0,600)
ax_z =          ('Z/m',         700,0,700)
ax_d =          ('D/m',         100,0,600)
ax_domtheta =   ('theta/deg',   60,0,180)
ax_domphi   =   ('phi/deg',     165,-240,90)

# BOOK ################################################################################################################################################################################################################################################################################################################################################################################################
    
pm = rpm.PlotManager()
pm.SetOutFile(ROOT.TFile(args.fileout, 'recreate'))
pm.SetBoxConf(bPreProc=preproc_namer, bProcessor=rpm.proc_skipempty)

pm.SetBoxConf(bOutDir=pm.GetOutFile().mkdir('dist','',True), bPreProc=rpm.preproc_namer, bNum=3, bUseFolder=False)
pm.Add('map3d_trig',  bType=rpm.H3,     bAxs=ax_x+ax_y+ax_z, bNum=1, bProcessor=[proc_skip100, rpm.proc_savecanvas], bOptions='glcol2',  bTitle='map3d trig').histos[0].Rebin3D(4,4,4)
pm.Add('map3d_q',     bType=rpm.H3,     bAxs=ax_x+ax_y+ax_z, bNum=1, bProcessor=[proc_skip100], bTitle='map3d charge').histos[0].Rebin3D(4,4,4)
pm.Add('qsumVdist',   bType=rpm.H2,     bAxs=ax_d+ax_qsum,           bProcessor=[proc_skip100, rpm.proc_profx],     bTitle='dom qsum vs dist beacon '    )
pm.Add('qmeanVdist',  bType=rpm.H2,     bAxs=ax_d+ax_q,              bProcessor=[proc_skip100, rpm.proc_profx],     bTitle='dom qmean vs dist beacon '   )
pm.Add('tmeanVdist',  bType=rpm.H2,     bAxs=ax_d+ax_dt,             bProcessor=[proc_skip100, rpm.proc_profx],     bTitle='dom tmean vs dist beacon '   )

pm.SetBoxConf(bOutDir=pm.GetOutFile().mkdir('du','',True), bPreProc=preproc_namer, bUseFolder=True)
pm.Add('qsumVdom',     bType=rpm.H2,  bAxs=ax_dom+ax_qsum,     bNum=dumax,      bProcessor=[proc_skip100],   bTitle='qsum vs floor for du =')
pm.Add('tmeanVdom',    bType=rpm.H2,  bAxs=ax_dom+ax_dt,       bNum=dumax,      bProcessor=[proc_skip100],   bTitle='tmean vs floor for du =')
pm.Add('phiVdom',      bType=rpm.H2,  bAxs=ax_dom+ax_domphi,   bNum=dumax,      bProcessor=[proc_skip100, rpm.proc_profy],   bTitle='reco phi vs floor for du =')
pm.Add('thetaVdom',    bType=rpm.H2,  bAxs=ax_dom+ax_domtheta, bNum=dumax,      bProcessor=[proc_skip100, rpm.proc_profx],   bTitle='reco theta vs floor for du =')
pm.Add('tdiffsVnpe',   bType=rpm.H2,  bAxs=ax_qsmall+ax_tdiff,                  bProcessor=[proc_skip100],   bTitle='all pair pmt tdiff vs npemean', bUseFolders=False)

pm.SetBoxConf(bOutDir = (dusdir := pm.GetOutFile().mkdir('dus','',True)), bPreProc=preproc_namer, bNum=dommax, bUseFolders=False)
for ii in args.dus:
    ttag = F'for du={ii}  dom='          
    pm.Add(namerdudomx('npeVpmt',   ii),        bType=rpm.H2,    bAxs=ax_pmt+ax_q,           bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('npeVpmt','',True),      bTitle=F'npe vs pmtid {ttag}')
    pm.Add(namerdudomx('npepmt22',  ii),        bType=rpm.H1,    bAxs=ax_q,                  bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('npepmt22','',True),     bTitle=F'npe of pmt22 {ttag}')
    pm.Add(namerdudomx('dtpmt22',   ii),        bType=rpm.H1,    bAxs=ax_dt,                 bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('dtpmt22','',True),      bTitle=F'dt of pmt22 {ttag}')
    pm.Add(namerdudomx('dtpmtfirst',ii),        bType=rpm.H1,    bAxs=ax_dt,                 bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('dtpmtfirst','',True),   bTitle=F'dt of first pmt {ttag}')
    pm.Add(namerdudomx('dtVpmt',    ii),        bType=rpm.H2,    bAxs=ax_pmt+ax_dt,          bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('dtVpmt','',True),       bTitle=F'dt vs pmt {ttag}')
    pm.Add(namerdudomx('dtVnpe',    ii),        bType=rpm.H2,    bAxs=ax_q+ax_dt,            bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('dtVnpe','',True),       bTitle=F'dt vs npe {ttag}')
    pm.Add(namerdudomx('tdiffs',    ii),        bType=rpm.H1,    bAxs=ax_tdiff,              bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('tdiffs','',True),       bTitle=F'all pair pmt tdiff {ttag}')
    pm.Add(namerdudomx('tdiffsVnpe',ii),        bType=rpm.H2,    bAxs=ax_qsmall+ax_tdiff,    bProcessor=[proc_skip100],  bOutDir=dusdir.mkdir('tdiffsVnpe','',True),   bTitle=F'all pair pmt tdiff vs npemean {ttag}')
    
# TREE ################################################################################################################################################################################################################################################################################################################################################################################################ 

treedom = TreeManager('dom', fileout=pm.GetOutFile(), bdic={'eve,dom,du':('i', (1,), None), 'pe,ti,tfirst,theta,phi':('d', (1,), None), 'di,pos':('d', (3,), None)})

# LOOP ################################################################################################################################################################################################################################################################################################################################################################################################ 

for eve in tqdm(data.itertuples(), total=data.shape[0], colour='blue'):
    
    for idu, du in enumerate(eve.du):
        
        if not du in args.dus: continue
        
        for idom, dom in enumerate(eve.dom[idu]):
            
            domdists = [eve.d1[idu][idom], eve.d2[idu][idom], 0.0]
            pmts =      eve.pmt[idu][idom]
            npes =      eve.npe[idu][idom]
            dts =       eve.dt[idu][idom]
            domqsum =   eve.npesum[idu][idom]
            domqmean =  eve.npemean[idu][idom]
            domtmean =  eve.tmean[idu][idom]
            pos =       [getattr(eve, ii)[idu][idom] for ii in 'xyz']            
            domtheta =  eve.theta[idu][idom]
            domphi =    eve.phi[idu][idom]

            pm.Fill('map3d_trig',  pos[0], pos[1], pos[2])
            pm.Fill('map3d_q',     pos[0], pos[1], pos[2], domqsum)
                        
            for (ii1,ii2) in combpmts[0:len(pmts)-1]:
                ttt = dts[ii1]-dts[ii2]
                qqq = 0.5*(npes[ii1]+npes[ii2])
                pm.Fill(namerdudomx('tdiffs',  du),             ttt,    idx=dom)
                pm.Fill(namerdudomx('tdiffsVnpe',  du),   qqq,  ttt,    idx=dom)    
                pm.Fill('tdiffsVnpe',   qqq,  ttt)    

            for ipmt, (pmt,npe,dt) in enumerate(zip(pmts, npes, dts)):
                
                pm.Fill(namerdudomx('npeVpmt',   du),    pmt, npe,   idx=dom)
                pm.Fill(namerdudomx('dtVpmt',    du),    pmt, dt,    idx=dom)
                pm.Fill(namerdudomx('dtVnpe',    du),    npe, dt,    idx=dom)
                pm.Fill(namerdudomx('npepmt22',  du),         npe,   idx=dom, condition=pmt==10)
                pm.Fill(namerdudomx('dtpmt22',   du),          dt,   idx=dom, condition=pmt==10)                
                
            pm.Fill(namerdudomx('dtpmtfirst',   du),  tfirst := np.min(dts),   idx=dom)                
            
            pm.Fill('qsumVdom',    dom, domqsum,                idx=du)
            pm.Fill('tmeanVdom',   dom, domtmean,               idx=du)
            pm.Fill('thetaVdom',   dom, np.degrees(domtheta),   idx=du)
            pm.Fill('phiVdom',     dom, np.degrees(domphi),     idx=du)
            
            for ii, dd in enumerate(domdists):
                pm.Fill('qsumVdist',  dd, domqsum,  idx=ii)
                pm.Fill('qmeanVdist', dd, domqmean, idx=ii)
                pm.Fill('tmeanVdist', dd, domtmean, idx=ii)
            
            treedom.dset(dict(eve=eve.eve, dom=dom, du=du, pe=domqsum, ti=domtmean, pos=pos, di=domdists, tfirst=tfirst, theta=np.degrees(domtheta), phi=np.degrees(domphi)), fill=True)
            
# TERMINATE ################################################################################################################################################################################################################################################################################################################################################################################################ 

treedom.write()
pm.ProcessBoxes(closefile=True)

