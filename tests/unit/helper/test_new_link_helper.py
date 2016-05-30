import unittest

from haproxy.helper.new_link_helper import _calc_links, _get_linked_compose_services, _get_container_envvars, \
    _get_container_endpoints, get_container_links_str, get_service_links_str, get_additional_links

container1 = {u'ExecIDs': None,
              u'State': {u'Status': u'running', u'Pid': 28121, u'OOMKilled': False, u'Dead': False, u'Paused': False,
                         u'Running': True, u'FinishedAt': u'0001-01-01T00:00:00Z', u'Restarting': False, u'Error': u'',
                         u'StartedAt': u'2016-03-09T14:32:04.685183778Z', u'ExitCode': 0},
              u'Config': {u'Tty': False, u'Cmd': [u'dockercloud-haproxy'],
                          u'Volumes': {u'/Users/hfeng/.docker/machine/machines/default': {}}, u'Domainname': u'',
                          u'WorkingDir': u'', u'Image': u'haproxy', u'Hostname': u'b02cb80c8a8c', u'StdinOnce': False,
                          u'Labels': {u'com.docker.compose.service': u'lb',
                                      u'com.docker.compose.config-hash': u'd885398ce9e71438ec5d8a8ee349d189b2d056b2122e74186e813b433577c353',
                                      u'com.docker.compose.project': u'tmp', u'com.docker.compose.version': u'1.6.0',
                                      u'com.docker.compose.oneoff': u'False',
                                      u'com.docker.compose.container-number': u'1'}, u'AttachStdin': False,
                          u'User': u'', u'Env': [u'DOCKER_HOST=tcp://192.168.99.100:2376', u'DOCKER_TLS_VERIFY=1',
                                                 u'DOCKER_CERT_PATH=/Users/hfeng/.docker/machine/machines/default',
                                                 u'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                                                 u'RSYSLOG_DESTINATION=127.0.0.1', u'MODE=http', u'BALANCE=roundrobin',
                                                 u'MAXCONN=4096',
                                                 u'OPTION=redispatch, httplog, dontlognull, forwardfor',
                                                 u'TIMEOUT=connect 5000, client 50000, server 50000',
                                                 u'STATS_PORT=1936', u'STATS_AUTH=stats:stats',
                                                 u'SSL_BIND_OPTIONS=no-sslv3',
                                                 u'SSL_BIND_CIPHERS=ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:DHE-DSS-AES128-SHA:DES-CBC3-SHA',
                                                 u'HEALTH_CHECK=check'],
                          u'ExposedPorts': {u'1936/tcp': {}, u'443/tcp': {}, u'80/tcp': {}}, u'OnBuild': None,
                          u'AttachStderr': False, u'Entrypoint': None, u'AttachStdout': False, u'OpenStdin': False},
              u'ResolvConfPath': u'/mnt/sda1/var/lib/docker/containers/b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c/resolv.conf',
              u'HostsPath': u'/mnt/sda1/var/lib/docker/containers/b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c/hosts',
              u'Args': [], u'Driver': u'aufs', u'Path': u'dockercloud-haproxy',
              u'HostnamePath': u'/mnt/sda1/var/lib/docker/containers/b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c/hostname',
              u'RestartCount': 0, u'Name': u'/tmp_lb_1', u'Created': u'2016-03-09T14:32:04.459781679Z',
              u'GraphDriver': {u'Data': None, u'Name': u'aufs'}, u'Mounts': [
        {u'RW': True, u'Source': u'/Users/hfeng/.docker/machine/machines/default',
         u'Destination': u'/Users/hfeng/.docker/machine/machines/default', u'Mode': u'rw',
         u'Propagation': u'rprivate'}], u'ProcessLabel': u'', u'NetworkSettings': {u'Bridge': u'', u'Networks': {
        u'tmp_default': {u'NetworkID': u'0b29dd1b81a581926f309d4c1e3abd369732de8337912d31b71da5f840878932',
                         u'MacAddress': u'02:42:ac:13:00:04', u'GlobalIPv6PrefixLen': 0,
                         u'Links': [u'tmp_hello_1:hello', u'tmp_hello_1:hello_1', u'tmp_hello_1:tmp_hello_1',
                                    u'tmp_world_1:tmp_world_1', u'tmp_world_1:world', u'tmp_world_1:world_1'],
                         u'GlobalIPv6Address': u'', u'IPv6Gateway': u'', u'IPAMConfig': None,
                         u'EndpointID': u'1ff219fbde6eade176066f250010e4de41a1e0403083b5413de7c9de3582d6e2',
                         u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.4', u'Gateway': u'172.19.0.1',
                         u'Aliases': [u'lb', u'b02cb80c8a']}}, u'SecondaryIPv6Addresses': None,
                                                                                   u'LinkLocalIPv6Address': u'',
                                                                                   u'HairpinMode': False,
                                                                                   u'IPv6Gateway': u'',
                                                                                   u'SecondaryIPAddresses': None,
                                                                                   u'SandboxID': u'2479d32873d22bd9f2c074a2108116d0340fff45c37ede4f91c74bed8127e842',
                                                                                   u'MacAddress': u'',
                                                                                   u'GlobalIPv6Address': u'',
                                                                                   u'Gateway': u'',
                                                                                   u'LinkLocalIPv6PrefixLen': 0,
                                                                                   u'EndpointID': u'',
                                                                                   u'SandboxKey': u'/var/run/docker/netns/2479d32873d2',
                                                                                   u'GlobalIPv6PrefixLen': 0,
                                                                                   u'IPPrefixLen': 0, u'IPAddress': u'',
                                                                                   u'Ports': {u'1936/tcp': None,
                                                                                              u'443/tcp': None,
                                                                                              u'80/tcp': [
                                                                                                  {u'HostPort': u'80',
                                                                                                   u'HostIp': u'0.0.0.0'}]}},
              u'AppArmorProfile': u'',
              u'Image': u'sha256:7682ea99c4ce6811154dd2b2fad3a6b374adc08e9b495068e903686e77882dfd',
              u'LogPath': u'/mnt/sda1/var/lib/docker/containers/b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c/b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c-json.log',
              u'HostConfig': {u'CpuPeriod': 0, u'MemorySwappiness': -1, u'ContainerIDFile': u'', u'MemorySwap': 0,
                              u'BlkioDeviceReadIOps': None, u'CpuQuota': 0, u'Dns': None, u'ExtraHosts': None,
                              u'PidsLimit': 0, u'DnsSearch': None, u'Privileged': False, u'Ulimits': None,
                              u'CpusetCpus': u'', u'CgroupParent': u'', u'BlkioWeight': 0,
                              u'RestartPolicy': {u'MaximumRetryCount': 0, u'Name': u''}, u'OomScoreAdj': 0,
                              u'BlkioDeviceReadBps': None, u'VolumeDriver': u'', u'ReadonlyRootfs': False,
                              u'CpuShares': 0, u'PublishAllPorts': False, u'MemoryReservation': 0,
                              u'BlkioWeightDevice': None, u'ConsoleSize': [0, 0], u'NetworkMode': u'tmp_default',
                              u'BlkioDeviceWriteBps': None, u'Isolation': u'', u'GroupAdd': None, u'Devices': None,
                              u'BlkioDeviceWriteIOps': None, u'Binds': [
                      u'/Users/hfeng/.docker/machine/machines/default:/Users/hfeng/.docker/machine/machines/default:rw'],
                              u'CpusetMems': u'', u'KernelMemory': 0, u'UTSMode': u'', u'PidMode': u'',
                              u'VolumesFrom': [], u'CapDrop': None, u'DnsOptions': None, u'ShmSize': 67108864,
                              u'Links': None, u'IpcMode': u'',
                              u'PortBindings': {u'80/tcp': [{u'HostPort': u'80', u'HostIp': u''}]},
                              u'SecurityOpt': None, u'CapAdd': None, u'Memory': 0, u'OomKillDisable': False,
                              u'LogConfig': {u'Config': {}, u'Type': u'json-file'}},
              u'Id': u'b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c', u'MountLabel': u''}
