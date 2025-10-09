"""
Responsible for reflecting BGP-learned routes back to VPP.
"""

import select
import signal
import threading
import time
from enum import IntEnum
from multiprocessing import Pipe

from pyroute2 import IPRoute

from vpp_vrouter.client.client import ExtendedVPPAPIClient
from vpp_vrouter.common import models
from vpp_vrouter.common.utils import get_main_logger

logger = get_main_logger()

# route reflector configuration (must be set from PAPI++ server, but that starts after route_reflector due to
# FRR container starting first for FRR Agent IP address retrieval)
_config_lock = threading.Lock()
_papi_server_host = ""
_papi_server_port = 0


class Proto(IntEnum):  # https://fossies.org/linux/iproute2/etc/iproute2/rt_protos
    UNSPEC = 0
    REDIRECT = 1
    KERNEL = 2
    BOOT = 3
    STATIC = 4
    GATED = 8
    RA = 9
    MRT = 10
    ZEBRA = 11
    BIRD = 12
    DNROUTED = 13
    XORP = 14
    NTK = 15
    DHCP = 16
    KEEPALIVED = 18
    BABEL = 42
    OPENR = 99
    BGP = 186
    ISIS = 187
    OSPF = 188
    RIP = 189
    EIGRP = 192


def configure_route_reflector(
    papi_server_host: str = "0.0.0.0", papi_server_port: int = 9999
):
    with _config_lock:
        global _papi_server_host, _papi_server_port
        _papi_server_host = papi_server_host
        _papi_server_port = papi_server_port


def start_route_reflector_in_background():
    quit_signaling_out, quit_signaling_in = Pipe()
    rr_thread = threading.Thread(target=_route_reflection, args=(quit_signaling_in,))
    rr_thread.start()

    def graceful_shutdown_callback():
        quit_signaling_out.send("")
        rr_thread.join()
        quit_signaling_out.close()
        quit_signaling_in.close()

    return graceful_shutdown_callback


def _wait_for_configuration():
    while True:
        logger.info("waiting for configuration...")
        with _config_lock:
            global _papi_server_host, _papi_server_port
            if _papi_server_host:
                return _papi_server_host, _papi_server_port
        time.sleep(1)


def _route_reflection(quit_signaling_in):
    logger.info("started route reflection thread")
    papi_server_host, papi_server_port = _wait_for_configuration()
    logger.debug("create poll object")
    poll = select.poll()

    logger.debug("create IPRoute object")
    with IPRoute(nlm_generator=True) as ipr:
        logger.debug("register IPRoute for select.POLLIN")
        poll.register(ipr, select.POLLIN)
        poll.register(quit_signaling_in, select.POLLIN)

        logger.debug("bind IPRoute to get broadcasts")
        ipr.bind()

        added_routes = dict()  # dict of previously added routes

        while True:
            logger.debug("waiting for new netlink data")
            try:
                # Note: could use also poll.poll(<timeout in milliseconds>) but that would mean to have compromise
                # between graceful shutdown length and listening interruptions
                notifications = poll.poll()
            except Exception as e:
                logger.exception("exception from netlink data wait", e)
                notifications = []  # nothing was retrieved
            logger.info(f"processing new (poll.poll) notifications: {notifications}")
            if any(
                notification[0] == quit_signaling_in.fileno()
                for notification in notifications
            ):
                logger.info(
                    "detected command for graceful shutdown -> ending route reflection thread"
                )
                break  # something came from quit signaling pipe -> need to end listening to netlink and stop

            if notifications:
                logger.debug("loading ip address replace mapping")
                # quick and dirty solution how to replace ip address in learned routes from BGP/OSPF,
                # it is needed due to using GRE tunnel (LCP hack) that have different ip address to the wireguard
                # tunnel addresses and we want to use wg tunnel addresses for vpp route installation (so that dataplane
                # won't go through GRE tunnel that is LCP hack for controlplane)
                # FIXME this should be configurable from Vrouter client
                ip_address_replace_mapping = _get_ip_address_replace_mapping()
                logger.debug("retrieving netlink data")
                _handle_netlink_messages(
                    ipr.get(),
                    added_routes,
                    papi_server_host,
                    papi_server_port,
                    ip_address_replace_mapping,
                )


def _get_ip_address_replace_mapping():
    ip_address_replace_mapping = {}
    try:
        with open("/rr-ip-replace.txt") as input_file:
            for line in input_file:
                old_ip, new_ip = line.partition("=>")[::2]
                ip_address_replace_mapping[old_ip.strip()] = new_ip.strip()
    except FileNotFoundError:
        logger.debug("input file for ip_address_replace_mapping not present")

    logger.debug("ip_address_replace_mapping: " + str(ip_address_replace_mapping))
    return ip_address_replace_mapping


