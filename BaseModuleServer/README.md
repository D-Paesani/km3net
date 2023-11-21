


docker build -t bmserver .



sudo docker run -v -it -p 5001:5001 -d bmserver


docker images -a   
docler ps -a

docker rmi -f bmserver   



curl localhost:5001
