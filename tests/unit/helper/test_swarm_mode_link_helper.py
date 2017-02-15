import json
import unittest

from haproxy.helper.swarm_mode_link_helper import *

haproxy_inspect = json.loads('''{
        "Id": "3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74",
        "Created": "2016-11-02T21:35:22.932871142Z",
        "Path": "/sbin/tini",
        "Args": [
            "--",
            "dockercloud-haproxy"
        ],
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
            "OOMKilled": false,
            "Dead": false,
            "Pid": 24523,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2016-11-02T21:35:23.620757277Z",
            "FinishedAt": "0001-01-01T00:00:00Z"
        },
        "Image": "sha256:fd9d2fb63734019320a868043deb1c38455d411223329b3b7b54942a84290cdb",
        "ResolvConfPath": "/var/lib/docker/containers/3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74/resolv.conf",
        "HostnamePath": "/var/lib/docker/containers/3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74/hostname",
        "HostsPath": "/var/lib/docker/containers/3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74/hosts",
        "LogPath": "/var/lib/docker/containers/3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74/3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74-json.log",
        "Name": "/haproxy.1.dhdlwtxof3wrect3fa6it88zz",
        "RestartCount": 0,
        "Driver": "aufs",
        "MountLabel": "",
        "ProcessLabel": "",
        "AppArmorProfile": "",
        "ExecIDs": null,
        "HostConfig": {
            "Binds": [
                "/var/run/docker.sock:/var/run/docker.sock"
            ],
            "ContainerIDFile": "",
            "LogConfig": {
                "Type": "json-file",
                "Config": {}
            },
            "NetworkMode": "default",
            "PortBindings": null,
            "RestartPolicy": {
                "Name": "",
                "MaximumRetryCount": 0
            },
            "AutoRemove": false,
            "VolumeDriver": "",
            "VolumesFrom": null,
            "CapAdd": null,
            "CapDrop": null,
            "Dns": null,
            "DnsOptions": null,
            "DnsSearch": null,
            "ExtraHosts": null,
            "GroupAdd": null,
            "IpcMode": "",
            "Cgroup": "",
            "Links": null,
            "OomScoreAdj": 0,
            "PidMode": "",
            "Privileged": false,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "SecurityOpt": null,
            "UTSMode": "",
            "UsernsMode": "",
            "ShmSize": 67108864,
            "Runtime": "runc",
            "ConsoleSize": [
                0,
                0
            ],
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": null,
            "BlkioDeviceReadBps": null,
            "BlkioDeviceWriteBps": null,
            "BlkioDeviceReadIOps": null,
            "BlkioDeviceWriteIOps": null,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": null,
            "DiskQuota": 0,
            "KernelMemory": 0,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": -1,
            "OomKillDisable": false,
            "PidsLimit": 0,
            "Ulimits": null,
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0
        },
        "GraphDriver": {
            "Name": "aufs",
            "Data": null
        },
        "Mounts": [
            {
                "Source": "/var/run/docker.sock",
                "Destination": "/var/run/docker.sock",
                "Mode": "",
                "RW": true,
                "Propagation": "rprivate"
            }
        ],
        "Config": {
            "Hostname": "3daf8d8386f1",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "ExposedPorts": {
                "1936/tcp": {},
                "443/tcp": {},
                "80/tcp": {}
            },
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "RSYSLOG_DESTINATION=127.0.0.1",
                "MODE=http",
                "BALANCE=roundrobin",
                "MAXCONN=4096",
                "OPTION=redispatch, httplog, dontlognull, forwardfor",
                "TIMEOUT=connect 5000, client 50000, server 50000",
                "STATS_PORT=1936",
                "STATS_AUTH=stats:stats",
                "SSL_BIND_OPTIONS=no-sslv3",
                "SSL_BIND_CIPHERS=ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:DHE-DSS-AES128-SHA:DES-CBC3-SHA",
                "HEALTH_CHECK=check inter 2000 rise 2 fall 3",
                "NBPROC=1"
            ],
            "Cmd": [
                "dockercloud-haproxy"
            ],
            "Image": "tifayuki/haproxy:latest",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": [
                "/sbin/tini",
                "--"
            ],
            "OnBuild": null,
            "Labels": {
                "com.docker.swarm.node.id": "cynvrub3608h5yepe3ryhnfgc",
                "com.docker.swarm.service.id": "07ql4q5a48seh1uhcr2m7ngar",
                "com.docker.swarm.service.name": "haproxy",
                "com.docker.swarm.task": "",
                "com.docker.swarm.task.id": "dhdlwtxof3wrect3fa6it88zz",
                "com.docker.swarm.task.name": "haproxy.1"
            }
        },
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "66f3808b0dfc854b316f66b34db0ab79b333c853f52f7fc46dc5843c585195a3",
            "HairpinMode": false,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {
                "1936/tcp": null,
                "443/tcp": null,
                "80/tcp": null
            },
            "SandboxKey": "/var/run/docker/netns/66f3808b0dfc",
            "SecondaryIPAddresses": null,
            "SecondaryIPv6Addresses": null,
            "EndpointID": "",
            "Gateway": "",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "",
            "IPPrefixLen": 0,
            "IPv6Gateway": "",
            "MacAddress": "",
            "Networks": {
                "ingress": {
                    "IPAMConfig": {
                        "IPv4Address": "10.255.0.6"
                    },
                    "Links": null,
                    "Aliases": [
                        "3daf8d8386f1"
                    ],
                    "NetworkID": "b951j4at14qali5nxevshec93",
                    "EndpointID": "f996d826b406aa17ef8f821f870c3e2f1ebb2df7cdf6611b5c35aad8f9bb27d8",
                    "Gateway": "",
                    "IPAddress": "10.255.0.6",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:0a:ff:00:06"
                },
                "proxy": {
                    "IPAMConfig": {
                        "IPv4Address": "10.0.0.3"
                    },
                    "Links": null,
                    "Aliases": [
                        "3daf8d8386f1"
                    ],
                    "NetworkID": "0l130ctu8xay6vfft1mb4tjv0",
                    "EndpointID": "5999f497ee3d1f5bfc1b1987337fda0b171073b5d5d144239324c40a3fdae48a",
                    "Gateway": "",
                    "IPAddress": "10.0.0.3",
                    "IPPrefixLen": 24,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:0a:00:00:03"
                }
            }
        }
    }''')