container2 = {u'ExecIDs': None,
              u'State': {u'Status': u'running', u'Pid': 28095, u'OOMKilled': False, u'Dead': False, u'Paused': False,
                         u'Running': True, u'FinishedAt': u'0001-01-01T00:00:00Z', u'Restarting': False, u'Error': u'',
                         u'StartedAt': u'2016-03-09T14:32:04.43566653Z', u'ExitCode': 0}, u'Config': {u'Tty': False,
                                                                                                      u'Cmd': [
                                                                                                          u'/bin/sh',
                                                                                                          u'-c',
                                                                                                          u'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"'],
                                                                                                      u'Volumes': None,
                                                                                                      u'Domainname': u'',
                                                                                                      u'WorkingDir': u'',
                                                                                                      u'Image': u'dockercloud/hello-world',
                                                                                                      u'Hostname': u'a90c1c19288d',
                                                                                                      u'StdinOnce': False,
                                                                                                      u'Labels': {
                                                                                                          u'com.docker.compose.service': u'hello',
                                                                                                          u'com.docker.compose.config-hash': u'ea29a97e3dceca1e7926d7d8d9e6e6709bb169d572f244be149dd187775101c5',
                                                                                                          u'com.docker.compose.project': u'tmp',
                                                                                                          u'com.docker.compose.version': u'1.6.0',
                                                                                                          u'com.docker.compose.oneoff': u'False',
                                                                                                          u'com.docker.compose.container-number': u'1'},
                                                                                                      u'AttachStdin': False,
                                                                                                      u'User': u'',
                                                                                                      u'Env': [
                                                                                                          u'VIRTUAL_HOST=a.com',
                                                                                                          u'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'],
                                                                                                      u'ExposedPorts': {
                                                                                                          u'80/tcp': {}},
                                                                                                      u'OnBuild': None,
                                                                                                      u'AttachStderr': False,
                                                                                                      u'Entrypoint': None,
                                                                                                      u'AttachStdout': False,
                                                                                                      u'OpenStdin': False},
              u'ResolvConfPath': u'/mnt/sda1/var/lib/docker/containers/a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b/resolv.conf',
              u'HostsPath': u'/mnt/sda1/var/lib/docker/containers/a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b/hosts',
              u'Args': [u'-c',
                        u'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"'],
              u'Driver': u'aufs', u'Path': u'/bin/sh',
              u'HostnamePath': u'/mnt/sda1/var/lib/docker/containers/a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b/hostname',
              u'RestartCount': 0, u'Name': u'/tmp_hello_1', u'Created': u'2016-03-09T14:32:04.258871274Z',
              u'GraphDriver': {u'Data': None, u'Name': u'aufs'}, u'Mounts': [], u'ProcessLabel': u'',
              u'NetworkSettings': {u'Bridge': u'', u'Networks': {
                  u'tmp_default': {u'NetworkID': u'0b29dd1b81a581926f309d4c1e3abd369732de8337912d31b71da5f840878932',
                                   u'MacAddress': u'02:42:ac:13:00:03', u'GlobalIPv6PrefixLen': 0, u'Links': None,
                                   u'GlobalIPv6Address': u'', u'IPv6Gateway': u'', u'IPAMConfig': None,
                                   u'EndpointID': u'c0a2a68da8d03fc8907c965c6cf9641100fe8d22eca7ae61b4a4a1dcae7e8b09',
                                   u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.3', u'Gateway': u'172.19.0.1',
                                   u'Aliases': [u'hello', u'a90c1c1928']}}, u'SecondaryIPv6Addresses': None,
                                   u'LinkLocalIPv6Address': u'', u'HairpinMode': False, u'IPv6Gateway': u'',
                                   u'SecondaryIPAddresses': None,
                                   u'SandboxID': u'c45503e43dbedb4b7387c34c8711aa910e2adae8480b340556fbb9f78cfedc90',
                                   u'MacAddress': u'', u'GlobalIPv6Address': u'', u'Gateway': u'',
                                   u'LinkLocalIPv6PrefixLen': 0, u'EndpointID': u'',
                                   u'SandboxKey': u'/var/run/docker/netns/c45503e43dbe', u'GlobalIPv6PrefixLen': 0,
                                   u'IPPrefixLen': 0, u'IPAddress': u'', u'Ports': {u'80/tcp': None}},
              u'AppArmorProfile': u'',
              u'Image': u'sha256:b05299680b1d33adab9987c5a49b8e374fa0c48c6aa22191b3b71d8fcdce97d0',
              u'LogPath': u'/mnt/sda1/var/lib/docker/containers/a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b/a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b-json.log',
              u'HostConfig': {u'CpuPeriod': 0, u'MemorySwappiness': -1, u'ContainerIDFile': u'', u'MemorySwap': 0,
                              u'BlkioDeviceReadIOps': None, u'CpuQuota': 0, u'Dns': None, u'ExtraHosts': None,
                              u'PidsLimit': 0, u'DnsSearch': None, u'Privileged': False, u'Ulimits': None,
                              u'CpusetCpus': u'', u'CgroupParent': u'', u'BlkioWeight': 0,
                              u'RestartPolicy': {u'MaximumRetryCount': 0, u'Name': u''}, u'OomScoreAdj': 0,
                              u'BlkioDeviceReadBps': None, u'VolumeDriver': u'', u'ReadonlyRootfs': False,
                              u'CpuShares': 0, u'PublishAllPorts': False, u'MemoryReservation': 0,
                              u'BlkioWeightDevice': None, u'ConsoleSize': [0, 0], u'NetworkMode': u'tmp_default',
                              u'BlkioDeviceWriteBps': None, u'Isolation': u'', u'GroupAdd': None, u'Devices': None,
                              u'BlkioDeviceWriteIOps': None, u'Binds': [], u'CpusetMems': u'', u'KernelMemory': 0,
                              u'UTSMode': u'', u'PidMode': u'', u'VolumesFrom': [], u'CapDrop': None,
                              u'DnsOptions': None, u'ShmSize': 67108864, u'Links': None, u'IpcMode': u'',
                              u'PortBindings': {}, u'SecurityOpt': None, u'CapAdd': None, u'Memory': 0,
                              u'OomKillDisable': False, u'LogConfig': {u'Config': {}, u'Type': u'json-file'}},
              u'Id': u'a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b', u'MountLabel': u''}
