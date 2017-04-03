# Settings: BALANCE

## Name

BALANCE

## Type:

Environment Variable
    
## Location:

`dockercloud/haproxy` container or service

## Default Value

roundrobin

## Description

This environment variable defines the default load balance strategy in the `defaults` section. Possible value: `roundrobin`, `static-rr`, `source`, `leastconn`, etc.  See:[HAProxy:balance](https://cbonte.github.io/haproxy-dconv/1.6/configuration.html#4-balance)| 

## Example


```
-e BALANCE=source
```

Setting the above environment variable changes the balance strategy from default `roundrobin` to `source`


```
    defaults
 >    balance source 
      log global
      mode http
      option redispatch
      option httplog
      option dontlognull
      option forwardfor
      timeout connect 5000
      timeout client 50000
      timeout server 50000
  ```