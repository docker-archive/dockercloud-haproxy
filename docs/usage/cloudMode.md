# Running in Docker Cloud (Cloud Mode)

1. Launch the service you want to load-balance using Docker Cloud.

2. Launch the load balancer. To do this, select "Jumpstarts", "Proxies" and select `dockercloud/haproxy`. During the "Environment variables" step of the wizard, link to the service created earlier (the name of the link is not important), and add "Full Access" API role (this will allow HAProxy to be updated dynamically by querying Docker Cloud's API).

	**Note**:
	- If you are using `docker-cloud cli`, or `stackfile`, please set `roles` to `global`
	- Please **DO NOT** set `sequential_deployment: true` on this image.

That's it - the haproxy container will start querying Docker Cloud's API for an updated list of containers in the service and reconfigure itself automatically, including:

* start/stop/terminate containers in the linked application services
* start/stop/terminate/scale up/scale down/redeploy the linked application services
* add new links to HAProxy
* remove old links from HAProxy

## example of stackfile in Docker Cloud:

	web:
	  image: 'dockercloud/hello-world:latest'
	  target_num_containers: 2
	lb:
	  image: 'dockercloud/haproxy:latest'
	  links:
	    - web
	  ports:
	    - '80:80'
	  roles:
	    - global