container3 = {u'ExecIDs': None,
              u'State': {u'Status': u'running', u'Pid': 28077, u'OOMKilled': False, u'Dead': False, u'Paused': False,
                         u'Running': True, u'FinishedAt': u'0001-01-01T00:00:00Z', u'Restarting': False, u'Error': u'',
                         u'StartedAt': u'2016-03-09T14:32:04.244529108Z', u'ExitCode': 0}, u'Config': {u'Tty': False,
                                                                                                       u'Cmd': [
                                                                                                           u'/bin/sh',
                                                                                                           u'-c',
                                                                                                           u'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"'],
                                                                                                       u'Volumes': None,
                                                                                                       u'Domainname': u'',
                                                                                                       u'WorkingDir': u'',
                                                                                                       u'Image': u'dockercloud/hello-world',
                                                                                                       u'Hostname': u'8c64c58e2887',
                                                                                                       u'StdinOnce': False,
                                                                                                       u'Labels': {
                                                                                                           u'com.docker.compose.service': u'world',
                                                                                                           u'com.docker.compose.config-hash': u'd94bc3989630b0089b0b1e9fd29f0808618f078e84e61b687c6415ed6e424d43',
                                                                                                           u'com.docker.compose.project': u'tmp',
                                                                                                           u'com.docker.compose.version': u'1.6.0',
                                                                                                           u'com.docker.compose.oneoff': u'False',
                                                                                                           u'com.docker.compose.container-number': u'1'},
                                                                                                       u'AttachStdin': False,
                                                                                                       u'User': u'',
                                                                                                       u'Env': [
                                                                                                           u'VIRTUAL_HOST=ab.com',
                                                                                                           u'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'],
                                                                                                       u'ExposedPorts': {
                                                                                                           u'80/tcp': {}},
                                                                                                       u'OnBuild': None,
                                                                                                       u'AttachStderr': False,
                                                                                                       u'Entrypoint': None,
                                                                                                       u'AttachStdout': False,
                                                                                                       u'OpenStdin': False},
              u'ResolvConfPath': u'/mnt/sda1/var/lib/docker/containers/8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550/resolv.conf',
              u'HostsPath': u'/mnt/sda1/var/lib/docker/containers/8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550/hosts',
              u'Args': [u'-c',
                        u'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"'],
              u'Driver': u'aufs', u'Path': u'/bin/sh',
              u'HostnamePath': u'/mnt/sda1/var/lib/docker/containers/8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550/hostname',
              u'RestartCount': 0, u'Name': u'/tmp_world_1', u'Created': u'2016-03-09T14:32:04.074966658Z',
              u'GraphDriver': {u'Data': None, u'Name': u'aufs'}, u'Mounts': [], u'ProcessLabel': u'',
              u'NetworkSettings': {u'Bridge': u'', u'Networks': {
                  u'tmp_default': {u'NetworkID': u'0b29dd1b81a581926f309d4c1e3abd369732de8337912d31b71da5f840878932',
                                   u'MacAddress': u'02:42:ac:13:00:02', u'GlobalIPv6PrefixLen': 0, u'Links': None,
                                   u'GlobalIPv6Address': u'', u'IPv6Gateway': u'', u'IPAMConfig': None,
                                   u'EndpointID': u'8cac874933ef933f82a182474d849d36b363cde076b75960bc36abac49b4a08e',
                                   u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.2', u'Gateway': u'172.19.0.1',
                                   u'Aliases': [u'world', u'8c64c58e28']}}, u'SecondaryIPv6Addresses': None,
                                   u'LinkLocalIPv6Address': u'', u'HairpinMode': False, u'IPv6Gateway': u'',
                                   u'SecondaryIPAddresses': None,
                                   u'SandboxID': u'17ecb5b2206c150468ce42b04bf3cbd7248aa13eeb085f1cf3d44cdcf6692ee5',
                                   u'MacAddress': u'', u'GlobalIPv6Address': u'', u'Gateway': u'',
                                   u'LinkLocalIPv6PrefixLen': 0, u'EndpointID': u'',
                                   u'SandboxKey': u'/var/run/docker/netns/17ecb5b2206c', u'GlobalIPv6PrefixLen': 0,
                                   u'IPPrefixLen': 0, u'IPAddress': u'', u'Ports': {u'80/tcp': None}},
              u'AppArmorProfile': u'',
              u'Image': u'sha256:b05299680b1d33adab9987c5a49b8e374fa0c48c6aa22191b3b71d8fcdce97d0',
              u'LogPath': u'/mnt/sda1/var/lib/docker/containers/8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550/8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550-json.log',
              u'HostConfig': {u'CpuPeriod': 0, u'MemorySwappiness': -1, u'ContainerIDFile': u'', u'MemorySwap': 0,
                              u'BlkioDeviceReadIOps': None, u'CpuQuota': 0, u'Dns': None, u'ExtraHosts': None,
                              u'PidsLimit': 0, u'DnsSearch': None, u'Privileged': False, u'Ulimits': None,
                              u'CpusetCpus': u'', u'CgroupParent': u'', u'BlkioWeight': 0,
                              u'RestartPolicy': {u'MaximumRetryCount': 0, u'Name': u''}, u'OomScoreAdj': 0,
                              u'BlkioDeviceReadBps': None, u'VolumeDriver': u'', u'ReadonlyRootfs': False,
                              u'CpuShares': 0, u'PublishAllPorts': False, u'MemoryReservation': 0,
                              u'BlkioWeightDevice': None, u'ConsoleSize': [0, 0], u'NetworkMode': u'tmp_default',
                              u'BlkioDeviceWriteBps': None, u'Isolation': u'', u'GroupAdd': None, u'Devices': None,
                              u'BlkioDeviceWriteIOps': None, u'Binds': [], u'CpusetMems': u'', u'KernelMemory': 0,
                              u'UTSMode': u'', u'PidMode': u'', u'VolumesFrom': [], u'CapDrop': None,
                              u'DnsOptions': None, u'ShmSize': 67108864, u'Links': None, u'IpcMode': u'',
                              u'PortBindings': {}, u'SecurityOpt': None, u'CapAdd': None, u'Memory': 0,
                              u'OomKillDisable': False, u'LogConfig': {u'Config': {}, u'Type': u'json-file'}},
              u'Id': u'8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550', u'MountLabel': u''}
