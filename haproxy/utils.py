import logging
import time

import dockercloud

import config

logger = logging.getLogger("haproxy")


def fetch_remote_obj(uri):
    if not uri:
        return None

    while True:
        try:
            obj = dockercloud.Utils.fetch_by_resource_uri(uri)
            return obj
        except Exception as e:
            logger.error(e)
            time.sleep(config.API_RETRY)


def get_uuid_from_resource_uri(uri):
    terms = uri.strip("/").split("/")
    if len(terms) < 2:
        return ""
    return terms[-1]


def save_to_file(name, content):
    try:
        with open(name, 'w') as f:
            f.write(content)
            return True
    except Exception as e:
        logger.error("Cannot write to file(%s): %s" % (name, e))
        return False


def prettify(cfg, indent="  "):
    text = ""
    for section, contents in cfg.items():
        text += "%s\n" % section
        for content in contents:
            text += "%s%s\n" % (indent, content)
    return text.strip()


def get_service_attribute(details, attr_name, service_alias=None):
    # when there is no virtual host is set, service is None
    if service_alias:
        try:
            return details[service_alias][attr_name]
        except:
            return None
    else:
        # Randomly pick a None value from the linked service
        for _service_alias in details.iterkeys():
            try:
                if details[_service_alias][attr_name]:
                    return details[_service_alias][attr_name]
            except:
                continue
        return None


def get_bind_string(enable_ssl, port_num, ssl_bind_string, bind_settings):
    bind_string = " ".join([port_num, bind_settings.get(port_num, "")])
    if enable_ssl:
        bind_string = " ".join([bind_string.strip(), ssl_bind_string])
    return bind_string.strip()
