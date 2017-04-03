# dockercloud/haproxy


HAProxy image that balances between linked containers and, if launched in Docker Cloud or using Docker Compose v2,
reconfigures itself when a linked cluster member redeploys, joins or leaves.

## Version

The available version can be found here: https://hub.docker.com/r/dockercloud/haproxy/tags/
 - `latest` is built against master branch
 - `staging` is built against staging branch
 - `x.x.x` is built against git tags on github

**Attention** : Please **ALWAYS** use a specific image tag that works for you. **DO NOT** use `dockercloud/haproxy:latest` in any situation other than testing purpose.

## Usage

You can use `dockercloud/haproxy` in 4 different scenarios:

- [Cloud Mode](docs/usage/cloudMode.md):

Running `dockercloud/haproxy` in Docker Cloud *standard mode*. It can detect the service changes and reconfigure itself automatically by listening Docker Cloud stream events and querying DockerCloud API.
- [Legacy Mode](docs/usage/legacyMode.md):

Running `dockercloud/haproxy` using Docker legacy links *(before docker v1.9.0)* with `docker run --link` flag or Docker Compose v1. In this mode, `dockercloud/haproxy` DOES NOT detecting the changes of underlying service. You have to redeploy the proxy container manually. 
- [Compose Mode](docs/usage/composeMode.md):

Running with Docker Compose v2 *(since docker-compose 1.6)*, compatible with Docker Classic Swarm. Support auto self configuration by listening to docker events.
- [Swarm Mode](docs/usage/swarmMode.md):

Running with Docker Swarm Mode *(since docker v1.12)*, compatible with Docker Cloud *swarm mode*. Support auto self configuration by listening to docker events.

## Configuration

### Global and default settings of HAProxy

Settings in this part is immutable, you have to redeploy HAProxy service to make the changes take effects