tasks = json.loads('''[
   {
      "ID":"31b6fuwub6dcgdrvy0kivxvug",
      "Version":{
         "Index":349
      },
      "CreatedAt":"2016-11-02T21:56:05.92682272Z",
      "UpdatedAt":"2016-11-02T21:56:11.655915956Z",
      "Spec":{
         "ContainerSpec":{
            "Image":"dockercloud/hello-world",
            "Env":[
               "SERVICE_PORTS=80"
            ]
         },
         "Resources":{
            "Limits":{

            },
            "Reservations":{

            }
         },
         "RestartPolicy":{
            "Condition":"any",
            "MaxAttempts":0
         },
         "Placement":{
            "Constraints":[
               "node.role != manager"
            ]
         }
      },
      "ServiceID":"d3eeqw6rtkbgu70cxb5y7axcq",
      "Slot":3,
      "NodeID":"965jrum2z15lhg6sjt782rjlg",
      "Status":{
         "Timestamp":"2016-11-02T21:56:11.604463096Z",
         "State":"running",
         "Message":"started",
         "ContainerStatus":{
            "ContainerID":"11f9bc253be25966e652817aca64f640363b1f699041d90164f6de9176dac555",
            "PID":13098
         }
      },
      "DesiredState":"running",
      "NetworksAttachments":[
         {
            "Network":{
               "ID":"0l130ctu8xay6vfft1mb4tjv0",
               "Version":{
                  "Index":18
               },
               "CreatedAt":"2016-11-02T21:26:20.984765988Z",
               "UpdatedAt":"2016-11-02T21:26:20.987359847Z",
               "Spec":{
                  "Name":"proxy",
                  "DriverConfiguration":{
                     "Name":"overlay"
                  },
                  "IPAMOptions":{
                     "Driver":{
                        "Name":"default"
                     }
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"257"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.0.0.0/24",
                        "Gateway":"10.0.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.0.0.7/24"
            ]
         }
      ]
   },
   {
      "ID":"7y45xdhy929wzcq94wqdqb8d3",
      "Version":{
         "Index":339
      },
      "CreatedAt":"2016-11-02T21:54:47.893974769Z",
      "UpdatedAt":"2016-11-02T21:54:49.631538801Z",
      "Spec":{
         "ContainerSpec":{
            "Image":"dockercloud/hello-world",
            "Env":[
               "SERVICE_PORTS=80"
            ]
         },
         "Resources":{
            "Limits":{

            },
            "Reservations":{

            }
         },
         "RestartPolicy":{
            "Condition":"any",
            "MaxAttempts":0
         },
         "Placement":{
            "Constraints":[
               "node.role != manager"
            ]
         }
      },
      "ServiceID":"d3eeqw6rtkbgu70cxb5y7axcq",
      "Slot":2,
      "NodeID":"965jrum2z15lhg6sjt782rjlg",
      "Status":{
         "Timestamp":"2016-11-02T21:54:49.535733008Z",
         "State":"running",
         "Message":"started",
         "ContainerStatus":{
            "ContainerID":"55a87868d5199974c97fdb6767266254cffb4e9361236f685959c51fbb76e632",
            "PID":12789
         }
      },
      "DesiredState":"running",
      "NetworksAttachments":[
         {
            "Network":{
               "ID":"0l130ctu8xay6vfft1mb4tjv0",
               "Version":{
                  "Index":18
               },
               "CreatedAt":"2016-11-02T21:26:20.984765988Z",
               "UpdatedAt":"2016-11-02T21:26:20.987359847Z",
               "Spec":{
                  "Name":"proxy",
                  "DriverConfiguration":{
                     "Name":"overlay"
                  },
                  "IPAMOptions":{
                     "Driver":{
                        "Name":"default"
                     }
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"257"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.0.0.0/24",
                        "Gateway":"10.0.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.0.0.6/24"
            ]
         }
      ]
   },
   {
      "ID":"8chj1pflicy6l927q0p7rme99",
      "Version":{
         "Index":344
      },
      "CreatedAt":"2016-11-02T21:54:47.89412758Z",
      "UpdatedAt":"2016-11-02T21:56:06.026779896Z",
      "Spec":{
         "ContainerSpec":{
            "Image":"dockercloud/hello-world",
            "Env":[
               "SERVICE_PORTS=80"
            ]
         },
         "Resources":{
            "Limits":{

            },
            "Reservations":{

            }
         },
         "RestartPolicy":{
            "Condition":"any",
            "MaxAttempts":0
         },
         "Placement":{
            "Constraints":[
               "node.role != manager"
            ]
         }
      },
      "ServiceID":"d3eeqw6rtkbgu70cxb5y7axcq",
      "Slot":3,
      "NodeID":"965jrum2z15lhg6sjt782rjlg",
      "Status":{
         "Timestamp":"2016-11-02T21:56:05.904153598Z",
         "State":"failed",
         "Message":"started",
         "Err":"task: non-zero exit (137)",
         "ContainerStatus":{
            "ContainerID":"ccaae14ec0a34c771e854301ec53254d9b21d816c34b7306cc5873ecb4193f73",
            "ExitCode":137
         }
      },
      "DesiredState":"shutdown",
      "NetworksAttachments":[
         {
            "Network":{
               "ID":"0l130ctu8xay6vfft1mb4tjv0",
               "Version":{
                  "Index":18
               },
               "CreatedAt":"2016-11-02T21:26:20.984765988Z",
               "UpdatedAt":"2016-11-02T21:26:20.987359847Z",
               "Spec":{
                  "Name":"proxy",
                  "DriverConfiguration":{
                     "Name":"overlay"
                  },
                  "IPAMOptions":{
                     "Driver":{
                        "Name":"default"
                     }
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"257"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.0.0.0/24",
                        "Gateway":"10.0.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.0.0.7/24"
            ]
         }
      ]
   },
   {
      "ID":"bbref0yvjbix87pv6xz1jc3pr",
      "Version":{
         "Index":330
      },
      "CreatedAt":"2016-11-02T21:54:24.145238542Z",
      "UpdatedAt":"2016-11-02T21:54:25.728068594Z",
      "Spec":{
         "ContainerSpec":{
            "Image":"dockercloud/hello-world",
            "Env":[
               "SERVICE_PORTS=80"
            ]
         },
         "Resources":{
            "Limits":{

            },
            "Reservations":{

            }
         },
         "RestartPolicy":{
            "Condition":"any",
            "MaxAttempts":0
         },
         "Placement":{
            "Constraints":[
               "node.role != manager"
            ]
         }
      },
      "ServiceID":"d3eeqw6rtkbgu70cxb5y7axcq",
      "Slot":1,
      "NodeID":"965jrum2z15lhg6sjt782rjlg",
      "Status":{
         "Timestamp":"2016-11-02T21:54:25.701959042Z",
         "State":"running",
         "Message":"started",
         "ContainerStatus":{
            "ContainerID":"c3d5891385d4ea40baec5d5593f9d5559ffe847b6fd9be48ec2e7c6313322f49",
            "PID":12511
         }
      },
      "DesiredState":"running",
      "NetworksAttachments":[
         {
            "Network":{
               "ID":"0l130ctu8xay6vfft1mb4tjv0",
               "Version":{
                  "Index":18
               },
               "CreatedAt":"2016-11-02T21:26:20.984765988Z",
               "UpdatedAt":"2016-11-02T21:26:20.987359847Z",
               "Spec":{
                  "Name":"proxy",
                  "DriverConfiguration":{
                     "Name":"overlay"
                  },
                  "IPAMOptions":{
                     "Driver":{
                        "Name":"default"
                     }
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"257"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.0.0.0/24",
                        "Gateway":"10.0.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.0.0.5/24"
            ]
         }
      ]
   },
   {
      "ID":"dhdlwtxof3wrect3fa6it88zz",
      "Version":{
         "Index":309
      },
      "CreatedAt":"2016-11-02T21:35:22.594024912Z",
      "UpdatedAt":"2016-11-02T21:35:23.671835435Z",
      "Spec":{
         "ContainerSpec":{
            "Image":"tifayuki/haproxy",
            "Mounts":[
               {
                  "Type":"bind",
                  "Source":"/var/run/docker.sock",
                  "Target":"/var/run/docker.sock"
               }
            ]
         },
         "Resources":{
            "Limits":{

            },
            "Reservations":{

            }
         },
         "RestartPolicy":{
            "Condition":"any",
            "MaxAttempts":0
         },
         "Placement":{
            "Constraints":[
               "node.role == manager"
            ]
         }
      },
      "ServiceID":"07ql4q5a48seh1uhcr2m7ngar",
      "Slot":1,
      "NodeID":"cynvrub3608h5yepe3ryhnfgc",
      "Status":{
         "Timestamp":"2016-11-02T21:35:23.623790929Z",
         "State":"running",
         "Message":"started",
         "ContainerStatus":{
            "ContainerID":"3daf8d8386f141466a62dbc4bfc5016f364202277dbe1a34b4bd7da0d4f17c74",
            "PID":24523
         }
      },
      "DesiredState":"running",
      "NetworksAttachments":[
         {
            "Network":{
               "ID":"b951j4at14qali5nxevshec93",
               "Version":{
                  "Index":7
               },
               "CreatedAt":"2016-11-02T21:19:46.859033951Z",
               "UpdatedAt":"2016-11-02T21:19:46.861842857Z",
               "Spec":{
                  "Name":"ingress",
                  "Labels":{
                     "com.docker.swarm.internal":"true"
                  },
                  "DriverConfiguration":{

                  },
                  "IPAMOptions":{
                     "Driver":{

                     },
                     "Configs":[
                        {
                           "Subnet":"10.255.0.0/16",
                           "Gateway":"10.255.0.1"
                        }
                     ]
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"256"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.255.0.0/16",
                        "Gateway":"10.255.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.255.0.6/16"
            ]
         },
         {
            "Network":{
               "ID":"0l130ctu8xay6vfft1mb4tjv0",
               "Version":{
                  "Index":18
               },
               "CreatedAt":"2016-11-02T21:26:20.984765988Z",
               "UpdatedAt":"2016-11-02T21:26:20.987359847Z",
               "Spec":{
                  "Name":"proxy",
                  "DriverConfiguration":{
                     "Name":"overlay"
                  },
                  "IPAMOptions":{
                     "Driver":{
                        "Name":"default"
                     }
                  }
               },
               "DriverState":{
                  "Name":"overlay",
                  "Options":{
                     "com.docker.network.driver.overlay.vxlanid_list":"257"
                  }
               },
               "IPAMOptions":{
                  "Driver":{
                     "Name":"default"
                  },
                  "Configs":[
                     {
                        "Subnet":"10.0.0.0/24",
                        "Gateway":"10.0.0.1"
                     }
                  ]
               }
            },
            "Addresses":[
               "10.0.0.3/24"
            ]
         }
      ]
   }
]''')

