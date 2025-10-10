"""
Provides utility functionality related to Pyro5 framework used for communication between client and server.
"""

import time
from abc import ABC

import Pyro5

from vpp_vrouter.common import serializers
from vpp_vrouter.common.utils import get_main_logger

logger = get_main_logger()
api_expose = Pyro5.api.expose


class NamedWrapper(ABC):
    @staticmethod
    def name():
        pass


def _init(wrappers, pyro_daemon_port, nameserver_daemon_port):
    """Configure and start Pyro5 instance (multiple daemons)"""

    # configure Pyro settings
    Pyro5.config.SERVERTYPE = "multiplex"
    Pyro5.config.POLLTIMEOUT = 3

    # fix serialization for custom types
    serializers.import_pyro5_serializers()

    # preparing host values for Namespace and Pyro5 main daemon
    # (Note: development and test/production environment is supported:
    # 1. development(Pyro5 runs locally): client connects to namespace daemon and due to its host set to
    # all_ip_addresses, connection from client is accepted. Nameserver provides address to exact object (exposed API)
    # in Pyro5 main daemon (object identified and pyro5 main daemon ip address and port). Client connect directly
    # to pyro5 main daemon and connection is accepted due to correct destination ip address.
    # 2. test/production (Pyro run in container/remotely): client connects to ip address/port of container
    # with namespace daemon (daemon accepts it due to all_ip_addresses set in as its host) and provides back address
    # to exact object (exposed API)in Pyro5 main daemon (object identified and pyro5 main daemon ip address and port).
    # It will reference containers IP address (+ port that should be open on container). Client will connect to
    # container ip and Pyro5 main daemon will see it coming from container interface with container IP address and
    # accept it.
    # Configuring Namespace daemon host to anything else (specific IP address) lead to problem in one of the cases.
    # )
    all_ip_addresses = "0.0.0.0"
    my_ip_address = Pyro5.socketutil.get_ip_address(None, workaround127=True)

    # start pyro name server with broadcast server
    nameserver_uri, nameserver_daemon, broadcast_server = Pyro5.nameserver.start_ns(
        host=all_ip_addresses, port=nameserver_daemon_port
    )
    assert broadcast_server is not None, "expect a broadcast server to be created"
    logger.info("created pyro nameserver, uri=%s" % nameserver_uri)

    # create a pyro daemon
    pyro_daemon = Pyro5.api.Daemon(host=my_ip_address, port=pyro_daemon_port)

    # register wrapper with pyro daemons
    for wrapper in wrappers:
        wrapper_uri = pyro_daemon.register(wrapper)
        logger.info(f"created pyro server for {wrapper.name()} (uri={wrapper_uri})")
        nameserver_daemon.nameserver.register(wrapper.name(), wrapper_uri)

    return (nameserver_daemon, broadcast_server, pyro_daemon)


def _run_loop(nameserver_daemon, broadcast_server, pyro_daemon):
    """Run Pyro5 request loop"""

    # Because this server runs the different daemons using the "multiplex" server type,
    # we can use the built in support (since Pyro 4.44) to combine multiple daemon event loops.
    # We can then simply run the event loop of the 'master daemon'. It will dispatch correctly.
    pyro_daemon.combine(nameserver_daemon)
    pyro_daemon.combine(broadcast_server)

    def loopcondition():
        logger.debug(f"{time.asctime()} Waiting for requests...")
        return True

    pyro_daemon.requestLoop(loopcondition)


def _cleanup(nameserver_daemon, broadcast_server, pyro_daemon):
    """Clean up any Pyro5 setup"""
    # clean up
    nameserver_daemon.close()
    broadcast_server.close()
    pyro_daemon.close()
    pyro_daemon.shutdown()
    logger.info("pyro daemons cleaned up")
    # kill pyro daemon


def get_external_ip_address():
    return Pyro5.socketutil.get_ip_address(None, workaround127=True)


def run_server_loop(*wrappers, pyro_daemon_port=8888, nameserver_daemon_port=9999):
    """Runs Pyro5 server and waits in loop for requests (blocking call)"""

    daemons = _init(wrappers, pyro_daemon_port, nameserver_daemon_port)
    _run_loop(*daemons)
    _cleanup(*daemons)  # for cases when loop breaks/is shutdown by call