containers = [{u'Status': u'Up 3 hours', u'Created': 1457533924, u'Image': u'haproxy',
               u'Labels': {u'com.docker.compose.service': u'lb',
                           u'com.docker.compose.config-hash': u'd885398ce9e71438ec5d8a8ee349d189b2d056b2122e74186e813b433577c353',
                           u'com.docker.compose.project': u'tmp', u'com.docker.compose.version': u'1.6.0',
                           u'com.docker.compose.oneoff': u'False', u'com.docker.compose.container-number': u'1'},
               u'NetworkSettings': {u'Networks': {
                   u'tmp_default': {u'NetworkID': u'', u'MacAddress': u'02:42:ac:13:00:04',
                                    u'GlobalIPv6PrefixLen': 0, u'Links': None, u'GlobalIPv6Address': u'',
                                    u'IPv6Gateway': u'', u'IPAMConfig': None,
                                    u'EndpointID': u'1ff219fbde6eade176066f250010e4de41a1e0403083b5413de7c9de3582d6e2',
                                    u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.4', u'Gateway': u'172.19.0.1',
                                    u'Aliases': None}}}, u'HostConfig': {u'NetworkMode': u'tmp_default'},
               u'ImageID': u'sha256:7682ea99c4ce6811154dd2b2fad3a6b374adc08e9b495068e903686e77882dfd',
               u'Command': u'dockercloud-haproxy', u'Names': [u'/tmp_lb_1'],
               u'Id': u'b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c',
               u'Ports': [{u'IP': u'0.0.0.0', u'Type': u'tcp', u'PublicPort': 80, u'PrivatePort': 80},
                          {u'Type': u'tcp', u'PrivatePort': 1936}, {u'Type': u'tcp', u'PrivatePort': 443}]},
              {u'Status': u'Up 3 hours', u'Created': 1457533924, u'Image': u'dockercloud/hello-world',
               u'Labels': {u'com.docker.compose.service': u'hello',
                           u'com.docker.compose.config-hash': u'ea29a97e3dceca1e7926d7d8d9e6e6709bb169d572f244be149dd187775101c5',
                           u'com.docker.compose.project': u'tmp', u'com.docker.compose.version': u'1.6.0',
                           u'com.docker.compose.oneoff': u'False', u'com.docker.compose.container-number': u'1'},
               u'NetworkSettings': {u'Networks': {
                   u'tmp_default': {u'NetworkID': u'', u'MacAddress': u'02:42:ac:13:00:03',
                                    u'GlobalIPv6PrefixLen': 0, u'Links': None, u'GlobalIPv6Address': u'',
                                    u'IPv6Gateway': u'', u'IPAMConfig': None,
                                    u'EndpointID': u'c0a2a68da8d03fc8907c965c6cf9641100fe8d22eca7ae61b4a4a1dcae7e8b09',
                                    u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.3', u'Gateway': u'172.19.0.1',
                                    u'Aliases': None}}}, u'HostConfig': {u'NetworkMode': u'tmp_default'},
               u'ImageID': u'sha256:b05299680b1d33adab9987c5a49b8e374fa0c48c6aa22191b3b71d8fcdce97d0',
               u'Command': u'/bin/sh -c \'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"\'',
               u'Names': [u'/tmp_hello_1'],
               u'Id': u'a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b',
               u'Ports': [{u'Type': u'tcp', u'PrivatePort': 80}]},
              {u'Status': u'Up 3 hours', u'Created': 1457533924, u'Image': u'dockercloud/hello-world',
               u'Labels': {u'com.docker.compose.service': u'world',
                           u'com.docker.compose.config-hash': u'd94bc3989630b0089b0b1e9fd29f0808618f078e84e61b687c6415ed6e424d43',
                           u'com.docker.compose.project': u'tmp', u'com.docker.compose.version': u'1.6.0',
                           u'com.docker.compose.oneoff': u'False', u'com.docker.compose.container-number': u'1'},
               u'NetworkSettings': {u'Networks': {
                   u'tmp_default': {u'NetworkID': u'', u'MacAddress': u'02:42:ac:13:00:02',
                                    u'GlobalIPv6PrefixLen': 0, u'Links': None, u'GlobalIPv6Address': u'',
                                    u'IPv6Gateway': u'', u'IPAMConfig': None,
                                    u'EndpointID': u'8cac874933ef933f82a182474d849d36b363cde076b75960bc36abac49b4a08e',
                                    u'IPPrefixLen': 16, u'IPAddress': u'172.19.0.2', u'Gateway': u'172.19.0.1',
                                    u'Aliases': None}}}, u'HostConfig': {u'NetworkMode': u'tmp_default'},
               u'ImageID': u'sha256:b05299680b1d33adab9987c5a49b8e374fa0c48c6aa22191b3b71d8fcdce97d0',
               u'Command': u'/bin/sh -c \'php-fpm -d variables_order="EGPCS" && (tail -F /var/log/nginx/access.log &) && exec nginx -g "daemon off;"\'',
               u'Names': [u'/tmp_world_1'],
               u'Id': u'8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550',
               u'Ports': [{u'Type': u'tcp', u'PrivatePort': 80}]}]
