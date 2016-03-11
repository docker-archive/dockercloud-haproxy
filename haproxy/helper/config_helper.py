import re


def config_ssl_bind_options(ssl_bind_options):
    statements = []
    if ssl_bind_options:
        statements.append("ssl-default-bind-options %s" % ssl_bind_options)
    return statements


def config_ssl_bind_ciphers(ssl_bind_ciphers):
    statements = []
    if ssl_bind_ciphers:
        statements.append("ssl-default-bind-ciphers %s" % ssl_bind_ciphers)
    return statements


def config_extra_settings(extra_settings):
    statements = []
    if extra_settings:
        settings = re.split(r'(?<!\\),', extra_settings)
        for _setting in settings:
            setting = _setting.strip()
            if setting:
                statements.append(setting.replace("\,", ","))
    return statements


def config_option(option):
    statements = []
    if option:
        for _opt in option.split(","):
            opt = _opt.strip()
            if opt:
                statements.append("option %s" % opt.strip())
    return statements


def config_timeout(timeout):
    statements = []
    if timeout:
        for _t in timeout.split(","):
            t = _t.strip()
            if t:
                statements.append("timeout %s" % t)
    return statements
