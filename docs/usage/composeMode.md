# Running with Docker Compose v2 (Compose Mode)

Docker Compose 1.6 supports a new format of the compose file. In the new version(v2), the old link that injects environment variables is deprecated.

Similar to using legacy links, here list some differences that you need to notice:
- This image must be run using Docker Compose, as it relies on the Docker Compose labels for configuration.
- The container needs access to the docker socket, you must mount the correct files and set the related environment to make it work.
- A link is required in order to ensure that dockercloud/haproxy is aware of which service it needs to balance, although links are not needed for service discovery since docker 1.10. Linked aliases are not required.
- DO not overwrite `HOSTNAME` environment variable in `dockercloud/haproxy container`.
- As it is the case on Docker Cloud, auto reconfiguration is supported when the linked services scales or/and the linked container starts/stops.
- The container name is maintained by docker-compose, and used for service discovery as well. Please **DO NOT** change `container_name` of the linked service in the compose file to a non-standard name. Otherwise, that service will be ignored.

## example of docker-compose.yml running on Linux or Docker for Mac (beta):

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

## example of docker-compose.yml running on Mac OS

	version: '2'
	services:
	  web:
	    image: dockercloud/hello-world
	  lb:
	    image: dockercloud/haproxy
	    links:
	      - web
	    environment:
	      - DOCKER_TLS_VERIFY
	      - DOCKER_HOST
	      - DOCKER_CERT_PATH
	    volumes:
	      - $DOCKER_CERT_PATH:$DOCKER_CERT_PATH
	    ports:
	      - 80:80

Once the stack is up, you can scale the web service using `docker-compose scale web=3`. dockercloud/haproxy will automatically reload its configuration.

## Running with Docker Compose v2 and Swarm (using envvar)
When using links like previous section, the Docker Swarm scheduler can be too restrictive.
Even with overlay network, swarm (As of 1.1.0) will attempt to schedule haproxy on the same node as the linked service due to legacy links behavior.
This can cause unwanted scheduling patterns or errors such as "Unable to find a node fulfilling all dependencies..."

Since Compose V2 allows discovery through the service names, Dockercloud haproxy only needs the links to indentify which service should be load balanced.

A second option is to use the `ADDITIONAL_SERVICES` variable for indentification of services.

- Set the `ADDITIONAL_SERVICES` env variable to your linked services.
- You also want to set depends_on to ensure the web service is started before haproxy so that the hostname can be resolved. This controls scheduling order but not location.
- The container still needs access to the docker daemon to get load balanced containers' configs.
- If any trouble with haproxy not updating the config, try running reload.sh or set the `DEBUG` envvar.
- This image is also compatible with Docker Swarm, and supports the docker native `overlay` network across multi-hosts.

## example of docker-compose.yml in 'project_dir' directory running in linux:

	version: '2'
	services:
	  web:
	    image: dockercloud/hello-world
	  blog:
	    image: dockercloud/hello-world
	  lb:
	    image: dockercloud/haproxy
	    depends_on:
	      - web
	      - blog
	    environment:
	      - ADDITIONAL_SERVICES=project_dir:web,project_dir:blog
	    volumes:
	      - /var/run/docker.sock:/var/run/docker.sock
	    ports:
	      - 80:80
