# dockercloud/haproxy


HAProxy image that balances between linked containers and, if launched in Docker Cloud or using Docker Compose v2,
reconfigures itself when a linked cluster member redeploys, joins or leaves.

## Version

- latest: `dockercloud/haproxy:1.2.1`

**Attention** : Please *ALWAYS* use a specific image tag that works for you. Do *NOT* use `dockercloud/haproxy:latest` in any situation other than testing purpose.

## Usage

You can use `dockercloud/haproxy` in three different ways:

- running in Docker Cloud
- running with docker legacy links
- running with Docker Compose v2(new links, compatible with Docker Swarm)

### Running in Docker Cloud

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

##### example of stackfile in Docker Cloud:

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

### Running with docker legacy links

Legacy link refers to the link created before docker 1.10, and the link created in default bridge network in docker 1.10 or after.

##### example of legacy links using docker cli

    docker run -d --name web1 dockercloud/hello-world
    docker run -d --name web2 dockercloud/hello-world
    docker run -d -p 80:80 --link web1:web1 --link web2:web2 dockercloud/haproxy

#### example of docker-compose.yml v1 format:

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


### Running with Docker Compose v2(new links)

Docker Compose 1.6 supports a new format of the compose file. In the new version(v2), the old link that injects environment variables is deprecated.

Similar to using legacy links, here list some differences that you need to notice:
- This image must be run using Docker Compose, as it relies on the Docker Compose labels for configuration.
- The container needs access to the docker socket, you must mount the correct files and set the related environment to make it work.
- A link is required in order to ensure that dockercloud/haproxy is aware of which service it needs to balance, although links are not needed for service discovery since docker 1.10. Linked aliases are not required.
- DO not overwrite `HOSTNAME` environment variable in `dockercloud/haproxy container`.
- As it is the case on Docker Cloud, auto reconfiguration is supported when the linked services scales or/and the linked container starts/stops.

##### example of docker-compose.yml running on Linux or Docker for Mac (beta):

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

##### example of docker-compose.yml running on Mac OS

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

#### Running with Docker Compose v2 and Swarm (using envvar)
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

##### example of docker-compose.yml in 'project_dir' directory running in linux:

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

## Configuration

### Global and default settings of HAProxy###

Settings in this part is immutable, you have to redeploy HAProxy service to make the changes take effects