services = json.loads('''[
   {
      "ID":"07ql4q5a48seh1uhcr2m7ngar",
      "Version":{
         "Index":303
      },
      "CreatedAt":"2016-11-02T21:35:22.58592166Z",
      "UpdatedAt":"2016-11-02T21:35:22.589063478Z",
      "Spec":{
         "Name":"haproxy",
         "TaskTemplate":{
            "ContainerSpec":{
               "Image":"tifayuki/haproxy",
               "Mounts":[
                  {
                     "Type":"bind",
                     "Source":"/var/run/docker.sock",
                     "Target":"/var/run/docker.sock"
                  }
               ]
            },
            "Resources":{
               "Limits":{

               },
               "Reservations":{

               }
            },
            "RestartPolicy":{
               "Condition":"any",
               "MaxAttempts":0
            },
            "Placement":{
               "Constraints":[
                  "node.role == manager"
               ]
            }
         },
         "Mode":{
            "Replicated":{
               "Replicas":1
            }
         },
         "UpdateConfig":{
            "Parallelism":1,
            "FailureAction":"pause"
         },
         "Networks":[
            {
               "Target":"0l130ctu8xay6vfft1mb4tjv0"
            }
         ],
         "EndpointSpec":{
            "Mode":"vip",
            "Ports":[
               {
                  "Protocol":"tcp",
                  "TargetPort":80,
                  "PublishedPort":80
               }
            ]
         }
      },
      "Endpoint":{
         "Spec":{
            "Mode":"vip",
            "Ports":[
               {
                  "Protocol":"tcp",
                  "TargetPort":80,
                  "PublishedPort":80
               }
            ]
         },
         "Ports":[
            {
               "Protocol":"tcp",
               "TargetPort":80,
               "PublishedPort":80
            }
         ],
         "VirtualIPs":[
            {
               "NetworkID":"b951j4at14qali5nxevshec93",
               "Addr":"10.255.0.5/16"
            },
            {
               "NetworkID":"0l130ctu8xay6vfft1mb4tjv0",
               "Addr":"10.0.0.2/24"
            }
         ]
      },
      "UpdateStatus":{
         "StartedAt":"0001-01-01T00:00:00Z",
         "CompletedAt":"0001-01-01T00:00:00Z"
      }
   },
   {
      "ID":"d3eeqw6rtkbgu70cxb5y7axcq",
      "Version":{
         "Index":331
      },
      "CreatedAt":"2016-11-02T21:54:24.135035851Z",
      "UpdatedAt":"2016-11-02T21:54:47.891254579Z",
      "Spec":{
         "Name":"app",
         "TaskTemplate":{
            "ContainerSpec":{
               "Image":"dockercloud/hello-world",
               "Env":[
                  "SERVICE_PORTS=80"
               ]
            },
            "Resources":{
               "Limits":{

               },
               "Reservations":{

               }
            },
            "RestartPolicy":{
               "Condition":"any",
               "MaxAttempts":0
            },
            "Placement":{
               "Constraints":[
                  "node.role != manager"
               ]
            }
         },
         "Mode":{
            "Replicated":{
               "Replicas":3
            }
         },
         "UpdateConfig":{
            "Parallelism":1,
            "FailureAction":"pause"
         },
         "Networks":[
            {
               "Target":"0l130ctu8xay6vfft1mb4tjv0"
            }
         ],
         "EndpointSpec":{
            "Mode":"vip"
         }
      },
      "Endpoint":{
         "Spec":{
            "Mode":"vip"
         },
         "VirtualIPs":[
            {
               "NetworkID":"0l130ctu8xay6vfft1mb4tjv0",
               "Addr":"10.0.0.4/24"
            }
         ]
      },
      "UpdateStatus":{
         "StartedAt":"0001-01-01T00:00:00Z",
         "CompletedAt":"0001-01-01T00:00:00Z"
      }
   }
]''')

