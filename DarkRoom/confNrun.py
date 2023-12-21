import os
import argparse

runformat = 'KM3NeT_00000168_00000%s.root'

parser = argparse.ArgumentParser(description='Configuration tool for runs')
parser.add_argument('--getruns',         type=int,   default=[], nargs='+')
parser.add_argument('--runtot',          type=int,   default=[], nargs='+')
parser.add_argument('--runlaser',        type=int,   default=[], nargs='+')
parser.add_argument('--conftot',         type=str,   default='VENDOR_L0')
parser.add_argument('--conflaser',       type=str,   default='LASER_PATCHED_PMT08_t73_464_L0__EXAMPLE')
parser.add_argument('--dorun',           type=int,   default=0)

args = parser.parse_args()

print('loading env')
os.system('module load jpp/17.0.0-rc.1')

for ii in args.getruns:
    print('getting run ', ii)
    os.system(F'rsync -ah --progress /sps/km3net/users/smastroi/caserta/D2DU100CE/KM3NeT_00000168_00000{ii}.root ./runs/')

if args.runtot != [] and args.runlaser != []:
    with open('run_list.txt', 'w') as fff:
        print('creating runlist')
        fff.write('\n')
        fff.writelines([F'\n{runformat%str(ii)} tot {args.conftot}' for ii in args.runtot])
        fff.write('\n')
        fff.writelines([F'\n{runformat%str(ii)} laser {args.conflaser}' for ii in args.runlaser])

        print('getting runs')
        os.system('sh get_runs.sh')

if args.dorun:
    
    os.system('module load jpp/17.0.0-rc.1')
    os.system('sh get_runs.sh')
    
    os.chdir('tot')
    os.system('pwd')
    os.system('sh loop_checktot.sh')
    os.chdir('..')
    os.chdir('laser')
    os.system('sh loop_pulsar.sh')
    
#add remove symlink and --force flag to rerun