links = {u'8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550':
             {'service_name': u'tmp_world',
              'container_name': u'tmp_world_1',
              'container_envvars': [
                  {'value': u'ab.com',
                   'key': u'VIRTUAL_HOST'}, {
                      'value': u'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                      'key': u'PATH'}],
              'compose_service': u'world',
              'compose_project': u'tmp',
              'endpoints': {
                  u'80/tcp': u'tcp://tmp_world_1:80'}},
         u'a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b':
             {'service_name': u'tmp_hello',
              'container_name': u'tmp_hello_1',
              'container_envvars': [
                  {'value': u'a.com',
                   'key': u'VIRTUAL_HOST'}, {
                      'value': u'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                      'key': u'PATH'}],
              'compose_service': u'hello',
              'compose_project': u'tmp',
              'endpoints': {
                  u'80/tcp': u'tcp://tmp_hello_1:80'}}}


class NewLinkHelperTestCase(unittest.TestCase):
    class Docker:
        def inspect_container(self, container_id):
            if container_id == "b02cb80c8a8cec248cf5109abd7cab1eb2d05012fcbfe146c4aa2e6fdeb4a52c":
                return container1
            if container_id == "a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b":
                return container2
            if container_id == "8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550":
                return container3

        def containers(self):
            return containers

    def test_calc_links(self):
        docker = self.Docker()
        self.assertEqual(links, _calc_links(docker, ['hello', 'world'], 'tmp'))

    def test_get_additional_links(self):
        docker = self.Docker()

        additional_links, additional_services = get_additional_links(docker, "tmp:hello, tmp:world")
        self.assertEqual(links, additional_links)
        self.assertEqual(set(["tmp_hello","tmp_world"]), additional_services)

        additional_links, additional_services = get_additional_links(docker, "tmp:hello, tmp:world, tmp:aaa, aaa:bbb")
        self.assertEqual(links, additional_links)
        self.assertSetEqual(set(["tmp_hello", "tmp_world"]), additional_services)

    def test_get_container_endpoints(self):
        endpoints = {u'1936/tcp': u'tcp://tmp_lb_1:1936', u'443/tcp': u'tcp://tmp_lb_1:443',
                     u'80/tcp': u'tcp://tmp_lb_1:80'}
        self.assertEqual(endpoints, _get_container_endpoints(container1, "tmp_lb_1"))

        endpoints = {u'1936/tcp': u'tcp://something:1936', u'443/tcp': u'tcp://something:443',
                     u'80/tcp': u'tcp://something:80'}
        self.assertEqual(endpoints, _get_container_endpoints(container1, "something"))

    def test_get_container_envvars(self):
        envvars = [{'value': u'tcp://192.168.99.100:2376', 'key': u'DOCKER_HOST'},
                   {'value': u'1', 'key': u'DOCKER_TLS_VERIFY'},
                   {'value': u'/Users/hfeng/.docker/machine/machines/default', 'key': u'DOCKER_CERT_PATH'},
                   {'value': u'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'key': u'PATH'},
                   {'value': u'127.0.0.1', 'key': u'RSYSLOG_DESTINATION'}, {'value': u'http', 'key': u'MODE'},
                   {'value': u'roundrobin', 'key': u'BALANCE'}, {'value': u'4096', 'key': u'MAXCONN'},
                   {'value': u'redispatch, httplog, dontlognull, forwardfor', 'key': u'OPTION'},
                   {'value': u'connect 5000, client 50000, server 50000', 'key': u'TIMEOUT'},
                   {'value': u'1936', 'key': u'STATS_PORT'}, {'value': u'stats:stats', 'key': u'STATS_AUTH'},
                   {'value': u'no-sslv3', 'key': u'SSL_BIND_OPTIONS'}, {
                       'value': u'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:DHE-DSS-AES128-SHA:DES-CBC3-SHA',
                       'key': u'SSL_BIND_CIPHERS'}, {'value': u'check', 'key': u'HEALTH_CHECK'}]
        self.assertEqual(envvars, _get_container_envvars(container1))

    def test_get_link_compose_services(self):
        services = [u'hello', u'world']
        self.assertEqual(services, _get_linked_compose_services(container1["NetworkSettings"]["Networks"], 'tmp'))

        self.assertEqual([], _get_linked_compose_services(container1["NetworkSettings"]["Networks"], ''))

    def test_get_service_links_str(self):
        self.assertEqual([u'tmp_hello', u'tmp_world'], get_service_links_str(links))

    def test_get_container_links_str(self):
        self.assertEqual([u'tmp_hello_1', u'tmp_world_1'], get_container_links_str(links))
