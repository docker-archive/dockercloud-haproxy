#!/bin/bash

set -e

function rm_container {
    set +e
    docker rm -fv "$@" > /dev/null 2>&1
    set -e
}

function cleanup {
    echo "   Removing related containers"
    rm_container web-a web-b web-c web-d web-e web-f web-g lb
    echo "   Removing cert files"
    rm -f *.pem
}

function create_cert {
    openssl req -x509 -newkey rsa:2048 -keyout key$1.pem -out ca$1.pem -days 1080 -nodes -subj "/CN=$2/O=My Company Name LTD./C=US"
    cp key$1.pem cert$1.pem
    cat ca$1.pem >> cert$1.pem
}

function wait_for_startup {
    LOOP_LIMIT=10
    for (( i=0 ; ; i++ )); do
        if [ ${i} -eq ${LOOP_LIMIT} ]; then
            break
        fi
        sleep 1
        curl -kL "$@" > /dev/null 2>&1 && break
    done
}

echo "=> Testing running environment"
docker version
which curl > /dev/null
which awk > /dev/null
echo

echo "=> Clean up"
cleanup
echo

echo "=> Building haproxy image"
docker build -t haproxy .
echo

echo "=> Creating certificates"
create_cert 0 ${DOCKER_HOST_IP}
create_cert 1 web-a.org
create_cert 2 web-b.org
echo


echo "=> Docker Host Ip address"
DOCKER_HOST_IP=${DOCKER_HOST_IP:-$1}
if docker-machine ip $1; then
    DOCKER_HOST_IP=`docker-machine ip $1`
fi
DOCKER_HOST_IP=${DOCKER_HOST_IP:-"127.0.0.1"}
echo

echo "=> Running Tests"

echo "=> Test if haproxy is running properly"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME="web-a" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 8000:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:8000
curl -ssfL -I http://${DOCKER_HOST_IP}:8000 > /dev/null
echo

echo "=> Test Default_SSL_CERT(client verifies server)"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME="web-a" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -e DEFAULT_SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" -p 443:443 haproxy
wait_for_startup https://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF "SSL certificate problem" > /dev/null
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test SSL verification(server verifies client)"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME="web-a" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -e DEFAULT_SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" -e CA_CERT="$(awk 1 ORS='\\n' ca0.pem)" -p 443:443 haproxy
wait_for_startup https://${DOCKER_HOST_IP}
echo "   Sending request without certificate"
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 > /dev/null | grep 'handshake' > /dev/null
echo "   Sending request with a wrong certificate"
curl -sSfL --cacert ca1.pem --cert cert1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 > /dev/null | grep 'alert unknown ca' > /dev/null
echo "   Sending request with the correct certificate"
curl -sSfL --cacert ca1.pem --cert cert0.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test mounting certs from volume"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME="web-a" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -e CERT_FOLDER="/certs/" -v $(pwd)/cert1.pem:/certs/cert1.pem -p 443:443 haproxy
wait_for_startup https://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF "SSL certificate problem" > /dev/null
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test mounting ca-cert from volume"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME="web-a" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -e CERT_FOLDER="/certs/" -v $(pwd)/cert1.pem:/certs/cert1.pem -e CA_CERT_FILE="/cacert/ca0.pem"  -v $(pwd)/ca0.pem:/cacert/ca0.pem -p 443:443 haproxy
wait_for_startup https://${DOCKER_HOST_IP}
echo "   Sending request without certificate"
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 > /dev/null | grep 'handshake' > /dev/null
echo "   Sending request with a wrong certificate"
curl -sSfL --cacert ca1.pem --cert cert1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 > /dev/null | grep 'alert unknown ca' > /dev/null
echo "   Sending request with the correct certificate"c
curl -sSfL --cacert ca1.pem --cert cert0.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test virtual host"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST=web-a.org dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST=web-b.org dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-b.org:80:${DOCKER_HOST_IP} web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
echo

