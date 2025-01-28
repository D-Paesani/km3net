

SSH_PASS='yourpassw'

dulist=(D0DU107CT D0DU102CT)
dulist=(D0DU114CT)

for i in "${!dulist[@]}"
do
    printf "\n\n ${dulist[i]} \n\n"

    sshpass -p $SSH_PASS rsync -ah --progress yyy@cca.in2p3.fr:/sps/km3net/users/xxx/Process3/${dulist[i]}/tot/output/*.png ../tot/ 
    sshpass -p $SSH_PASS rsync -ah --progress yyy@cca.in2p3.fr:/sps/km3net/users/xxx/Process3/${dulist[i]}/tot/output/more/*.root ../tot/more/ 
    sshpass -p $SSH_PASS rsync -ah --progress yyy@cca.in2p3.fr:/sps/km3net/users/xxx/Process3/${dulist[i]}/laser/output/more/*.root ../data/
    
done