def _handle_netlink_messages(
    messages,
    added_routes,
    papi_server_host,
    papi_server_port,
    ip_address_replace_mapping,
):
    for message in messages:
        logger.debug(f"got netlink message: {message}")
        if message["event"] in ["RTM_NEWROUTE", "RTM_DELROUTE"] and message[
            "proto"
        ] in [int(Proto.BGP), int(Proto.OSPF)]:
            route = _get_route(message, ip_address_replace_mapping)
            route_key = route.destination_network
            try:
                with ExtendedVPPAPIClient(
                    server_host=papi_server_host, server_port=papi_server_port
                ) as client:
                    if message["event"] == "RTM_NEWROUTE":
                        if added_routes.get(route_key):
                            logger.info(
                                f"deleting previous route due to update: {added_routes.get(route_key)}"
                            )
                            reply = client.delete_configuration(
                                added_routes.get(route_key)
                            )
                            if (
                                not reply.vpp_apply_success
                                or not reply.processing_error == ""
                            ):
                                logger.error(
                                    f"couldn't delete previous route(update) {added_routes.get(route_key)}"
                                )
                            del added_routes[route_key]

                        logger.info(f"adding new route {route}")
                        reply = client.add_configuration(route)
                        if (
                            not reply.vpp_apply_success
                            or not reply.all_added_items_applied_to_vpp
                            or not reply.processing_error == ""
                        ):
                            logger.error(f"couldn't add new route route {route}")
                        added_routes[route_key] = route
                    elif message["event"] == "RTM_DELROUTE":
                        logger.info(f"deleting previous route {route}")
                        reply = client.delete_configuration(route)
                        if (
                            not reply.vpp_apply_success
                            or not reply.processing_error == ""
                        ):
                            logger.error(f"couldn't delete previous route {route}")
                        del added_routes[route_key]
            except Exception:
                logger.exception(
                    f"can't create/delete route from route reflector (route={route})"
                )


def _get_route(netlink_message, ip_address_replace_mapping):
    # extract some common data from netlink message
    logger.debug("extracting info from message")
    dest_net = (
        f"{netlink_message.get_attr('RTA_DST')}/{netlink_message['dst_len']}"
        if netlink_message.get_attr("RTA_DST")
        else "0.0.0.0/0"
    )
    priority = (
        netlink_message.get_attr("RTA_PRIORITY")
        if netlink_message.get_attr("RTA_PRIORITY")
        else 1
    )

    # single output path
    if netlink_message.get_attr("RTA_MULTIPATH") is None:
        gw_addr = (
            netlink_message.get_attr("RTA_GATEWAY")
            if netlink_message.get_attr("RTA_GATEWAY") is not None
            else ""
        )
        out_interface_name = _get_output_interface_name(
            netlink_message.get_attr("RTA_OIF")
        )

        # reflect route change (send route change to PAPI++ server)
        # Requirement: name of interface must be the same as logical name in PAPI++ server
        return models.RouteConfigurationItem(
            destination_network=_ip_address_replace(
                dest_net, ip_address_replace_mapping
            ),
            next_hop_address=_ip_address_replace(gw_addr, ip_address_replace_mapping),
            outgoing_interface=out_interface_name,
            weight=priority,
        )

    # multiple output paths
    route = models.RouteConfigurationItem(
        destination_network=_ip_address_replace(dest_net, ip_address_replace_mapping),
        multi_output_paths=[],
    )
    for multipath in netlink_message.get_attr("RTA_MULTIPATH"):
        gw_addr = (
            multipath.get_attr("RTA_GATEWAY")
            if multipath.get_attr("RTA_GATEWAY") is not None
            else ""
        )
        out_interface_name = _get_output_interface_name(multipath["oif"])

        # reflect route change (send route change to PAPI++ server)
        # Requirement: name of interface must be the same as logical name in PAPI++ server
        route.multi_output_paths.append(
            models.RouteOutputPath(
                next_hop_address=_ip_address_replace(
                    gw_addr, ip_address_replace_mapping
                ),
                outgoing_interface=out_interface_name,
                weight=priority,
            )
        )
    return route


def _ip_address_replace(
    ip_or_network: str, ip_address_replace_mapping: dict[str, str]
) -> str:
    if ip_address_replace_mapping.get(ip_or_network):
        return ip_address_replace_mapping.get(
            ip_or_network
        )  # ip address that needs replacing
    if "/" in ip_or_network:  # network
        split = ip_or_network.split("/", 1)
        ip = split[0]
        mask = split[1]
        if ip_address_replace_mapping.get(ip):
            return (
                ip_address_replace_mapping.get(ip) + "/" + mask
            )  # network that needs its ip part to be replaced
    return ip_or_network


def _get_output_interface_name(netlink_oif_id):
    out_interface_name = ""  # no output interface
    if netlink_oif_id is not None:
        try:
            with IPRoute(
                nlm_generator=True
            ) as ipr2:  # if using IPRoute used for notification, it gets stucked
                link = ipr2.get_links(netlink_oif_id)
                out_interface_name = link[0].get_attr("IFLA_IFNAME")
        except Exception:
            logger.exception(
                f"can't get output interface name of netlink interface with id {netlink_oif_id}"
            )
    return out_interface_name


def _signal_based_wait():
    exit_later = True

    def exit_gracefully(*args):
        nonlocal exit_later
        exit_later = False

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    while exit_later:
        time.sleep(1)


if (
    __name__ == "__main__"
):  # this module is library, run as script for development purposes
    graceful_shutdown_callback = start_route_reflector_in_background()
    _signal_based_wait()
    graceful_shutdown_callback()