echo "=> Test multiple ssl certificates"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME="web-a" -e VIRTUAL_HOST="https://web-a.org" -e SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME="web-b" -e VIRTUAL_HOST="https://web-b.org" -e SSL_CERT="$(awk 1 ORS='\\n' cert2.pem)" dockercloud/hello-world
docker run -d --name lb  --link web-a:web-a --link web-b:web-b -p 443:443 haproxy
wait_for_startup https://${DOCKER_HOST_IP}
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --cacert ca2.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org  2>&1 2>&1 | grep -iF "SSL certificate problem: self signed certificate" > /dev/null
curl -sSfL --cacert ca2.pem --resolve web-b.org:443:${DOCKER_HOST_IP} https://web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --cacert ca1.pem --resolve web-b.org:443:${DOCKER_HOST_IP} https://web-b.org 2>&1 2>&1 | grep -iF "SSL certificate problem: self signed certificate" > /dev/null
echo

echo "=> Test multiple virtual host entries"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST='web-a.org, web-a.com' dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST='web-b.org, web-b.com' dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} http://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.com:80:${DOCKER_HOST_IP} http://web-a.com 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-b.org:80:${DOCKER_HOST_IP} http://web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve web-b.com:80:${DOCKER_HOST_IP} http://web-b.com 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
echo

echo "=> Test virtual host with duplicated entries"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST='web-a.org, web-a.org:80' dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST='web-b.org:8080, web-b.org:8080' dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b -p 80:80 -p 8080:8080 haproxy
wait_for_startup http://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} web-b.org:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} web-b.org:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
echo

echo "=> Test virtual host with ports"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST='web-a.org' dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST='web-b.org:8080' dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b -p 80:80 -p 8080:8080 haproxy
wait_for_startup http://${DOCKER_HOST_IP}
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} web-b.org:8080 ${DOCKER_HOST_IP}:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} -H 'Host:web-b.org' web-b.org:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
echo

echo "=> Test virtual host with scheme and ports"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="https://web-a.org:442" -e SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST="http://web-b.org:8080" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b -p 442:442 -p 8080:8080 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:8080
curl -sSfL --cacert ca1.pem --resolve web-a.org:442:${DOCKER_HOST_IP} https://web-a.org:442 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --cacert ca1.pem --resolve web-a.org:442:${DOCKER_HOST_IP} https://web-a.org:442 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} web-b.org:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve web-b.org:8080:${DOCKER_HOST_IP} -H 'Host:web-b.org' web-b.org:8080 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
echo

echo "=> Test virtual host with a value of *"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="*" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} -H 'Host:web-a.org' web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test virtual host with a value of */"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="*/" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} -H 'Host:web-a.org' web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org/abc 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual host with a value of */*"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="*/*" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} -H 'Host:web-a.org' web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80/abc 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo


echo "=> Test virtual host with wildcard in host and on a non-default port"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="http://web-*.org:8080" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 8080:8080 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:8080
curl -sSfL --resolve web-a.org:8080:${DOCKER_HOST_IP} web-a.org:8080 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:8080:${DOCKER_HOST_IP} -H 'Host:web-a.org' web-a.org:8080 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
echo

echo "=> Test virtual host that starts with wildcard"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="*.web-a.org" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve abc.web-a.org:80:${DOCKER_HOST_IP} abc.web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve abc.web-a.org:80:${DOCKER_HOST_IP} abc.web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.com:80:${DOCKER_HOST_IP} www.web-a.com 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual host that ends with wildcard"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="web-a.*" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.org:80:${DOCKER_HOST_IP} web-a.org:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.com:80:${DOCKER_HOST_IP} web-a.com 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve web-a.com:80:${DOCKER_HOST_IP} web-a.com:80 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual path"
rm_container web-a web-b web-c web-d web-e web-f web-g lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="*/pa/, */pa, */pa/*, */*/pa/*" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME=web-b -e VIRTUAL_HOST="*/pb" dockercloud/hello-world
docker run -d --name web-c -e HOSTNAME=web-c -e VIRTUAL_HOST="*/pc/" dockercloud/hello-world
docker run -d --name web-d -e HOSTNAME=web-d -e VIRTUAL_HOST="*/pd/*" dockercloud/hello-world
docker run -d --name web-e -e HOSTNAME=web-e -e VIRTUAL_HOST="*/*/pe/*" dockercloud/hello-world
docker run -d --name web-f -e HOSTNAME=web-f -e VIRTUAL_HOST="*/p*f/" dockercloud/hello-world
docker run -d --name web-g -e HOSTNAME=web-g -e VIRTUAL_HOST="*/*.js" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a --link web-b:web-b --link web-c:web-c --link web-d:web-d --link web-e:web-e --link web-f:web-f --link web-g:web-g -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80