|Environment Variable|Default|Description|
|:-----|:-----:|:----------|
|[ADDITIONAL_BACKEND_\<NAME\>](docs/settings/haproxy/additionalBackendName.md)|add an additional backend section with the name \<NAME>
|[ADDITIONAL_BACKEND_FILE_\<NAME\>](docs/settings/haproxy/additionalBackendFileName.md)|add an additional backend section with the name \<NAME> from a file
|[ADDITIONAL_SERVICES](docs/settings/haproxy/additionalServices.md)|add a list of services defined in another docker-compose project. ***Compose mode only***
|[BALANCE](docs/settings/haproxy/balance.md)|the load balancing algorithm to use. Default: `roundrobin`
|[CA_CERT](docs/settings/haproxy/caCert.md)|provide a CA Cert to make HAProxy to verify the client through environment variable|
|[CA_CERT_FILE](docs/settings/haproxy/caCertFile.md)|the path of a ca-cert file. This allows you to mount your ca-cert file directly from a volume instead of from envvar. If set, `CA_CERT` envvar will be ignored. Possible value: `/cacerts/cert0.pem`|
|[CERT_FOLDER](docs/settings/haproxy/certFolder.md)|the path of certificates. This allows you to mount your certificate files directly from a volume instead of from envvars. If set, `DEFAULT_SSL_CERT` and `SSL_CERT` from linked services are ignored. Possible value:`/certs/`|
|[DEFAULT_SSL_CERT](docs/settings/haproxy/defaultSslCert.md)|Default ssl cert, a pem file content with private key followed by public certificate, '\n'(two chars) as the line separator. should be formatted as one line - see [SSL Termination](#ssl-termination)|
|[EXTRA_BIND_SETTINGS](docs/settings/haproxy/extraBindSettings.md)|comma-separated string(`<port>:<setting>`) of extra settings, and each part will be appended to the related port bind section in the configuration file. To escape comma, use `\,`. Possible value: `443:accept-proxy, 80:name http`|
|[EXTRA_DEFAULT_SETTINGS](docs/settings/haproxy/extraDefaultSettings.md)|comma-separated string of extra settings, and each part will be appended to DEFAULT section in the configuration file. To escape comma, use `\,`|
|[EXTRA_DEFAULT_SETTINGS_FILE](docs/settings/haproxy/extraDefaultSettingsFile.md)|File whose contents will be included in the DEFAULT section of the configuration file.|
|[EXTRA_FRONTEND_SETTINGS_\<PORT\>](docs/settings/haproxy/extraFrontendSettingsPort.md)|comma-separated string of extra settings, and each part will be appended frontend section with the port number specified in the name of the envvar. To escape comma, use `\,`. E.g. `EXTRA_FRONTEND_SETTINGS_80=balance source, maxconn 2000`|
|[EXTRA_FRONTEND_SETTINGS_FILE_\<PORT\>](docs/settings/haproxy/extraFrontendSettingsFilePort.md)|File whose contents will be appended to the frontend section with the port number specified in the filename.|
|[EXTRA_GLOBAL_SETTINGS](docs/settings/haproxy/extraGlobalSettings.md)|comma-separated string of extra settings, and each part will be appended to GLOBAL section in the configuration file. To escape comma, use `\,`. Possible value: `tune.ssl.cachesize 20000, tune.ssl.default-dh-param 2048`|
|[EXTRA_GLOBAL_SETTINGS_FILE](docs/settings/haproxy/extraGlobalSettingsFile.md)|File whose contents will be included in the GLOBAL section of the configuration file.|
|[EXTRA_ROUTE_SETTINGS](docs/settings/haproxy/extraRouteSettings.md)|a string which is append to the each backend route after the health check, can be over written in the linked services. Possible value: "send-proxy"|
|[EXTRA_SSL_CERTS](docs/settings/haproxy/extraSsslCerts.md)|list of extra certificate names separated by comma, eg. `CERT1, CERT2, CERT3`. You also need to specify each certificate as separate env variables like so: `CERT1="<cert-body1>"`, `CERT2="<cert-body2>"`, `CERT3="<cert-body3>"`|
|[FORCE_DEFAULT_BACKEND](docs/settings/haproxy/forceDefaultBackend.md)| True | set the default_service as a default backend. This is useful when you have more than one backend and you don't want your default_service as a default backend    
|[HAPROXY_GROUP](docs/settings/haproxy/haproxyGroup.md)|haproxy|sets the group of the UNIX sockets to the designated system group name|
|[HAPROXY_USER](docs/settings/haproxy/haproxyUser.md)|haproxy|sets the user of the UNIX sockets to the designated system user name|
|[HEALTH_CHECK](docs/settings/haproxy/healthCheck.md)|check|set health check on each backend route, possible value: "check inter 2000 rise 2 fall 3". See:[HAProxy:check](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check)|
|[HTTP_BASIC_AUTH](docs/settings/haproxy/httpBasicAuth.md)|a comma-separated list of credentials(`<user>:<pass>`) for HTTP basic auth, which applies to all the backend routes. To escape comma, use `\,`. *Attention:* DO NOT rely on this for authentication in production|
|[HTTP_BASIC_AUTH_SECURE](docs/settings/haproxy/httpBasicAuthSecure.md)|a comma-separated list of credentials(`<user>:<encrypted-pass>`) for HTTP basic auth, which applies to all the backend routes. To escape comma, use `\,`. See:[HAProxy:user](https://cbonte.github.io/haproxy-dconv/1.5/configuration.html#3.4-user) *Attention:* DO NOT rely on this for authentication in production|
|[MAXCONN](docs/settings/haproxy/maxconn.md)|4096|sets the maximum per-process number of concurrent connections.|
|[MODE](docs/settings/haproxy/mode.md)|http|mode of load balancing for HAProxy. Possible values include: `http`, `tcp`, `health`|
|[MONITOR_PORT](docs/settings/haproxy/monitorPort.md)|the port number where monitor_uri should be added to. Use together with `MONITOR_URI`. Possible value: `80`|
|[MONITOR_URI](docs/settings/haproxy/monitorUri.md)|the exact URI which we want to intercept to return HAProxy's health status instead of forwarding the request.See: http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-monitor-uri. Possible value: `/ping`|
|[NBPROC](docs/settings/haproxy/nbproc.md)|1|sets the `nbproc` entry to the `global` section. By default, only one process is created, which is the recommended mode of operation.|
|[OPTION](docs/settings/haproxy/option.md)|redispatch|comma-separated list of HAProxy `option` entries to the `default` section.|
|[RELOAD_TIMEOUT](docs/settings/haproxy/reloadTimeout.md)|0| When haproxy is reconfigured, a new process starts and attaches to the TCP socket for new connections, leaving the old process to handle existing connections.  This timeout specifies how long the old process is permitted to continue running before being killed. <br/>  `-1`: Old process is killed immediately<br/>  `0`: No timeout, old process will run as long as TCP connections last.  This could potentially be quite a while as `http-keep-alives` are enabled which will keep TCP connections open.<br/>  `>0`: Timeout in secs after which the process will be killed.
|[RSYSLOG_DESTINATION](docs/settings/haproxy/rsyslogDestination.md)|127.0.0.1|the rsyslog destination to where HAProxy logs are sent|
|[SKIP_FORWARDED_PROTO](docs/settings/haproxy/skipForwardedProto.md)|If set to any value, HAProxy will not add an X-Forwarded- headers. This can be used when combining HAProxy with another load balancer|
|[SSL_BIND_CIPHERS](docs/settings/haproxy/sslBindCiphers.md)| |explicitly set which SSL ciphers will be used for the SSL server. This sets the HAProxy `ssl-default-bind-ciphers` configuration setting.|
|[SSL_BIND_OPTIONS](docs/settings/haproxy/sslBindOptions.md)|no-sslv3|explicitly set which SSL bind options will be used for the SSL server. This sets the HAProxy `ssl-default-bind-options` configuration setting. The default will allow only TLSv1.0+ to be used on the SSL server.|
|[STATS_AUTH](docs/settings/haproxy/statsAuth.md)|stats:stats|username and password required to access the Haproxy stats.|
|[STATS_PORT](docs/settings/haproxy/statsPort.md)|1936|port for the HAProxy stats section. If this port is published, stats can be accessed at `http://<host-ip>:<STATS_PORT>/`
|[TIMEOUT](docs/settings/haproxy/timeout.md)|connect 5000, client 50000, server 50000|comma-separated list of HAProxy `timeout` entries to the `default` section.|

### Settings in linked application services

Settings here can overwrite the settings in HAProxy, which are only applied to the linked services. If run in Docker Cloud, when the service redeploys, joins or leaves HAProxy service, HAProxy service will automatically update itself to apply the changes

|Environment Variable|Description|
|:-----|:----------|
|[BALANCE]()|load balancing algorithm to use. Possible values include: `roundrobin`, `static-rr`, `source`, `leastconn`. See:[HAProxy:balance](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-balance)|
|[COOKIE]()|sticky session option. Possible value `SRV insert indirect nocache`. See:[HAProxy:cookie](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-cookie)|
|[DEFAULT_SSL_CERT]()|similar to SSL_CERT, but stores the pem file at `/certs/cert0.pem` as the default ssl certs. If multiple `DEFAULT_SSL_CERT` are specified in linked services and HAProxy, the behavior is undefined|
|[EXCLUDE_PORTS]()|if set, the application by the application services to the backend routes. You can exclude the ports that you don't want to be routed, like database port|
|[EXCLUDE_BASIC_AUTH]()|if set(any value) and `HTTP_BASIC_AUTH` global setting is set, no basic auth will be applied to this service.|
|[EXTRA_ROUTE_SETTINGS]()|a string which is append to the each backend route after the health check,possible value: "send-proxy"|
|[EXTRA_SETTINGS]()|comma-separated string of extra settings, and each part will be appended to either related backend section or listen session in the configuration file. To escape comma, use `\,`. Possible value: `balance source`|
|[FAILOVER]()|if set(any value), it configures this service to be run as HAProxy `backup` for other configured service(s) in this backend|
|[FORCE_SSL]()|if set(any value) together with ssl termination enabled. HAProxy will redirect HTTP request to HTTPS request.
|[GZIP_COMPRESSION_TYPE]()|enable gzip compression. The value of this envvar is a list of MIME types that will be compressed. Some possible values: `text/html text/plain text/css application/javascript`. See:[HAProxy:compression](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-compression)|
|[HEALTH_CHECK]()|set health check on each backend route, possible value: "check inter 2000 rise 2 fall 3". See:[HAProxy:check](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check)|
|[HSTS_MAX_AGE]()|enable HSTS. It is an integer representing the max age of HSTS in seconds, possible value: `31536000`|
|[HTTP_CHECK]()|enable HTTP protocol to check on the servers health, possible value: "OPTIONS * HTTP/1.1\r\nHost:\ www". See:[HAProxy:httpchk](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-option%20httpchk)|
|[OPTION]()|comma-separated list of HAProxy `option` entries. `option` specified here will be added to related backend or listen part, and overwrite the OPTION settings in the HAProxy container|
|[SSL_CERT]()|ssl cert, a pem file with private key followed by public certificate, '\n'(two chars) as the line separator|
|[TCP_PORTS]()|comma separated ports(e.g. 9000, 9001, 2222/ssl). The port listed in `TCP_PORTS` will be load-balanced in TCP mode. Port ends with `/ssl` indicates that port needs SSL termination.
|[VIRTUAL_HOST_WEIGHT]()|an integer of the weight of an virtual host, used together with `VIRTUAL_HOST`, default:0. It affects the order of acl rules of the virtual hosts. The higher weight one virtual host has, the more priority that acl rules applies.|
|[VIRTUAL_HOST]()|specify virtual host and virtual path. Format: `[scheme://]domain[:port][/path], ...`. wildcard `*` can be used in `domain` and `path` part|

Swarm Mode only settings:

|Name|Type|Description|
|:---|:---:|:---------|
|[SERVICE_PORTS]()|envvar|comma separated ports(e.g. 80, 8080), which are the ports you would like to expose in your application service. This envvar is swarm mode only, and it is **MUST** be set in swarm mode|
|[com.docker.dockercloud.haproxy.deactivate=<true/false>`]()|label|when this label is set to true, haproxy will ignore the service. Could be useful for switching services on blue/green testing|


Check [the HAProxy configuration manual](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html) for more information on the above.

##### example of stackfile in Docker Cloud with settings in linked application:

	web:
	  image: 'dockercloud/hello-world:latest'
	  target_num_containers: 2
	  environment:
            - TCP_PORTS=443
            - EXCLUDE_PORTS=22
	lb:
	  image: 'dockercloud/haproxy:latest'
	  links:
	    - web
	  ports:
	    - '80:80'
	  roles:
	    - global


## Virtual host and virtual path

Both virtual host and virtual path can be specified in environment variable `VIRTUAL_HOST`, which is a set of comma separated urls with the format of `[scheme://]domain[:port][/path]`.

|Item|Default|Description|
|:---:|:-----:|:---------|
|scheme|http|possible values: `http`, `https`, `wss`|
|domain| |virtual host. `*` can be used as the wildcard|
|port|80/433|port number of the virtual host. When the scheme is `https`  `wss`, the default port will be to `443`|
|/path| |virtual path, starts with `/`. `*` can be used as the wildcard|

[**Here lists some examples of how the mapping works**](docs/vhosts/vhostExample.md)

## SSL termination

`dockercloud/haproxy` supports ssl termination on multiple certificates. For each application that you want ssl terminates, simply set `SSL_CERT` and `VIRTUAL_HOST`. HAProxy, then, reads the certificate from the link environment and sets the ssl termination up.

**Attention**: there was a bug that if an environment variable value contains "=", which is common in the `SSL_CERT`, docker skips that environment variable. As a result, multiple ssl termination only works on docker 1.7.0 or higher, or in Docker Cloud.

SSL termination is enabled when:

1. at least one SSL certificate is set, and
2. either `VIRTUAL_HOST` is not set, or it is set with "https" as the scheme.

To set SSL certificate, you can either:

1. set `DEFAULT_SSL_CERT` in `dockercloud/haproxy`, or
2. set `SSL_CERT` and/or `DEFAULT_SSL_CERT` in the application services linked to HAProxy

The difference between `SSL_CERT` and `DEFAULT_SSL_CERT` is that, the multiple certificates specified by `SSL_CERT` are stored in as cert1.pem, cert2.pem, ..., whereas the one specified by `DEFAULT_SSL_CERT` is always stored as cert0.pem. In that case, HAProxy will use cert0.pem as the default certificate when there is no SNI match. However, when multiple `DEFAULT_SSL_CERT` is provided, only one of the certificates can be stored as cert0.pem, others are discarded.

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
2. set `COOKIE=<value>`. use application cookie to determine which server a client should connect to. Possible value of `<value>` could be `SRV insert indirect nocache`

Check [HAProxy:cookie](http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-cookie) for more information.


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

    docker run -d --expose 8080 --name webapp dockercloud/hello-world
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
