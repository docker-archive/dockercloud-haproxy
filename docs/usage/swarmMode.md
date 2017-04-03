# Running with Docker SwarmMode (Swarm Mode)

Docker 1.12 supports SwarmMode natively. `dockercloud/haproxy` will auto config itself to load balance all the services running on the same network:

1. Create a new network using `docker network create -d overlay <name>` command

2. Launch `dockercloud/haproxy` service on that network on manager nodes.

3. Launch your application services that need to be load balanced on the same network.

    **Note**
    - You **HAVE TO** set the environment variable `SERVICE_PORTS=<port1>, <port2>` in your application service, which are the ports you would like to expose.
    - For `dockercloud/haproxy` service:
      If you mount `/var/run/docker.sock`, it can only be run on swarm manager nodes.
      If you want the haproxy service to run on worker nodes, you need to setup DOCKER_HOST envvar that points to the manager address.

* If your application services need to access other services(database, for example), you can attach your application services to two different network, one is for database and the other one for the proxy
* This feature is still experimental, please let us know if you find any bugs or have any suggestions.

## example of docker swarm mode support

    docker network create -d overlay proxy
    docker service create --name haproxy --network proxy --mount target=/var/run/docker.sock,source=/var/run/docker.sock,type=bind -p 80:80 --constraint "node.role == manager" dockercloud/haproxy
    docker service create -e SERVICE_PORTS="80" --name app --network proxy --constraint "node.role != manager" dockercloud/hello-world
    docker service scale app=2
    docker service update --env-add VIRTUAL_HOST=web.org app
