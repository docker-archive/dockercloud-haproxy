import logging
import os

from haproxy.utils import save_to_file

logger = logging.getLogger("haproxy")


def get_extra_ssl_certs(extra_ssl_cert):
    extra_certs = []
    if extra_ssl_cert:
        for _cert_name in extra_ssl_cert.split(","):
            cert_name = _cert_name.strip()
            if cert_name:
                cert = os.getenv(cert_name)
                if cert:
                    extra_certs.append(cert)
    return extra_certs


def save_certs(pathname, certs):
    try:
        if not os.path.exists(pathname):
            os.makedirs(pathname)
    except Exception as e:
        logger.error(e)
    for index, cert in enumerate(certs):
        filename = "/".join([pathname.rstrip("/"), "cert%d.pem" % index])
        save_to_file(filename, cert.replace("\\n", '\n'))
