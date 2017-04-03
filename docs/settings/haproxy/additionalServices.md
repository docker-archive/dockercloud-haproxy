# Settings: ADDITIONAL_SERVICES

## Name

ADDITIONAL_SERVICES

## Type:

Environment Variable
    
## Location:

`dockercloud/haproxy` container or service

## Default Value

Empty

## Limit

Compose mode only

## Description

This environment allows you to add a list of services that is defined in another docker-compose project. The format is `project1:blog, project2:www`, separated by comma. Service discovery will be based on container labels `com.docker.compose.[project|service]`. referenced services must be on a network resolvable and accessible to this containers.

*Note: You have to make sure that the services added to the load balancer are accessible and resolvable by the `dockercloud/haproxy` container*

## Example

1. Create a network named `lb`:

```
docker network create --driver bridge lb
```
2. Create and run 3 docker-compose projects with following content:

```bash
$ cat docker-compose-project1.yml

version: '2'
services:
    news:
        image: dockercloud/hello-world
    blog:
        image: dockercloud/hello-world
networks:
    default:
        external:
            name: lb
```

```bash
$ cat docker-compose-project2.yml

version: '2'
services:
    support:
        image: dockercloud/hello-world
    www:
        image: dockercloud/hello-world
networks:
    default:
        external:
            name: lb
```

```bash
$ cat docker-compose-lb.yml

version: '2'
services:
    web:
        image: dockercloud/hello-world
    lb:
        image: dockercloud/haproxy
        links:
            - web
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
        ports:
            - 80:80
        environment:
            - ADDITIONAL_SERVICES=project1:blog, project2:www
networks:
    default:
        external:
            name: lb
```

3. Run the following commands to create an run the projects:

```bash
$ docker-compose -p project1 -f docker-compose-project1.yml up -d
$ docker-compose -p project2 -f docker-compose-project2.yml up -d
$ docker-compose -p lb -f docker-compose-lb.yml up -d
```

4. You will find `project1_blog_1` and `project2_www` are added to the load balancer:

```
lb_1  | backend default_service
lb_1  |   server lb_web_1 lb_web_1:80 check inter 2000 rise 2 fall 3
lb_1  |   server project1_blog_1 project1_blog_1:80 check inter 2000 rise 2 fall 3
lb_1  |   server project2_www_1 project2_www_1:80 check inter 2000 rise 2 fall 3
```