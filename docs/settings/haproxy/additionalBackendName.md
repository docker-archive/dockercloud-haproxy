# Settings: ADDITIONAL_BACKEND_\<NAME>

## Name

ADDITIONAL_BACKEND_FILE_\<NAME>

## Type:

Environment Variable
    
## Location:

`dockercloud/haproxy` container or service

## Default Value

Empty

## Description

Similar to [ADDITIONAL_BACKEND_\<NAME>](additionalBackendFileName.md), it adds an additional backend section to the HAProxy configuration file with the name given in `<NAME>`. 

The \<NAME> is a combination of characters and numbers *([a-zA-Z0-9])*, which will be use at the name of the backend

The value is a comma separated string of a list of HAProxy configurations. Comma is translated to new line character. To escape comma, use `\,`. 

*Note: You probably need to config the frontend that uses this backend to make it work, by using `EXTRA_FRONTEND_SETTINGS_\<PORT\>` for instance.*

## Example

```
-e ADDITIONAL_BACKEND_Foo="balance source, server foo 127.0.0.1:8080"
-e ADDITIONAL_BACKEND_Bar="balance roundrobin, server foo 127.0.0.2:8080"
```

Setting the above environment variables result in adding the following sections to the configuration file:


```
backend Foo
  balance source
  server foo 127.0.0.1:8080
backend Bar
  balance roundrobin
  server foo 127.0.0.2:8080
```