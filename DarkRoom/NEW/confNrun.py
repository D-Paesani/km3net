# daniele.paesani@lns.infn.it

import os, argparse

loadenv = 'module load jpp/17.0.0-rc.1'
duid = 202
dudu = 'D0DU114CT'
runformat = F'KM3NeT_{duid:08d}_%08d.root'
getformat = F'rsync -ah --progress /sps/km3net/users/gferrara/antares_km3/dark_room/{dudu}/runs/{runformat} ./runs/'

parser = argparse.ArgumentParser(description=F'Configuration tool for runs [ {loadenv} ]')

parser.add_argument('--autoget',         type=int,   default=0)
parser.add_argument('--getruns',         type=int,   default=[], nargs='+')
parser.add_argument('--totven',          type=int,   default=[], nargs='+')
parser.add_argument('--tottun',          type=int,   default=[], nargs='+')
parser.add_argument('--laser',           type=int,   default=[], nargs='+')
parser.add_argument('--autolaser',       type=int,   default=1)
parser.add_argument('--conftotven',      type=str,   default='VENDOR_L0')
parser.add_argument('--conftottun',      type=str,   default='TUNED_L0')
parser.add_argument('--conflaser',       type=str,   default='LASER_PATCHED_PMT%02d_t74_463_L0__EXAMPLE')
parser.add_argument('--pmtlaser',        type=int,   default=[7,15], nargs='+')
parser.add_argument('--dorun',           type=int,   default=1)
parser.add_argument('--cleartot',        type=int,   default=1)
parser.add_argument('--clearlaser',      type=int,   default=1)

args = parser.parse_args()

if args.cleartot: os.system('rm ./tot/runs/*.root')
if args.clearlaser: os.system('rm ./laser/runs/*.root')
    
allruns = []
for ii in ['totven', 'tottun', 'laser']:  
    allruns = list(set(allruns)|set(getattr(args, ii)))
allruns.sort()

if args.autoget:   args.getruns = allruns  
if args.autolaser: args.laser = allruns  

for ii in args.getruns:
    print('getting run ', ii)
    os.system(getformat%ii)

if allruns:
    with open('run_list.txt', 'w') as fff:
        print('creating runlist')
                
        fff.write('\n')
        fff.writelines([F'\n{runformat%ii} tot     {args.conftotven}'  for ii in    args.totven])
        fff.write('\n')
        fff.writelines([F'\n{runformat%ii} tot     {args.conftottun}'  for ii in    args.tottun])
        fff.write('\n')
        for claser in [args.conflaser%ipmt for ipmt in args.pmtlaser]:
            fff.writelines([F'\n{runformat%ii} laser   {claser}'   for ii in    args.laser])

        print('getting runs')
        os.system('sh get_runs.sh')

if args.dorun:
    
    os.system('sh get_runs.sh')
    
    os.chdir('tot')
    os.system('sh loop_checktot.sh')
    os.chdir('..')
    os.chdir('laser')
    os.system('sh loop_pulsar.sh')
    
