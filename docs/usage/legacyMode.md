# Running with Docker legacy links (Legacy Mode)

Legacy link refers to the link created before docker 1.10, and the link created in default bridge network in docker 1.10 or after.

## example of legacy links using docker cli

    docker run -d --name web1 dockercloud/hello-world
    docker run -d --name web2 dockercloud/hello-world
    docker run -d -p 80:80 --link web1:web1 --link web2:web2 dockercloud/haproxy

## example of docker-compose.yml v1 format:

	web1:
	  image: 'dockercloud/hello-world:latest'
	web2:
	  image: 'dockercloud/hello-world:latest'
	lb:
	  image: 'dockercloud/haproxy:latest'
	  links:
	    - web1
	    - web2
	  ports:
	    - '80:80'

**Note**: Any link alias sharing the same prefix and followed by "-/_" with an integer is considered to be from the same service. For example: `web-1` and `web-2` belong to service `web`, `app_1` and `app_2` are from service `app`, but `app1` and `web2` are from different services.


