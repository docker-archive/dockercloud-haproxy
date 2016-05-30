import os
import re


def parse_extra_bind_settings(extra_bind_settings):
    bind_dict = {}
    if extra_bind_settings:
        settings = re.split(r'(?<!\\),', extra_bind_settings)
        for setting in settings:
            term = setting.split(":", 1)
            if len(term) == 2:
                bind_dict[term[0].strip().replace("\,", ",")] = term[1].strip().replace("\,", ",")
    return bind_dict


def parse_extra_frontend_settings(envvars):
    settings_dict = {}
    if isinstance(envvars, os._Environ) or isinstance(envvars, dict):
        frontend_settings_pattern = re.compile(r"^EXTRA_FRONTEND_SETTINGS_(\d{1,5})$")
        for k, v in envvars.iteritems():
            match = frontend_settings_pattern.match(k)
            if match:
                port = match.group(1)
                settings = [x.strip().replace("\,", ",") for x in re.split(r'(?<!\\),', v.strip())]
                if port in settings_dict:
                    settings_dict[port].extend(settings)
                else:
                    settings_dict[port] = settings
    return settings_dict


# envvar
ADDITIONAL_SERVICES = os.getenv("ADDITIONAL_SERVICES")
API_AUTH = os.getenv("DOCKERCLOUD_AUTH")
BALANCE = os.getenv("BALANCE", "roundrobin")
CA_CERT_FILE = os.getenv("CA_CERT_FILE")
CERT_FOLDER = os.getenv("CERT_FOLDER")
DEBUG = os.getenv("DEBUG", False)
DEFAULT_CA_CERT = os.getenv("CA_CERT")
DEFAULT_SSL_CERT = os.getenv("DEFAULT_SSL_CERT") or os.getenv("SSL_CERT")
EXTRA_BIND_SETTINGS = parse_extra_bind_settings(os.getenv("EXTRA_BIND_SETTINGS"))
EXTRA_DEFAULT_SETTINGS = os.getenv("EXTRA_DEFAULT_SETTINGS")
EXTRA_FRONTEND_SETTINGS = parse_extra_frontend_settings(os.environ)
EXTRA_GLOBAL_SETTINGS = os.getenv("EXTRA_GLOBAL_SETTINGS")
EXTRA_SSL_CERT = os.getenv("EXTRA_SSL_CERTS")
EXTRA_ROUTE_SETTINGS=os.getenv("EXTRA_ROUTE_SETTINGS", "")
HAPROXY_CONTAINER_URI = os.getenv("DOCKERCLOUD_CONTAINER_API_URI")
HAPROXY_SERVICE_URI = os.getenv("DOCKERCLOUD_SERVICE_API_URI")
HEALTH_CHECK = os.getenv("HEALTH_CHECK", "check inter 2000 rise 2 fall 3")
HTTP_BASIC_AUTH = os.getenv("HTTP_BASIC_AUTH")
MAXCONN = os.getenv("MAXCONN", "4096")
MODE = os.getenv("MODE", "http")
MONITOR_PORT = os.getenv("MONITOR_PORT")
MONITOR_URI = os.getenv("MONITOR_URI")
OPTION = os.getenv("OPTION", "redispatch, httplog, dontlognull, forwardfor")
RSYSLOG_DESTINATION = os.getenv("RSYSLOG_DESTINATION", "127.0.0.1")
SKIP_FORWARDED_PROTO = os.getenv("SKIP_FORWARDED_PROTO")
SSL_BIND_CIPHERS = os.getenv("SSL_BIND_CIPHERS")
SSL_BIND_OPTIONS = os.getenv("SSL_BIND_OPTIONS")
STATS_AUTH = os.getenv("STATS_AUTH", "stats:stats")
STATS_PORT = os.getenv("STATS_PORT", "1936")
TIMEOUT = os.getenv("TIMEOUT", "connect 5000, client 50000, server 50000")

# global
LINK_MODE = ""

# const
CERT_DIR = "/certs/"
CACERT_DIR = "/cacerts/"
HAPROXY_CONFIG_FILE = "/haproxy.cfg"
HAPROXY_RUN_COMMAND = ['/usr/sbin/haproxy', '-f', HAPROXY_CONFIG_FILE, '-db', '-q']
API_RETRY = 10  # seconds
PID_FILE = "/tmp/dockercloud-haproxy.pid"

# regular expressions
SERVICE_NAME_MATCH = re.compile(r"(.+)_\d+$")
BACKEND_MATCH = re.compile(r"(?P<proto>tcp|udp):\/\/(?P<addr>[^:]*):(?P<port>.*)")
SERVICE_ALIAS_MATCH = re.compile(r"_PORT_\d{1,5}_(TCP|UDP)$")
DETAILED_SERVICE_ALIAS_MATCH = re.compile(r"_\d+_PORT_\d{1,5}_(TCP|UDP)$")
ENV_SERVICE_ALIAS_MATCH = re.compile(r"_ENV_")
ENV_DETAILED_SERVICE_ALIAS_MATCH = re.compile(r"_\d+_ENV")
