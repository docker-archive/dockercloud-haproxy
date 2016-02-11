#!/bin/sh
kill -USR1 $(cat /tmp/dockercloud-haproxy.pid)