curl -sSfL ${DOCKER_HOST_IP}/pa 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pa/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pa/abc 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/abc/pa/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/abc/pa/123 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pa?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-a' > /dev/null

curl -sSfL ${DOCKER_HOST_IP}/pb | grep -iF 'My hostname is web-b' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/pb/ | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/pb/abc | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pb/ | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pb/123 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pb?u=user&p=pass" | grep -iF 'My hostname is web-b' > /dev/null

curl -sSL ${DOCKER_HOST_IP}/pc 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pc/ 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/pc/abc 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pc/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pc/123 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pc/?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-c' > /dev/null

curl -sSL ${DOCKER_HOST_IP}/pd 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pd/ 2>&1 | grep -iF 'My hostname is web-d' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pd/abc 2>&1 | grep -iF 'My hostname is web-d' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pd/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc/pd/123 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pd/?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-d' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pd/abc?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-d' > /dev/null

curl -sSL ${DOCKER_HOST_IP}/pe 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/pe/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/pe/abc 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/abc/pe/ 2>&1 | grep -iF 'My hostname is web-e' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/abc/pe/123 2>&1 | grep -iF 'My hostname is web-e' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/abc/pe/?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-e' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/abc/pe/123?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-e' > /dev/null

curl -sSL ${DOCKER_HOST_IP}/pf 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/pf/ 2>&1 | grep -iF 'My hostname is web-f' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/p3f 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/p3f/ 2>&1 | grep -iF 'My hostname is web-f' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/pf/?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-f' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/p3f/?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-f' > /dev/null

curl -sSfL ${DOCKER_HOST_IP}/abc.js 2>&1 | grep -iF 'My hostname is web-g' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/path/123.js 2>&1 | grep -iF 'My hostname is web-g' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/abc.js?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-g' > /dev/null
curl -sSfL "${DOCKER_HOST_IP}/path/123.js?u=user&p=pass" 2>&1 | grep -iF 'My hostname is web-g' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/abc.jpg 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSL ${DOCKER_HOST_IP}/path/abc.jpg 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual host combined with virtual path"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="http://www.web-a.org/p3/" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org/p3/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org:80/p3/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/p3/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org/p3 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web.org:80:${DOCKER_HOST_IP} www.web.org:80/p3/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual host combined with virtual path including wildcard"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="http://www.web-*.org/p*/" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org/p1/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org:80/p/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/p3/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web.org:80:${DOCKER_HOST_IP} www.web.org 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web-a.org:80:${DOCKER_HOST_IP} www.web-a.org/p3 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test virtual host combined with virtual path including wildcard on a none default port"
rm_container web-a lb
docker run -d --name web-a -e HOSTNAME=web-a -e VIRTUAL_HOST="http://www.web-*.org:8080/p*/" dockercloud/hello-world
docker run -d --name lb --link web-a:web-a -p 8080:8080 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:8080
curl -sSfL --resolve www.web-a.org:8080:${DOCKER_HOST_IP} www.web-a.org:8080/p1/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:8080:${DOCKER_HOST_IP} www.web-a.org:8080/p/ 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve www.web-a.org:8080:${DOCKER_HOST_IP} www.web-a.org:8080/p/ 2>&1 -H HOST:www.web-a.org| grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}:8080/p3/ 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web.org:8080:${DOCKER_HOST_IP} www.web.org:8080 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
curl -sSfL --resolve www.web-a.org:8080:${DOCKER_HOST_IP} www.web-a.org:8080/p3 2>&1 | grep -iF '503 Service Unavailable' > /dev/null
echo

