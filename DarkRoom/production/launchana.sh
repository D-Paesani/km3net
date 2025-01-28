#!/bin/bash

DU="114"
DUDU="0"
SSH_PASS='CCA!xxxx'

cmd1="cd /sps/km3net/users/xxx/Process3/D${DUDU}DU${DU}CT/"
cmd2="module load jpp/18.5.0"
cmd3="python3 confNrun.py ${1}"

echo
echo D${DUDU}DU${DU}CT
echo 

echo
echo $cmd3 
echo 

sshpass -p $SSH_PASS ssh -t xxx@cca.in2p3.fr << EOF
$cmd1
$cmd2
$cmd3
EOF