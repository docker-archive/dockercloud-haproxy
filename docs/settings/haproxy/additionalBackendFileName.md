# Settings: ADDITIONAL_BACKEND_FILE_\<NAME>

## Name

ADDITIONAL_BACKEND_FILE_\<NAME>

## Type:

Environment Variable
    
## Location:

`dockercloud/haproxy` container or service

## Default Value

Empty

## Description

Add an additional backend section to the HAProxy configuration file with the name given in `<NAME>`. This could be useful to if you want to let HAProxy load balance on a service that is either not in the current stack or not running in containers, for example.

## Usage

The \<NAME> is a combination of characters and numbers *([a-zA-Z0-9])*, which will be use at the name of the backend

The value is the path of a file, whose content is a comma separated string of a list of HAProxy configurations. Comma is translated to new line character. To escape comma, use `\,`. 

*Note: You probably need to config the frontend that uses this backend to make it work, by using `EXTRA_FRONTEND_SETTINGS_\<PORT\>` for instance.*

## Example

```bash
$ cat Foo
balance source
maxconn 2048
server foo1 127.0.0.1:8080
server foo2 127.0.0.2:8080

$ cat Bar
balance roundrobin
maxconn 1024
server bar1 127.0.0.3:8080
server bar2 127.0.0.4:8080
```

```
-e ADDITIONAL_BACKEND_FILE_Foo="/conf/Foo"
-v $(pwd)/Foo:/conf/Foo
-e ADDITIONAL_BACKEND_FILE_Bar="/conf/Bar"
-v $(pwd)/Bar:/conf/Bar
```

Setting the above environment variables result in adding the following sections to the configuration file:

```
backend Foo
  balance source
  maxconn 2048
  server foo1 127.0.0.1:8080
  server foo2 127.0.0.2:8080
backend Bar
  balance roundrobin
  maxconn 1024
  server bar1 127.0.0.3:8080
  server bar2 127.0.0.4:8080
```