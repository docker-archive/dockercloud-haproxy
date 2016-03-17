FROM alpine:edge
MAINTAINER Feng Honglin <hfeng@tutum.co>

# Install tini, haproxy, pip and the dockercloud-haproxy python package:
RUN apk --no-cache add \
    tini \
    haproxy \
    py-pip \
  && apk --no-cache add --virtual deps git \
  && pip install --upgrade \
    pip \
  && apk del deps \
  # Clean up obsolete files:
  && rm -rf \
    # Clean up any temporary files:
    /tmp/* \
    # Clean up the pip cache:
    /root/.cache \
    # Remove any compiled python files (compile on demand):
    `find / -regex '.*\.py[co]'`

COPY reload.sh /reload.sh
COPY . haproxy-src/
RUN cd /haproxy-src/ && \
  pip install . \
  # Clean up obsolete files:
  && rm -rf \
    # Clean up any temporary files:
    /tmp/* \
    # Clean up the pip cache:
    /root/.cache \
    # Remove any compiled python files (compile on demand):
    `find / -regex '.*\.py[co]'`

ENV RSYSLOG_DESTINATION=127.0.0.1 \
    MODE=http \
    BALANCE=roundrobin \
    MAXCONN=4096 \
    OPTION="redispatch, httplog, dontlognull, forwardfor" \
    TIMEOUT="connect 5000, client 50000, server 50000" \
    STATS_PORT=1936 \
    STATS_AUTH="stats:stats" \
    SSL_BIND_OPTIONS=no-sslv3 \
    SSL_BIND_CIPHERS="ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:DHE-DSS-AES128-SHA:DES-CBC3-SHA" \
    HEALTH_CHECK="check"

EXPOSE 80 443 1936
ENTRYPOINT ["tini", "--"]
CMD ["dockercloud-haproxy"]
