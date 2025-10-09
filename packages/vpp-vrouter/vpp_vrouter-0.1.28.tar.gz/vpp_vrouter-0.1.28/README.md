# Extended VPP API client

[![Build package and sync to S3](https://github.com/Unified-Sentinel-Data-Networks/vrouter-pantheon/actions/workflows/publish-vrouter-s3.yml/badge.svg)](https://github.com/Unified-Sentinel-Data-Networks/vrouter-pantheon/actions/workflows/publish-vrouter-s3.yml)

[![Build and Push FRR Image](https://github.com/Unified-Sentinel-Data-Networks/vrouter-pantheon/actions/workflows/build_frr.yml/badge.svg)](https://github.com/Unified-Sentinel-Data-Networks/vrouter-pantheon/actions/workflows/build_frr.yml)

Python VPP client inspired by [Ligato's vpp-agent][vpp-agent], but using in core the official
[Python VPP client][fd.io python api] distributed by FD.io.
The client is simplified version of vpp-agent. It tries to use all the hard lessons learned from vpp-agent development,
but to add minimal complexity. The main added features are:

1. Automatic configuration dependency resolving
   => postponing/rearranging VPP configuration to not avoid common pitfall of bad ordering of configuration commands for
   VPP)
2. Simplified API
3. Better logging (arranging configuration batches into "Transaction")
4. modularization (-> extensibility)
5. other implicit benefits from VPP-Agent

## Requirements

1. Python 3.10+
2. Python dependency tool [Poetry][poetry]

### Server specific requirements

1. Access to VPP's API json files and VPP API socket of running VPP instance
2. Some API parts require 'sudo' (linux configuration API parts). We don't want to store needed password or run whole
   server with root priviledges, so please set NOPASSWD for using certain linux tools (`ip`, `ln`, `unlink`). You can do
   that by using "sudo visudo" to add this to end of /etc/sudoers:<br>

```
<current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/ip
<current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/ln
<current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/unlink
```

### Client specific requirements

1. Ability to connect to running server (topology requirement: enable firewall, port forwarding,...)

### Test specific requirements

In addition to client and server requirements:

1. Docker
2. Installed linux tools: `ip`, `awk`, `grep`, `ps`, `kill`, `ping` (all only for LinuxConfigurationTestCases
   except `ip`, `ping`)
3. Python tools: `pip` (for LinuxConfigurationTestCases)

### Example specific requirements

In addition to client and server requirements:

1. Docker
2. Installed linux tools: `ip`, `ping`

## How to use it

1. build images (run only once at setup):

```
make images
```

2. start VPP (in container) by:

```
make dev-run
```

(It can be stopped later by `make dev-stop`)

3. run python server (just run python module in `server.py`)
4. choose one of examples in `examples.py` and run it (it will use client code as library (`client.py`))

Or just run one of the integration tests in `tests/test.py`. The integration tests can run all the code in 3 docker
containers (VPP, Server, Client) or just run client locally and other things (VPP, Server) in docker containers.

## How it works

The extended VPP client was designed as server/client. The client is thin-client telling the server what to configure.
The server remember all the configuration and does all the heavy-lifting and configures VPP
using [FD.io VPP client][fd.io python api].
This allows us to have multiple clients that can work separately in docker containers. This is possible due to using
remote object communication library [Pyro5][pyro5].

Server reacts to each configuration change by recomputing the dependencies and deciding which configuration can be
send to VPP with FD.io VPP client. If some configuration needs other things to be configured first (and they are
missing),
then the configuration is blocked (not sent to VPP, just remembered by server) until need configuration arrives from
client.

The client can always request the current configuration known by server (`get_configuration` API) and check the state
of each configuration that was sent to server. The server provides only it's own state, it does not listens to VPP for
changes. The server is the source of truth for VPP configuration. That means that for whatever reason VPP changes its
state, the configuration state in server is the one that should overwrite the VPP configuration (currently there is not
synchronization where server overwrites all VPP configuration according to server-remembered VPP configuration
from user). This means that any configuration of VPP should go through the server.

### VPP

Most of the API is related to configure [VPP][vpp]. The API provided here is only a small portion of the whole VPP API.
It was chosen to support USDN's Failover use case. It supports ACL (firewall), NAT, Static routing, Interface handling
(only loopback, dpdk, wireguard and tap interfaces), LCP and packet capturing(PCAP).

### FRR

There is simple support for the [FRRouting][frr] that controls one FRR instance running inside
[docker container][frr-docker]. Due to the nature of FRR that is actively changing linux routing of default linux
network namespace, the FRR must run in docker container to not mess up routing in the whole node/server.

In addition to FRR functionality, the docker container contains simple [route reflector][frr-reflector] that is copying
the routes learned(and written to docker network namespace) by FRR into VPP. It act just like another client talking to
server that configures the VPP.

### Linux

Some API (route and veth tunnel) is dedicated to configure packet flow in pure linux network namespace. This API
currently uses linux cmd line to configure things and has some limitations (see [limitations](#Limitations))

## Logging

PAPI-Server and FRR-agent create log files that are by default in the working directory where they were launched.
These data are in JSON format and therefore ready to be collected by telemetry tools. By default the same logs are
also writen(duplicated) into the console in non-JSON format for better development comfort.
Pyro5 library has separate log file.

## Limitations

- Pyro5 depends on python serialization capabilities (including 3rd parties) and FD.io VPP client objects are
  not serializable. This results in bad-structured/unstructured FD.io VPP client objects on client side of extended
  VPP client
- the implementation is only a simplified version of vpp-agent, that means only basic features and limited VPP
  configuration support
- Linux-related API (creation of veth tunnel and routes in linux) works currently only if python server is running
  in the host environment (=not working when python server is running inside docker container). Some additional work is
  need to lift this limitation (use some official python docker client instead of linux cmd line, some linux namespace
  exposure/handling in docker container)

[vpp-agent]: https://github.com/ligato/vpp-agent

[poetry]: https://python-poetry.org/docs/

[fd.io python api]: https://wiki.fd.io/view/VPP/Python_API

[vpp]:https://github.com/FDio/vpp

[pyro5]: https://github.com/irmen/Pyro5

[frr]: https://frrouting.org/

[frr-docker]: docker/frr

[frr-reflector]: frr/route_reflector.py
