import logging
import os
import re

logger = logging.getLogger("haproxy")


class RunningMode():
    LegacyMode, ComposeMode, SwarmMode, CloudMode = range(4)


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
        frontend_settings_file_pattern = re.compile(r"^EXTRA_FRONTEND_SETTINGS_FILE_(\d{1,5})$")
        for k, v in envvars.iteritems():
            settings = []
            match = frontend_settings_pattern.match(k)
            file_match = frontend_settings_file_pattern.match(k)
            if match:
                port = match.group(1)
                settings.extend([x.strip().replace("\,", ",") for x in re.split(r'(?<!\\),', v.strip())])
            elif file_match:
                port = file_match.group(1)
                try:
                    with open(v) as file:
                        for line in file:
                            settings.append(line.strip())
                except Exception as e:
                    logger.info("Error reading %s at '%s', error %s" % (k, v, e))

            if len(settings) > 0:
                if port in settings_dict:
                    settings_dict[port].extend(settings)
                else:
                    settings_dict[port] = settings
    return settings_dict


def parse_additional_backend_settings(envvars):
    settings_dict = {}
    if isinstance(envvars, os._Environ) or isinstance(envvars, dict):
        additional_backend_pattern = re.compile(r"^ADDITIONAL_BACKEND_(\w+)$")
        additional_backend_file_pattern = re.compile(r"^ADDITIONAL_BACKEND_FILE_(\w+)$")
        for k, v in envvars.iteritems():
            settings = []
            match = additional_backend_pattern.match(k)
            file_match = additional_backend_file_pattern.match(k)

            if file_match:
                server = file_match.group(1)
                try:
                    with open(v) as f:
                        for line in f:
                            settings.append(line.strip())
                except Exception as e:
                    logger.info("Error reading %s at '%s', error %s" % (k, v, e))
            elif match:
                server = match.group(1)
                settings.extend([x.strip().replace("\,", ",") for x in re.split(r'(?<!\\),', v.strip())])

            if len(settings) > 0:
                if server in settings_dict:
                    settings_dict[server].extend(settings)
                else:
                    settings_dict[server] = settings
    return settings_dict


# envvar
ADDITIONAL_BACKENDS = parse_additional_backend_settings(os.environ)
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
EXTRA_DEFAULT_SETTINGS_FILE = os.getenv("EXTRA_DEFAULT_SETTINGS_FILE")
EXTRA_FRONTEND_SETTINGS = parse_extra_frontend_settings(os.environ)
EXTRA_GLOBAL_SETTINGS = os.getenv("EXTRA_GLOBAL_SETTINGS")
EXTRA_GLOBAL_SETTINGS_FILE = os.getenv("EXTRA_GLOBAL_SETTINGS_FILE")
EXTRA_SSL_CERT = os.getenv("EXTRA_SSL_CERTS")
EXTRA_ROUTE_SETTINGS = os.getenv("EXTRA_ROUTE_SETTINGS", "")
FORCE_DEFAULT_BACKEND = os.getenv("FORCE_DEFAULT_BACKEND", "True")
HAPROXY_CONTAINER_URI = os.getenv("DOCKERCLOUD_CONTAINER_API_URI")
HAPROXY_SERVICE_URI = os.getenv("DOCKERCLOUD_SERVICE_API_URI")
HEALTH_CHECK = os.getenv("HEALTH_CHECK", "check inter 2000 rise 2 fall 3")
HTTP_BASIC_AUTH = os.getenv("HTTP_BASIC_AUTH")
HTTP_BASIC_AUTH_SECURE = os.getenv("HTTP_BASIC_AUTH_SECURE")
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
NBPROC = int(os.getenv("NBPROC", 1))
SWARM_MODE_POLLING_INTERVAL = int(os.getenv("SWARM_MODE_POLLING_INTERVAL", 5))
HAPROXY_USER = os.getenv("HAPROXY_USER", "haproxy")
HAPROXY_GROUP = os.getenv("HAPROXY_GROUP", "haproxy")
RELOAD_TIMEOUT = os.getenv("RELOAD_TIMEOUT", "0")

# global
RUNNING_MODE = None

# const
CERT_DIR = "/certs/"
CACERT_DIR = "/cacerts/"
HAPROXY_CONFIG_FILE = "/haproxy.cfg"
HAPROXY_RUN_COMMAND = ['/usr/sbin/haproxy', '-f', HAPROXY_CONFIG_FILE, '-db', '-q']
HAPROXY_CONFIG_CHECK_COMMAND = ['/usr/sbin/haproxy', '-c', '-f', HAPROXY_CONFIG_FILE]
API_RETRY = 10  # seconds
PID_FILE = "/tmp/dockercloud-haproxy.pid"
SERVICE_PORTS_ENVVAR_NAME = "SERVICE_PORTS"
LABEL_SWARM_MODE_DEACTIVATE = "com.docker.dockercloud.haproxy.deactivate"

# regular expressions
SERVICE_NAME_MATCH = re.compile(r"(.+)_\d+$")
BACKEND_MATCH = re.compile(r"(?P<proto>tcp|udp):\/\/(?P<addr>[^:]*):(?P<port>.*)")
SERVICE_ALIAS_MATCH = re.compile(r"_PORT_\d{1,5}_(TCP|UDP)$")
DETAILED_SERVICE_ALIAS_MATCH = re.compile(r"_\d+_PORT_\d{1,5}_(TCP|UDP)$")
ENV_SERVICE_ALIAS_MATCH = re.compile(r"_ENV_")
ENV_DETAILED_SERVICE_ALIAS_MATCH = re.compile(r"_\d+_ENV")
