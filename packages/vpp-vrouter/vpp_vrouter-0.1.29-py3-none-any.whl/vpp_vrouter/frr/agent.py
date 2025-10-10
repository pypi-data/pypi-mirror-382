"""
The agent running inside FRR container. The server relays FRR-related commands to this agent and the agent performs then
on the FRR instance. The agent also copy BGP-learned routes into VPP by acting as configuration client configuring routes
using server. The connection between agent and server is done by using Pyro5, just like in client/server connection.
"""

import logging
import subprocess
import threading

from vpp_vrouter.common.models import ProcessCallReply
from vpp_vrouter.common.utils import configure_main_logger, configure_pyro5_logging

logger = configure_main_logger(f"frr-agent", logging.DEBUG)
configure_pyro5_logging()  # must be before any Pyro5 import to configure logging
from vpp_vrouter.server import pyro
from vpp_vrouter.frr import route_reflector


def frr_api_wrapper():
    """Creates wrapper class that has all FRR API methods. The wrapper represents FRR API server"""

    @pyro.api_expose
    class Wrapper(pyro.NamedWrapper):
        def __init__(self):
            self.lock = threading.Lock()

        @staticmethod
        def name():
            return "frr.api"

        def run_vtysh_command(self, command) -> ProcessCallReply:
            try:
                self.lock.acquire(blocking=True)
                result = subprocess.run(
                    f"""vtysh -c "{command}" """, shell=True, capture_output=True
                )
                logger.info(f"Call of run_vtysh_command: {command} (result: {result})")
                return ProcessCallReply(
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            except Exception:
                logger.exception("Exception in run_vtysh_command")
            finally:
                self.lock.release()

        def load_vtysh_configuration(self, configuration: str) -> ProcessCallReply:
            try:
                self.lock.acquire(blocking=True)
                with open(r"/etc/frr/frr.conf", "w") as frr_config:
                    frr_config.write(configuration)
                result = subprocess.run("vtysh -b", shell=True, capture_output=True)
                logger.info(
                    f"Call of load_vtysh_configuration: configuration:\n{configuration}\n (result: {result})"
                )
                return ProcessCallReply(
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            except Exception:
                logger.exception("Exception in load_vtysh_configuration")
            finally:
                self.lock.release()

        def configure_route_reflector(
            self, papi_server_host: str = "0.0.0.0", papi_server_port: int = 9999
        ):
            try:
                self.lock.acquire(blocking=True)
                logger.info(
                    f"configuring route reflector (papi_server_host={papi_server_host}, "
                    f"papi_server_port={papi_server_port})"
                )
                route_reflector.configure_route_reflector(
                    papi_server_host=papi_server_host, papi_server_port=papi_server_port
                )
            except Exception:
                logger.exception("Exception in configure_route_reflector")
            finally:
                self.lock.release()

    return Wrapper


if __name__ == "__main__":
    graceful_shutdown_callback = route_reflector.start_route_reflector_in_background()
    pyro.run_server_loop(
        frr_api_wrapper(), pyro_daemon_port=6666, nameserver_daemon_port=7777
    )
    graceful_shutdown_callback()