expected_links = expected_links = {
    u'7y45xdhy929wzcq94wqdqb8d3': {'service_name': u'app', 'endpoints': {u'80/tcp': u'tcp://10.0.0.6:80'},
                                   'container_envvars': [{'value': u'80', 'key': u'SERVICE_PORTS'}],
                                   'container_name': u'app.2.7y45xdhy929wzcq94wqdqb8d3'},
    u'bbref0yvjbix87pv6xz1jc3pr': {'service_name': u'app', 'endpoints': {u'80/tcp': u'tcp://10.0.0.5:80'},
                                   'container_envvars': [{'value': u'80', 'key': u'SERVICE_PORTS'}],
                                   'container_name': u'app.1.bbref0yvjbix87pv6xz1jc3pr'},
    u'31b6fuwub6dcgdrvy0kivxvug': {'service_name': u'app', 'endpoints': {u'80/tcp': u'tcp://10.0.0.7:80'},
                                   'container_envvars': [{'value': u'80', 'key': u'SERVICE_PORTS'}],
                                   'container_name': u'app.3.31b6fuwub6dcgdrvy0kivxvug'}}
expected_linked_tasks = {u'7y45xdhy929wzcq94wqdqb8d3': {}, u'bbref0yvjbix87pv6xz1jc3pr': {},
                         u'31b6fuwub6dcgdrvy0kivxvug': {}}