|Environment Variable|Default|Description|
|:-----:|:-----:|:----------|
|ADDITIONAL_SERVICES| |list of additional services to balance (es: `prj1:web,prj2:sql`). Discovery will be based on `com.docker.compose.[project|service]` container labels. This environment variable only works on compose v2, and the referenced services must be on a network accessible to this containers.|
|BALANCE|roundrobin|load balancing algorithm to use. Possible values include: `roundrobin`, `static-rr`, `source`, `leastconn`. See:[HAProxy:balance](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-balance)|
|CA_CERT_FILE| |the path of a ca-cert file. This allows you to mount your ca-cert file directly from a volume instead of from envvar. If set, `CA_CERT` envvar will be ignored. Possible value: `/cacerts/cert0.pem`|
|CA_CERT| |CA cert for haproxy to verify the client. Use the same format as `DEFAULT_SSL_CERT`|
|CERT_FOLDER| |the path of certificates. This allows you to mount your certificate files directly from a volume instead of from envvars. If set, `DEFAULT_SSL_CERT` and `SSL_CERT` from linked services are ignored. Possible value:`/certs/`|
|DEFAULT_SSL_CERT| |Default ssl cert, a pem file content with private key followed by public certificate, '\n'(two chars) as the line separator. should be formatted as one line - see [SSL Termination](#ssl-termination)|
|EXTRA_BIND_SETTINGS| |comma-separated string(`<port>:<setting>`) of extra settings, and each part will be appended to the related port bind section in the configuration file. To escape comma, use `\,`. Possible value: `443:accept-proxy, 80:name http`|
|EXTRA_DEFAULT_SETTINGS| |comma-separated string of extra settings, and each part will be appended to DEFAULT section in the configuration file. To escape comma, use `\,`|
|EXTRA_FRONTEND_SETTINGS_\<PORT\>| |comma-separated string of extra settings, and each part will be appended frontend section with the port number specified in the name of the envvar. To escape comma, use `\,`. E.g. `EXTRA_FRONTEND_SETTINGS_80=balance source, maxconn 2000`|
|EXTRA_GLOBAL_SETTINGS| |comma-separated string of extra settings, and each part will be appended to GLOBAL section in the configuration file. To escape comma, use `\,`. Possible value: `tune.ssl.cachesize 20000, tune.ssl.default-dh-param 2048`|
|EXTRA_SSL_CERTS| |list of extra certificate names separated by comma, eg. `CERT1, CERT2, CERT3`. You also need to specify each certificate as separate env variables like so: `CERT1="<cert-body1>"`, `CERT2="<cert-body2>"`, `CERT3="<cert-body3>"`|
|HEALTH_CHECK|check|set health check on each backend route, possible value: "check inter 2000 rise 2 fall 3". See:[HAProxy:check](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check)|
|HTTP_BASIC_AUTH| |a comma-separated list of credentials(`<user>:<pass>`) for HTTP basic auth, which applies to all the backend routes. To escape comma, use `\,`. *Attention:* DO NOT rely on this for authentication in production|
|MAXCONN|4096|sets the maximum per-process number of concurrent connections.|
|MODE|http|mode of load balancing for HAProxy. Possible values include: `http`, `tcp`, `health`|
|MONITOR_PORT| |the port number where monitor_uri should be added to. Use together with `MONTIOR_URI`. Possible value: `80`|
|MONITOR_URI| |the exact URI which we want to intercept to return HAProxy's health status instead of forwarding the request.See: http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-monitor-uri. Possible value: `/ping`|
|OPTION|redispatch|comma-separated list of HAProxy `option` entries to the `default` section.|
|RSYSLOG_DESTINATION|127.0.0.1|the rsyslog destination to where HAProxy logs are sent|
|SSL_BIND_CIPHERS| |explicitly set which SSL ciphers will be used for the SSL server. This sets the HAProxy `ssl-default-bind-ciphers` configuration setting.|
|SSL_BIND_OPTIONS|no-sslv3|explicitly set which SSL bind options will be used for the SSL server. This sets the HAProxy `ssl-default-bind-options` configuration setting. The default will allow only TLSv1.0+ to be used on the SSL server.|
|STATS_AUTH|stats:stats|username and password required to access the Haproxy stats.|
|STATS_PORT|1936|port for the HAProxy stats section. If this port is published, stats can be accessed at `http://<host-ip>:<STATS_PORT>/`
|TIMEOUT|connect 5000, client 50000, server 50000|comma-separated list of HAProxy `timeout` entries to the `default` section.|

### Settings in linked application services###

Settings here can overwrite the settings in HAProxy, which are only applied to the linked services. If run in Docker Cloud, when the service redeploys, joins or leaves HAProxy service, HAProxy service will automatically update itself to apply the changes

|Environment Variable|Description|
|:-----:|:----------|
|APPSESSION|sticky session option, possible value `JSESSIONID len 52 timeout 3h`. See:[HAProxy:appsession](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-appsession)|
|BALANCE|load balancing algorithm to use. Possible values include: `roundrobin`, `static-rr`, `source`, `leastconn`. See:[HAProxy:balance](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-balance)|
|COOKIE|sticky session option. Possible value `SRV insert indirect nocache`. See:[HAProxy:cookie](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-cookie)|
|DEFAULT_SSL_CERT|similar to SSL_CERT, but stores the pem file at `/certs/cert0.pem` as the default ssl certs. If multiple `DEFAULT_SSL_CERT` are specified in linked services and HAProxy, the behavior is undefined|
|EXCLUDE_PORTS|comma separated port numbers(e.g. 3306, 3307). By default, HAProxy will add all the ports exposed by the application services to the backend routes. You can exclude the ports that you don't want to be routed, like database port|
|EXTRA_SETTINGS|comma-separated string of extra settings, and each part will be appended to either related backend section or listen session in the configuration file. To escape comma, use `\,`. Possible value: `balance source`|
|FORCE_SSL|if set(any value) together with ssl termination enabled. HAProxy will redirect HTTP request to HTTPS request.
|GZIP_COMPRESSION_TYPE|enable gzip compression. The value of this envvar is a list of MIME types that will be compressed, possible value: `text/html text/plain text/css`|
|HEALTH_CHECK|set health check on each backend route, possible value: "check inter 2000 rise 2 fall 3". See:[HAProxy:check](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check)|
|HSTS_MAX_AGE|enable HSTS. It is an integer representing the max age of HSTS in seconds, possible value: `31536000`|
|HTTP_CHECK|enable HTTP protocol to check on the servers health, possible value: "OPTIONS * HTTP/1.1\r\nHost:\ www". See:[HAProxy:httpchk](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-option%20httpchk)|
|OPTION|comma-separated list of HAProxy `option` entries. `option` specified here will be added to related backend or listen part, and overwrite the OPTION settings in the HAProxy container|
|SSL_CERT|ssl cert, a pem file with private key followed by public certificate, '\n'(two chars) as the line separator|
|TCP_PORTS|comma separated ports(e.g. 9000, 9001, 2222/ssl). The port listed in `TCP_PORTS` will be load-balanced in TCP mode. Port ends with `/ssl` indicates that port needs SSL termination.
|VIRTUAL_HOST_WEIGHT|an integer of the weight of an virtual host, used together with `VIRTUAL_HOST`, default:0. It affects the order of acl rules of the virtual hosts. The higher weight one virtual host has, the more priority that acl rules applies.|
|VIRTUAL_HOST|specify virtual host and virtual path. Format: `[scheme://]domain[:port][/path], ...`. wildcard `*` can be used in `domain` and `path` part|

Check [the HAProxy configuration manual](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html) for more information on the above.

## Virtual host and virtual path

Both virtual host and virtual path can be specified in environment variable `VIRTUAL_HOST`, which is a set of comma separated urls with the format of `[scheme://]domain[:port][/path]`.

|Item|Default|Description|
|:---:|:-----:|:---------|
|scheme|http|possible values: `http`, `https`, `wss`|
|domain||virtual host. `*` can be used as the wildcard|
|port|80/433|port number of the virtual host. When the scheme is `https`  `wss`, the default port will be to `443`|
|/path||virtual path, starts with `/`. `*` can be used as the wildcard|

#### examples of matching

|Virtual host|Match|Not match|
|:-----------|:----|:--------|
|http://example.com|example.com|www.example.com|
|example.com|example.com|www.example.com|
|example.com:90|example.com:90|example.com|
|https://example.com|https://example.com|example.com|
|https://example.com:444|https://example.com:444|https://example.com|
|\*.example.com|www.example.com|example.com|
|\*example.com|www.example.com, example.com, anotherexample.com|www.abc.com|
|www.e\*e.com|www.example.com, www.exxe.com|www.axxa.com|
|www.example.\*|www.example.com, www.example.org|example.com|
|\*|any website with HTTP||
|https://\*|any website with HTTPS||
|\*/path|example.com/path, example.org/path?u=user|example.com/path/|
|\*/path/|example.com/path/, example.org/path/?u=user|example.com/path, example.com/path/abc|
|\*/path/\*|example.com/path/, example.org/path/abc|example.com/abc/path/
|\*/\*/path/\*|example.com/path/, example.org/abc/path/, example.net/abc/path/123|example.com/path|
|\*/\*.js|example.com/abc.js, example.org/path/abc.js|example.com/abc.css|
|\*/\*.do/|example.com/abc.do/, example.org/path/abc.do/|example.com/abc.do|
|\*/path/\*.php|example.com/path/abc.php|example/abc.php, example.com/root/abc.php|
|\*.example.com/\*.jpg|www.example.com/abc.jpg, abc.example.com/123.jpg|example.com/abc.jpg|
|\*/path, \*/path/|example.com/path, example.org/path/||
|example.com:90, https://example.com|example.com:90, https://example.com||

**Note**:
1. The sequence of the acl rules generated based on VIRTUAL_HOST are random. In HAProxy, when an acl rule with a wide scope(e.g. *.example.com) is put before a rule with narrow scope(e.g. web.example.com), the narrow rule will never be reached. As a result, if the virtual hosts you set have overlapping scopes, you need to use `VIRTUAL_HOST_WEIGHT` to manually set the order of acl rules, namely, giving the narrow virtual host a higher weight than the wide one.
2. Every service that has the same VIRTUAL_HOST environment variable setting will be considered and merged into one single service. It may be useful for some testing scenario.

## SSL termination

`dockercloud/haproxy` supports ssl termination on multiple certificates. For each application that you want ssl terminates, simply set `SSL_CERT` and `VIRTUAL_HOST`. HAProxy, then, reads the certificate from the link environment and sets the ssl termination up.

**Attention**: there was a bug that if an environment variable value contains "=", which is common in the `SSL_CERT`, docker skips that environment variable. As a result, multiple ssl termination only works on docker 1.7.0 or higher, or in Docker Cloud.

SSL termination is enabled when:

1. at least one SSL certificate is set, and
2. either `VIRTUAL_HOST` is not set, or it is set with "https" as the scheme.

To set SSL certificate, you can either:

1. set `DEFAULT_SSL_CERT` in `dockercloud/haproxy`, or
2. set `SSL_CERT` and/or `DEFAULT_SSL_CERT` in the application services linked to HAProxy

The difference between `SSL_CERT` and `DEFAULT_SSL_CERT` is that, the multiple certificates specified by `SSL_CERT` are stored in as cert1.pem, cert2.pem, ..., whereas the one specified by `DEFAULT_SSL_CERT` is always stored as cert0.pem. In that case, HAProxy will use cert0.pem as the default certificate when there is no SNI match. However, when multiple `DEFAULT_SSL_CERTIFICATE` is provided, only one of the certificates can be stored as cert0.pem, others are discarded.

#### PEM Files
The certificate specified in `dockercloud/haproxy` or in the linked application services is a pem file, containing a private key followed by a public certificate(private key must be put before the public certificate and any extra Authority certificates, order matters). You can run the following script to generate a self-signed certificate:

	openssl req -x509 -newkey rsa:2048 -keyout key.pem -out ca.pem -days 1080 -nodes -subj '/CN=*/O=My Company Name LTD./C=US'
	cp key.pem cert.pem
	cat ca.pem >> cert.pem

Once you have the pem file, you can run this command to convert the file correctly to one line:

	awk 1 ORS='\\n' cert.pem

Copy the output and set it as the value of `SSL_CERT` or `DEFAULT_SSL_CERT`.

## Affinity and session stickiness

There are three method to setup affinity and sticky session:

1. set `BALANCE=source` in your application service. When setting `source` method of balance, HAProxy will hash the client IP address and make sure that the same IP always goes to the same server.
2. set `APPSESSION=<value>`. use application session to determine which server a client should connect to. Possible value of `<value>` could be `JSESSIONID len 52 timeout 3h`
2. set `COOKIE=<value>`. use application cookie to determine which server a client should connect to. Possible value of `<value>` could be `SRV insert indirect nocache`

Check [HAProxy:appsession](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-appsession) and [HAProxy:cookie](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-cookie) for more information.


## TCP load balancing

By default, `dockercloud/haproxy` runs in `http` mode. If you want a linked service to run in a `tcp` mode, you can specify the environment variable `TCP_PORTS`, which is a comma separated ports(e.g. 9000, 9001).

For example, if you run:

	docker --name app-1 --expose 9000 --expose 9001 -e TCP_PORTS="9000, 9001" your_app
	docker --name app-2 --expose 9000 --expose 9001 -e TCP_PORTS="9000, 9001" your_app
	docker run --link app-1:app-1 --link app-2:app-2 -p 9000:9000, 9001:9001 dockercloud/haproxy

Then, haproxy balances the load between `app-1` and `app-2` in both port `9000` and `9001` respectively.

Moreover, If you have more exposed ports than `TCP_PORTS`, the rest of the ports will be balancing using `http` mode.

For example, if you run:

	docker --name app-1 --expose 80 --expose 22 -e TCP_PORTS=22 your_app
	docker --name app-2 --expose 80 --expose 22 -e TCP_PORTS=22 your_app
	docker run --link app-1:app-2 --link app-2:app-2 -p 80:80 -p 22:22 dockercloud/haproxy

Then, haproxy balances in `http` mode at port `80` and balances in `tcp` on port at port `22`.

In this way, you can do the load balancing both in `tcp` and in `http` at the same time.

In `TCP_PORTS`, if you set port that ends with '/ssl', for example `2222/ssl`, HAProxy will set ssl termination on port `2222`.

Note:

1. You are able to set `VIRTUAL_HOST` and `TCP_PORTS` at the same them, giving more control on `http` mode.
2. Be careful that, the load balancing on `tcp` port is applied to all the services. If you link two(or more) different services using the same `TCP_PORTS`, `dockercloud/haproxy` considers them coming from the same service.

## WebSocket support
-----------------

There are two ways to enable the support of websocket:

1. As websocket starts using HTTP protocol, you can use virtual host to specify the scheme using `ws` or `wss`. For example, `-e VIRTUAL_HOST="ws://ws.example.com, wss://wss.example.com"
2. Websocket itself is a TCP connection, you can also try the TCP load balancing mentioned in the previous section.


## Use case scenarios

#### My webapp container exposes port 8080(or any other port), and I want the proxy to listen in port 80

Use the following:

    docker run -d --expose 80 --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 80:80 dockercloud/haproxy

#### My webapp container exposes port 80 and database ports 8083/8086, and I want the proxy to listen in port 80 without my database ports added to haproxy

    docker run -d -e EXCLUDE_PORTS=8803,8806 --expose 80 --expose 8033 --expose 8086 --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 80:80 dockercloud/haproxy

#### My webapp container exposes port 8080(or any other port), and I want the proxy to listen in port 8080

Use the following:

    docker run -d --expose 8080 --name webapp your_app
    docker run -d --link webapp:webapp -p 8080:80 dockercloud/haproxy

#### I want the proxy to terminate SSL connections and forward plain HTTP requests to my webapp to port 8080(or any port)

Use the following:

    docker run -d -e SSL_CERT="YOUR_CERT_TEXT" --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 443:443 -p 80:80 dockercloud/haproxy

or

    docker run -d --link webapp:webapp -p 443:443 -p 80:80 -e DEFAULT_SSL_CERT="YOUR_CERT_TEXT" dockercloud/haproxy

The certificate in `YOUR_CERT_TEXT` is a combination of private key followed by public certificate. Remember to put `\n` between each line of the certificate. A way to do this, assuming that your certificate is stored in `~/cert.pem`, is running the following:

    docker run -d --link webapp:webapp -p 443:443 -p 80:80 -e DEFAULT_SSL_CERT="$(awk 1 ORS='\\n' ~/cert.pem)" dockercloud/haproxy

#### I want the proxy to terminate SSL connections and redirect HTTP requests to HTTPS

Use the following:

    docker run -d -e FORCE_SSL=yes -e SSL_CERT="YOUR_CERT_TEXT" --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 443:443 dockercloud/haproxy

#### I want to load my SSL certificate from volume instead of passing it through environment variable

You can use `CERT_FOLDER` envvar to specify which folder the certificates are mounted in the container, using the following:

    docker run -d --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -e CERT_FOLDER="/certs/" -v $(pwd)/cert1.pem:/certs/cert1.pem -p 443:443 dockercloud/haproxy

#### I want to set up virtual host routing by domain

Virtual hosts can be configured by the proxy reading linked container environment variables (`VIRTUAL_HOST`). Here is an example:

    docker run -d -e VIRTUAL_HOST="www.webapp1.com, www.webapp1.org" --name webapp1 dockercloud/hello-world
    docker run -d -e VIRTUAL_HOST=www.webapp2.com --name webapp2 your/webapp2
    docker run -d --link webapp1:webapp1 --link webapp2:webapp2 -p 80:80 dockercloud/haproxy

In the example above, when you access `http://www.webapp1.com` or `http://www.webapp1.org`, it will show the service running in container `webapp1`, and `http://www.webapp2.com` will go to container `webapp2`.

If you use the following:

    docker run -d -e VIRTUAL_HOST=www.webapp1.com --name webapp1 dockercloud/hello-world
    docker run -d -e VIRTUAL_HOST=www.webapp2.com --name webapp2-1 dockercloud/hello-world
    docker run -d -e VIRTUAL_HOST=www.webapp2.com --name webapp2-2 dockercloud/hello-world
    docker run -d --link webapp1:webapp1 --link webapp2-1:webapp2-1 --link webapp2-2:webapp2-2 -p 80:80 dockercloud/haproxy

When you access `http://www.webapp1.com`, it will show the service running in container `webapp1`, and `http://www.webapp2.com` will go to both containers `webapp2-1` and `webapp2-2` using round robin (or whatever is configured in `BALANCE`).

#### I want all my `*.node.io` domains point to my service

    docker run -d -e VIRTUAL_HOST="*.node.io" --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 80:80 dockercloud/haproxy

#### I want `web.example.com` go to one service and `*.example.com` go to another service

    docker run -d -e VIRTUAL_HOST="web.example.com" -e VIRTUAL_HOST_WEIGHT=1 --name webapp dockercloud/hello-world
    docker run -d -e VIRTUAL_HOST="*.example.com" -e VIRTUAL_HOST_WEIGHT=0 --name app dockercloud/hello-world
    docker run -d --link webapp:webapp --link app:app -p 80:80 dockercloud/haproxy

#### I want all the requests to path `/path` point to my service

	docker run -d -e VIRTUAL_HOST="*/path, */path/*" --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 80:80 dockercloud/haproxy

#### I want all the static html request point to my service

	docker run -d -e VIRTUAL_HOST="*/*.htm, */*.html" --name webapp dockercloud/hello-world
    docker run -d --link webapp:webapp -p 80:80 dockercloud/haproxy

#### I want to see stats of HAProxy

	docker run -d --link webapp:webapp -e STATS_AUTH="auth:auth" -e STATS_PORT=1936 -p 80:80 -p 1936:1936 dockercloud/haproxy

#### I want to send all my logs to papertrailapp

Replace `<subdomain>` and `<port>` with your the values matching your papertrailapp account:

    docker run -d --name web1 dockercloud/hello-world
    docker run -d --name web2 dockercloud/hello-world
    docker run -it --env RSYSLOG_DESTINATION='<subdomain>.papertrailapp.com:<port>' -p 80:80 --link web1:web1 --link web2:web2 dockercloud/haproxy

## Topologies using virtual hosts


Docker Cloud or Docker Compose v2:

                                                               |---- container_a1
                                        |----- service_a ----- |---- container_a2
                                        |   (virtual host a)   |---- container_a3
    internet --- dockercloud/haproxy--- |
                                        |                      |---- container_b1
                                        |----- service_b ----- |---- container_b2
                                            (virtual host b)   |---- container_b3


Legacy links:

                                        |---- container_a1 (virtual host a) ---|
                                        |---- container_a2 (virtual host a) ---|---logic service_a
                                        |---- container_a3 (virtual host a) ---|
    internet --- dockercloud/haproxy--- |
                                        |---- container_b1 (virtual host b) ---|
                                        |---- container_b2 (virtual host b) ---|---logic service_b
                                        |---- container_b3 (virtual host b) ---|

## Manually reload haproxy

In most cases, `dockercloud/haproxy` will configure itself automatically when the linked services change, you don't need to reload it manually. But for some reason, if you have to do so, here is how:

* `docker exec <haproxy_id> /reload.sh`, if you are on the node where dockercloud/haproxy deploys
* `docker-cloud exec <haproxy_uuid> /reload.sh`, if you use docker-cloud cli