echo "=> Test multiple frontends"
rm_container web-a web-b web-c lb
docker run -d --name web-a -e HOSTNAME="web-a" -e VIRTUAL_HOST="https://web-a.org:444, weba2.org:8008" -e SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME="web-b" -e VIRTUAL_HOST="https://web-b.org, http://webb2.org" -e SSL_CERT="$(awk 1 ORS='\\n' cert2.pem)" dockercloud/hello-world
docker run -d --name web-c -e HOSTNAME="web-c" -e VIRTUAL_HOST="webc.org, http://webc1.org:8009, webc2.org/path/, */*.do/, *:8011/*.php/" dockercloud/hello-world
docker run -d --name lb  --link web-a:web-a --link web-b:web-b --link web-c:web-c -p 443:443 -p 444:444 -p 8008:8008 -p 8009:8009 -p 80:80 -p 8011:8011 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --cacert ca1.pem --resolve web-a.org:444:${DOCKER_HOST_IP} https://web-a.org:444 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --resolve weba2.org:8008:${DOCKER_HOST_IP} weba2.org:8008 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --cacert ca2.pem --resolve web-b.org:443:${DOCKER_HOST_IP} https://web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve webb2.org:80:${DOCKER_HOST_IP} webb2.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --resolve webc.org:80:${DOCKER_HOST_IP} webc.org 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL --resolve webc1.org:8009:${DOCKER_HOST_IP} webc1.org:8009 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL --resolve webc2.org:80:${DOCKER_HOST_IP} webc2.org/path/ 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL --resolve webc3.org:80:${DOCKER_HOST_IP} webc3.org/abc.do/ 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}/abc.do/ 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL --resolve webc3.org:8011:${DOCKER_HOST_IP} webc3.org:8011/abc.php/ webc2.org/path 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
curl -sSfL ${DOCKER_HOST_IP}:8011/abc.php/ 2>&1 | grep -iF 'My hostname is web-c' > /dev/null
echo

echo "=> Test force_ssl with virtual host"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME="web-a" -e VIRTUAL_HOST="https://web-a.org, web-a.org" -e SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME="web-b" -e VIRTUAL_HOST="https://web-b.org, web-b.org" -e SSL_CERT="$(awk 1 ORS='\\n' cert2.pem)" -e FORCE_SSL=true dockercloud/hello-world
docker run -d --name lb  --link web-a:web-a --link web-b:web-b -p 443:443 -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --cacert ca2.pem --resolve web-b.org:443:${DOCKER_HOST_IP} https://web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} --resolve web-a.org:80:${DOCKER_HOST_IP} http://web-a.org 2>&1 | grep -iF 'My hostname is web-a' > /dev/null
curl -sSfL --cacert ca2.pem --resolve web-b.org:443:${DOCKER_HOST_IP} --resolve web-b.org:80:${DOCKER_HOST_IP} http://web-b.org 2>&1 | grep -iF 'My hostname is web-b' > /dev/null
curl -sSIL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} --resolve web-a.org:80:${DOCKER_HOST_IP} http://web-a.org 2>&1 | grep -iF "http/1.1" | grep -v "301" > /dev/null
curl -sSIL --cacert ca2.pem --resolve web-b.org:443:${DOCKER_HOST_IP} --resolve web-b.org:80:${DOCKER_HOST_IP} http://web-b.org 2>&1 | grep -iF '301 Moved Permanently' > /dev/null
echo

echo "=> Testing force_ssl without virtual host"
rm_container web-a web-b lb
docker run -d --name web-a -e HOSTNAME="web-ab" -e SSL_CERT="$(awk 1 ORS='\\n' cert1.pem)" dockercloud/hello-world
docker run -d --name web-b -e HOSTNAME="web-ab" -e FORCE_SSL=true dockercloud/hello-world
docker run -d --name lb  --link web-a:web-a --link web-b:web-b -p 443:443 -p 80:80 haproxy
wait_for_startup http://${DOCKER_HOST_IP}:80
curl -sSfL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org 2>&1 | grep -iF 'My hostname is web-ab' > /dev/null
curl -sSIL --cacert ca1.pem --resolve web-a.org:443:${DOCKER_HOST_IP} https://web-a.org > /dev/null
echo

echo "=> Clean up"
cleanup
echo "=> Done!"