expected_nets = {"0l130ctu8xay6vfft1mb4tjv0"}
expected_service_id = "07ql4q5a48seh1uhcr2m7ngar"


class SWARMModeLinkHelperTestCase(unittest.TestCase):
    def test_get_new_added_links_uri_with_exception(self):
        class Docker:
            def inspect_container(self, container_id):
                raise Exception("an exception")

        service_id, nets = get_swarm_mode_haproxy_id_nets(Docker(), "exception")
        self.assertEquals("", service_id)
        self.assertEquals(set(), nets)

    def test_get_new_added_links_uri(self):
        class Docker:
            def inspect_container(self, container_id):
                return haproxy_inspect

        service_id, nets = get_swarm_mode_haproxy_id_nets(Docker(), "id")
        self.assertEquals(expected_service_id, service_id)
        self.assertEquals(expected_nets, nets)

    def test_get_swarm_mode_links(self):
        class Docker:
            def services(self):
                return services

            def tasks(self, filters):
                return [t for t in tasks if t.get("DesiredState", "") == "running"]

        links, linked_tasks = get_swarm_mode_links(Docker(), expected_service_id, expected_nets)
        self.assertEquals(expected_links, links)
        self.assertEquals(expected_linked_tasks, linked_tasks)

    def test_get_task_links(self):
        links, linked_tasks = get_task_links([t for t in tasks if t.get("DesiredState", "") == "running"],
                                             services, expected_service_id, expected_nets)
        self.assertEquals(expected_links, links)
        self.assertEquals(expected_linked_tasks, linked_tasks)

    def test_get_tasks_envvars(self):
        envvar = get_task_envvars(tasks[0].get("Spec", {}).get("ContainerSpec", {}).get("Env", []))
        self.assertEquals([{'value': u'80', 'key': u'SERVICE_PORTS'}], envvar)
