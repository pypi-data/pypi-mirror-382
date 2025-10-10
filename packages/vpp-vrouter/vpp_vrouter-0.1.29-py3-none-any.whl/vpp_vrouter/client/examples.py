"""
Examples of client usage.
"""

import ipaddress
import subprocess
import time
from pprint import pprint
from threading import Thread

from vpp_vrouter.client import ExtendedVPPAPIClient, BasicVPPAPIClient
from vpp_vrouter.common import models
from vpp_vrouter.common.models import DHCPConfigurationItem


def simple_example():
    """The most simple configuration using the client"""

    # New Python API for configuring VPP
    with ExtendedVPPAPIClient() as client:
        # create route in VPP
        reply = client.add_configuration(
            # adding configuration in wrong order just to see if dependencies work
            models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                next_hop_address="192.0.3.1",
                outgoing_interface="my-tap",
                # referencing interface that is not yet configured -> postponed configuration
            )
        )
        pprint(reply)

        # create interface in VPP
        reply = client.add_configuration(
            models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"], mtu=1500
            )
        )
        pprint(reply)

    # Python VPP API distributed with VPP (non-extended/original PAPI)
    with BasicVPPAPIClient() as client:
        pass  # commented out due to the serialization problems from response (see BasicVPPAPIClient documentation)
        # rv = client.tap_create_v2()
        # tap_sw_index = rv[3]  # rv.sw_if_index
        # pprint(rv)
        #
        # rv = client.sw_interface_set_flags(
        #     sw_if_index=tap_sw_index,
        #     flags=1  # VppEnum.vl_api_if_status_flags_t.IF_STATUS_API_FLAG_LINK_UP
        # )
        # pprint(rv)
        #
        # fibpaths = None
        # prefix_addr = IPv4Network('10.1.3.0/24')
        # next_hop_addr = IPv4Address('192.0.3.1')
        # rv = client.ip_route_add_del(
        #     is_add=1,
        #     is_multipath=0,
        #     route={'table_id': 0,
        #            'prefix': prefix_addr,
        #            # 'src': self.src,
        #            'n_paths': 1,
        #            'paths': [VppRoutePath(next_hop_addr, tap_sw_index).encode()],
        #            # 0xffffffff for no interface sw index
        #            },
        # )
        #
        # pprint(rv)
        #
        # for intf in client.sw_interface_dump():
        #     print(intf)
        #     # print(intf.interface_name)


def duplicated_config_example():
    """Example of configuring the same thing twice. The requested behaviour should be that the second call should
    return error."""

    with ExtendedVPPAPIClient() as client:
        interface_config = models.InterfaceConfigurationItem(
            name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
        )
        reply = client.add_configuration(interface_config)
        pprint(reply)
        assert reply.vpp_apply_success
        assert len(reply.vpp_apply_attempted_items) > 0
        assert not reply.processing_error

        reply = client.add_configuration(interface_config)
        pprint(reply)
        assert reply.processing_error
        assert reply.added_items[0].config == interface_config


def get_current_config_example():
    """Example of retrieving the inner configuration state of the server.

    The server uses this configuration as source of truth, that means that in any case of configuration difference
    between VPP and server, the server uses this state to overwrite the VPP configuration.
    """

    with ExtendedVPPAPIClient() as client:
        reply = client.add_configuration(
            # adding configuration in wrong order just to see if dependencies work
            models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                next_hop_address="192.0.3.1",
                outgoing_interface="my-tap",
            )
        )
        pprint(reply)
        reply = client.get_configuration()
        pprint(reply)


def wait_with_context_example():
    """Example of configuration from different clients/docker containers/nodes (here just Threads) and how to wait
    for the configuration to be ready."""

    # it is used for logical grouping of configuration here (grouping on client's user side),
    # but could hold any context information
    context = "1"

    def add_route(delay):
        time.sleep(delay)
        print("adding route")
        with ExtendedVPPAPIClient() as client:
            reply = client.add_configuration(
                # adding configuration in wrong order just to see if dependencies work
                models.RouteConfigurationItem(
                    destination_network="10.1.3.0/24",
                    next_hop_address="192.0.3.1",
                    outgoing_interface="my-tap",
                ),
                context=context,
            )
            pprint(reply)
            time.sleep(
                5
            )  # checking that running multiple clients from multiple threads doesn't raise Error
        pass

    def add_interface(delay):
        time.sleep(delay)
        print("adding interface")
        with ExtendedVPPAPIClient() as client:
            reply = client.add_configuration(
                models.InterfaceConfigurationItem(
                    name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
                ),
                context=context,
            )
            pprint(reply)
            time.sleep(
                5
            )  # checking that running multiple clients from multiple threads doesn't raise Error

    def wait_for_config(delay):
        time.sleep(delay)
        print("waiting for config")
        with ExtendedVPPAPIClient() as client:

            def check_application_to_vpp(config_item_details) -> bool:
                applied_config_items_with_right_context = [
                    detail
                    for detail in config_item_details
                    if detail.metadata.get("context") == context
                    and detail.state == models.State.APPLIED
                ]
                # NOTE: filter by context is not enough as waiting thread start sooner than all context configuration
                # is sent to vpp_client -> need to have more knowledge to wait properly (config item count in this case)
                return len(applied_config_items_with_right_context) == 2

            client.wait_for_configuration(configuration_check=check_application_to_vpp)
            print("config is applied in VPP")
        pass

    threads = [
        Thread(name="Thread-wait", target=wait_for_config, args=(1,)),
        Thread(name="Thread-route", target=add_route, args=(2,)),
        Thread(name="Thread-interface", target=add_interface, args=(3,)),
    ]
    try:
        for t in threads:
            t.start()
    except Exception as e:
        print("Error: unable to start thread due to ", e)
    try:
        for t in threads:
            t.join()
    except Exception as e:
        print("Error: unable to join thread due to ", e)


def route_delete_example():
    """Simple example how to delete previously added configuration."""

    with ExtendedVPPAPIClient() as client:
        interface_config = models.InterfaceConfigurationItem(
            name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
        )
        route_config = models.RouteConfigurationItem(
            destination_network="10.1.3.0/24",
            next_hop_address="192.0.3.1",
            outgoing_interface="my-tap",
        )
        reply = client.add_configuration(interface_config, route_config)
        pprint(reply)
        reply = client.delete_configuration(route_config)
        pprint(reply)


def acl_example():
    """Example of how to configure ACL in VPP. (The ACL configuration is done just to expose most of the possibilities
    what to configure and not as meaningful configuration for some topology use case)"""

    with ExtendedVPPAPIClient() as client:
        # create ACL (with linked interfaces)
        reply = client.add_configuration(
            models.InterfaceConfigurationItem(
                name="acl-input-tap", enabled=True, ip_addresses=["10.100.1.1/24"]
            ),
            models.InterfaceConfigurationItem(
                name="acl-output-tap", enabled=True, ip_addresses=["10.200.1.1/24"]
            ),
            models.ACLConfigurationItem(
                name="ACL1",
                ingress=["acl-input-tap"],
                egress=["acl-output-tap"],
                rules=[
                    models.ACLRuleConfigurationItem(
                        action=models.ACLAction.PERMIT,
                        refinement=models.IPSpecification(
                            addresses=models.IPAddresses(
                                destination_network=ipaddress.IPv4Network(
                                    "10.200.1.0/24"
                                ),
                                source_network=ipaddress.IPv4Network("10.100.1.0/24"),
                            ),
                            protocol=models.ICMPProtocol(
                                icmp_code_range=models.ICMPRange(
                                    first=0, last=8
                                )  # includes echo and echo reply
                            ),
                        ),
                    ),
                    models.ACLRuleConfigurationItem(  # Deny all other
                        action=models.ACLAction.DENY
                    ),
                ],
            ),
        )
        pprint(reply)

        # delete existing ACL
        reply = client.get_configuration()
        acl_config = [
            item.config
            for item in reply.items
            if isinstance(item.config, models.ACLConfigurationItem)
            and item.config.name == "ACL1"
        ][0]
        reply = client.delete_configuration(acl_config)
        pprint(reply)


def nat_example():
    """Example of how to configure NAT(Network Address Translation) in VPP. (The NAT configuration is done just to
    expose most of the possibilities what to configure and not as meaningful configuration for some topology use
    case)"""

    with ExtendedVPPAPIClient() as client:
        tap_out_config = models.InterfaceConfigurationItem(
            name="tap-nat-out", enabled=True, ip_addresses=["10.100.1.1/24"]
        )
        tap_in_config = models.InterfaceConfigurationItem(
            name="tap-nat-in", enabled=True, ip_addresses=["10.200.1.1/24"]
        )
        tap_out_nat_config = models.Nat44InterfaceConfigurationItem(
            name=tap_out_config.name, nat_outside=True
        )
        tap_in_nat_config = models.Nat44InterfaceConfigurationItem(
            name=tap_in_config.name, nat_inside=True
        )
        tcp_service_config = models.DNat44ConfigurationItem(
            label="tcp-service",
            static_mappings=[
                models.StaticMapping(
                    external_ip=ipaddress.IPv4Address("80.80.80.80"),
                    external_port=8888,
                    protocol=models.ProtocolInNAT.TCP,
                    local_ips=[
                        models.LocalIP(
                            local_ip=ipaddress.IPv4Interface(
                                tap_in_config.ip_addresses[0]
                            ).ip,
                            local_port=8000,
                        )
                    ],
                )
            ],
        )
        reply = client.add_configuration(
            tcp_service_config,
            tap_out_config,
            tap_in_config,
            tap_out_nat_config,
            tap_in_nat_config,
        )
        pprint(reply)

        reply = client.delete_configuration(
            tcp_service_config, tap_in_nat_config, tap_out_nat_config
        )
        pprint(reply)


def wireguard_example():
    """Example of how to configure Wireguard in VPP. (The wireguard configuration is done just to expose most
    of the possibilities what to configure and not as meaningful configuration for some topology use case)
    """

    with ExtendedVPPAPIClient() as client:
        wireguard_interface_config = models.InterfaceConfigurationItem(
            name="my-wg",
            enabled=True,
            ip_addresses=["10.100.1.1/24"],
            type=models.InterfaceType.WIREGUARD_TUNNEL,
            mtu=1420,  # leaving some room for encryption encapsulation so that packet don't break into segments
            link=models.WireguardInterfaceLink(
                private_key="cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=",  # encoded in base64
                port=50000,
                src_addr=ipaddress.IPv4Address("10.100.0.1"),
            ),
        )
        wireguard_peer_config = models.WireguardPeerConfigurationItem(
            public_key="hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=",  # encoded in base64
            port=50000,
            endpoint=ipaddress.IPv4Address("10.100.0.2"),
            allowed_ips=["0.0.0.0/0"],
            wg_if_name=wireguard_interface_config.name,
        )
        reply = client.add_configuration(
            wireguard_interface_config, wireguard_peer_config
        )
        pprint(reply)

        reply = client.delete_configuration(
            wireguard_interface_config, wireguard_peer_config
        )
        pprint(reply)


def vpp_stats_example():
    """Example using transient VPPStatsQuery based stats API."""

    with ExtendedVPPAPIClient() as client:
        # Collect stats for specific interfaces
        query = models.VPPStatsQuery(
            interface_names=["wg0", "vpp-wan"],
            include_error_counters=True,
            debug=True,
        )
        print("Collecting interface-specific VPP statistics for wg0 and vpp-wan...")
        reply = client.get_vpp_stats(query)
        if reply.success:
            for if_name in ["wg0", "vpp-wan"]:
                counters = reply.summarize_interface(if_name)
                if counters:
                    print(f"{if_name}: {counters}")
        else:
            print(f"Failed to collect interface stats: {reply.error}")

        # General stats collection with patterns
        general_query = models.VPPStatsQuery(
            patterns=["/if/rx", "/if/tx", "/if/drops"],
            include_error_counters=False,
            debug=True,
        )
        print("\nCollecting general VPP statistics...")
        general_reply = client.get_vpp_stats(general_query)
        if general_reply.success:
            print(f"Collected {len(general_reply.entries)} entries")
            sample = general_reply.entries[:5]
            for e in sample:
                print(f"  {e.name} ({e.type})")
        else:
            print(f"Failed to collect general stats: {general_reply.error}")


def frr_example():
    """Example of how to configure FRR running inside another docker.

    This is not VPP-related configuration, but is needed when we want to configure the topologies with FRR by using
    the client API."""

    # Note: connection to FRR must be configured so this examples work (launch PAPI++ server with correctly filled
    # --frr_agent_host and --frr_agent_port parameters referring to running FRR agent (in docker container) )
    with ExtendedVPPAPIClient() as client:
        # PAPI++ server gets the default initial FRR configuration at startup -> ideal start for FRR config addition
        frr_init_config = [
            config_detail.config
            for config_detail in client.get_configuration().items
            if isinstance(config_detail.config, models.FRRConfigurationItem)
        ][0]
        pprint(frr_init_config)

        # appending some bgp configuration to initial FRR config
        # (FRR config is updated, but that means just means delete of old config and add of new one. In case of FRR,
        # the delete does nothing because FRR need to have always some configuration. That means that only addition of
        # FRR configuration matters.)
        append_to_frr_config = (
            """ 
router bgp 100
 !
 address-family ipv4 unicast
  distance bgp 100 100 100
 exit-address-family
exit
!       
        """.strip(
                "\n "
            )
            + "\n"
        )
        reply = client.update_configuration(
            frr_init_config,
            models.FRRConfigurationItem(
                config=frr_init_config.config + append_to_frr_config
            ),
        )
        pprint(reply, width=260)


def failover_notification():
    """Example of how to use the existing client API to detect link failover.

    The solution is based on USDN "Failover" use case topology and the link failure is detected by OSPF agent running
    in FRR. The OSPF/FRR reacts to this information by replacing routes from failed link to routes to working link.
    The routes are then configured by small python program inside FRR docker container into VPP. The configuration is
    done as if another client connected to server and configured routes in VPP. So the detection is basically checking
    the route configuration(using get_configuration call in API) in some intervals and checking it for linked
    interfaces. When the watched changes occur, then failover happend. This is shown in this example. Of course
    the watcher must have knowledge about the IP addresses of the 2 redundant links that it is watching.
    """

    # initial topology
    # (2 data interfaces representing 2 redundant links into core network -> failover means switching between them)
    name_of_data_interface1 = "data-interface1"
    name_of_data_interface2 = "data-interface2"
    with ExtendedVPPAPIClient() as client:
        client.add_configuration(
            models.InterfaceConfigurationItem(
                name=name_of_data_interface1, enabled=True, ip_addresses=["10.0.1.1/24"]
            ),
            models.InterfaceConfigurationItem(
                name=name_of_data_interface2, enabled=True, ip_addresses=["10.0.2.1/24"]
            ),
            models.RouteConfigurationItem(
                destination_network="10.100.200.0/24",
                next_hop_address="10.0.1.2",
                outgoing_interface=name_of_data_interface1,
            ),
        )

    # define 2 threads, one simulating switching between data links in case of failover and other the client being
    # notified about it:
    def failover_switcher(delay):
        """Simulates FRR's OSPF link down detection.

        When data link is down, the OSPF will learn new routes that will reroute traffic to the other data link that is
        still functional and remove routes routing packets to data link that is down."""
        time.sleep(delay)
        print("failover switcher started")

        def failover_to_data_link2(client):
            # remove routes to link1
            client.delete_configuration(
                models.RouteConfigurationItem(
                    destination_network="10.100.200.0/24",
                    next_hop_address="10.0.1.2",
                    outgoing_interface=name_of_data_interface1,
                )
            )
            # replace old routes by adding the same routes, but to link2
            client.add_configuration(
                models.RouteConfigurationItem(
                    destination_network="10.100.200.0/24",
                    next_hop_address="10.0.2.2",
                    outgoing_interface=name_of_data_interface2,
                )
            )

        def failover_to_data_link1(client):
            # remove routes to link2
            client.delete_configuration(
                models.RouteConfigurationItem(
                    destination_network="10.100.200.0/24",
                    next_hop_address="10.0.2.2",
                    outgoing_interface=name_of_data_interface2,
                )
            )
            # replace old routes by adding the same routes, but to link1
            client.add_configuration(
                models.RouteConfigurationItem(
                    destination_network="10.100.200.0/24",
                    next_hop_address="10.0.1.2",
                    outgoing_interface=name_of_data_interface1,
                )
            )

        with ExtendedVPPAPIClient() as client:
            time.sleep(5)
            failover_to_data_link2(client)
            time.sleep(5)
            failover_to_data_link1(client)

    def notified_client(delay):
        """Client that will be "notified" about the failover.

        The notification means to actively check for certain route changes in PAPI++ server configuration
        """
        time.sleep(delay)
        print("notified client started")

        def wait_for_failover(client, link1, link2):
            initial_data_link = [
                detail.config.outgoing_interface
                for detail in client.get_configuration().items
                if detail.state == models.State.APPLIED
                and isinstance(detail.config, models.RouteConfigurationItem)
                and detail.config.outgoing_interface in [link1, link2]
            ][0]

            def check_for_failover(config_item_details) -> bool:
                actual_data_link = [
                    detail.config.outgoing_interface
                    for detail in config_item_details
                    if detail.state == models.State.APPLIED
                    and isinstance(detail.config, models.RouteConfigurationItem)
                    and detail.config.outgoing_interface in [link1, link2]
                ][0]
                return initial_data_link != actual_data_link

            client.wait_for_configuration(configuration_check=check_for_failover)
            if initial_data_link == link1:
                return link1, link2
            else:
                return link2, link1

        with ExtendedVPPAPIClient() as client:
            failing_link, new_link = wait_for_failover(
                client, name_of_data_interface1, name_of_data_interface2
            )
            print(f"detected failover from {failing_link} to {new_link}")
            failing_link, new_link = wait_for_failover(
                client, name_of_data_interface1, name_of_data_interface2
            )
            print(f"detected failover from {failing_link} to {new_link}")

    threads = [
        Thread(name="Thread-notified-client", target=notified_client, args=(1,)),
        Thread(name="Thread-failover-switcher", target=failover_switcher, args=(2,)),
    ]
    try:
        for t in threads:
            t.start()
    except Exception as e:
        print("Error: unable to start thread due to ", e)
    try:
        for t in threads:
            t.join()
    except Exception as e:
        print("Error: unable to join thread due to ", e)


def lcp_example():
    """Example of usage of LCP API in VPP"""

    with ExtendedVPPAPIClient() as client:
        lcp_globals_config = models.LCPGlobalsConfigurationItem(
            default_namespace="",
            lcp_sync=True,  # Enables copying of changes made in VPP into their Linux counterpart
            # sub-interface creation in VPP automatically creates a Linux Interface Pair(LIP) and its companion Linux
            # network interface
            lcp_auto_subint=True,
        )
        # source interface that LCP will mirrot into linux network namespace
        interface_config = models.InterfaceConfigurationItem(
            name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
        )
        lcp_pair_config = models.LCPPairConfigurationItem(
            interface=interface_config.name,
            mirror_interface_host_name=f"host-{interface_config.name}",
            mirror_interface_type=models.LCPHostInterfaceTypeEnum.TAP,
            host_namespace="",  # current/default linux namespace
        )
        reply = client.add_configuration(
            lcp_globals_config, interface_config, lcp_pair_config
        )
        pprint(reply)

        reply = client.delete_configuration(
            lcp_globals_config, interface_config, lcp_pair_config
        )
        pprint(reply)


def update_dpdk_interface():
    """Example showing how to update state and ip address of DPDK interface(interface not created by API, but created
    automatically from VPP's startup configuration)."""

    # Note: for example to work, you need to configure VPP with one dpdk interface in startup.conf and name it
    # "my-dpdk-interface" (see ../dev-setup/startup.conf)
    with ExtendedVPPAPIClient() as client:
        dpdk_init_config = [
            item.config
            for item in client.get_configuration().items
            if item.config.name == "my-dpdk-interface"
        ][0]
        reply = client.update_configuration(
            dpdk_init_config,
            models.InterfaceConfigurationItem(
                name=dpdk_init_config.name,
                type=dpdk_init_config.type,
                enabled=True,
                ip_addresses=["10.0.1.0/24"],
                mtu=8500,
            ),
        )
        pprint(reply)


def create_loop_interface():
    with ExtendedVPPAPIClient() as client:
        loop_config = models.InterfaceConfigurationItem(
            name="my-loop",
            type=models.InterfaceType.SOFTWARE_LOOPBACK,
            enabled=True,
            ip_addresses=["10.0.2.0/24"],
            mtu=1200,
        )
        reply = client.add_configuration(loop_config)
        pprint(reply)

        reply = client.delete_configuration(loop_config)
        pprint(reply)


def packet_capturing_example():
    with ExtendedVPPAPIClient() as client:
        # configure packet capturing and interface for traffic flow
        tap_tunnel_config = models.InterfaceConfigurationItem(
            name="my-tap",
            enabled=True,
            ip_addresses=["10.0.1.1/24"],
        )
        pcap_config = models.RunningPacketCapture(
            output_file_prefix="example",
            max_packets_to_capture="10",
            capture_rx_packets=True,
            capture_tx_packets=True,
            capture_dropped_packets=True,
            capture_only_from_interface=tap_tunnel_config.name,
            # or models.PCAP_ANY_INTERFACE to capture from all interfaces
            capture_by_matching_rules=[
                models.L2PacketMatchingRule(
                    # src_physical_address="",  # i.e. "02:fe:c2:6c:9d:bb" or "" to ignore
                    # dest_physical_address="",  # i.e. "02:fe:56:ac:8f:8a" or "" to ignore
                    protocol=0x800
                    # L2's IP4 (https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def)
                    # or don't do capture by protocol by using models.NO_PROTOCOL
                ),
                models.L3PacketMatchingRule(
                    # src_ipv4_address="",  # i.e. "10.0.1.2" or "" to ignore
                    dest_ipv4_address=tap_tunnel_config.ip_addresses[0][
                        :-3
                    ],  # i.e. "10.0.1.1" or "" to ignore
                    protocol=1,  # L3's ICMP (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
                    # or don't do capture by protocol by using models.NO_PROTOCOL
                ),
            ],
        )

        # start capturing
        reply = client.add_configuration(tap_tunnel_config, pcap_config)
        pprint(reply)

        ####
        # Warning: User interaction needed!
        # Stop here (debug breakpoint) and send manually some packets for capturing in VPP and continue running example
        # (Note: for noninteractive example check tests in ../tests/test.py, class PacketCapturingTestCases)
        ####

        # stop capturing (and store result to file)
        reply = client.delete_configuration(tap_tunnel_config, pcap_config)
        pprint(reply)
        if reply.vpp_apply_success and not reply.processing_error:
            capture_reply = [
                reply.metadata
                for reply in reply.vpp_apply_attempted_items
                if isinstance(reply.config, models.RunningPacketCapture)
            ][0]
            if not capture_reply["count_of_captured_packets"]:
                print("Nothing captured! No capture file written")
            else:
                print(
                    f'Captured {capture_reply["count_of_captured_packets"]} packets! Pcap file is at '
                    f'"{capture_reply["packet_capture_output_file"]}".'
                )


def from_docker_to_host_example():
    """Example how to configure traffic to go from local docker container to local host.

    This is needed for FRR to RouteReflector path."""

    # requirements:
    # install ip tool (for ubuntu: sudo apt install -y iproute2)

    # Note: if missing "vpp:test" image then build with 'make vpp-test-image' in root of this repo
    # Note2: any ubuntu 20.04 image with ip tool will do if you don't want to build vpp (it is used here because tests
    # use it so it is ready locally)
    subprocess.check_call(
        "docker run --rm --cap-add=NET_ADMIN --name test vpp:test sleep 1000s &",
        shell=True,
    )

    # configuration example
    with ExtendedVPPAPIClient() as client:
        veth_tunnel_config = models.LinuxDockerVethTunnelConfigurationItem(
            docker_container_name="test",
            host_interface_name="my-host-veth",
            docker_interface_name="my-veth",
            host_interface_ip_addresses=["10.0.1.1/24"],
            docker_interface_ip_addresses=["10.0.1.2/24"],
        )

        # add veth tunnel
        reply = client.add_configuration(veth_tunnel_config)
        pprint(reply)

        # make some pings through veth tunnel
        pprint(subprocess.check_output("ping -c 3 10.0.1.2", shell=True).decode())

        # remove veth tunnel
        reply = client.delete_configuration(veth_tunnel_config)
        pprint(reply)

    # cleanup
    subprocess.check_call("docker rm -f $(docker ps -q -f name=test)", shell=True)


def linux_route_example():
    """Example how to configure linux route.

    This is needed for FRR to RouteReflector path."""

    # Note: if missing "vpp:test" image then build with 'make vpp-test-image' in root of this repo
    # Note2: any ubuntu 20.04 image with ip tool will do if you don't want to build vpp (it is used here because tests
    # use it so it is ready locally)
    subprocess.check_call(
        "docker run --rm --cap-add=NET_ADMIN --name test vpp:test sleep 1000s &",
        shell=True,
    )

    with ExtendedVPPAPIClient() as client:
        linux_route_config = models.LinuxRouteConfigurationItem(
            docker_container_name="test",  # use empty string for linux host
            destination_network="10.0.1.0/24",
            outgoing_interface="eth0",
        )
        # add route
        reply = client.add_configuration(linux_route_config)
        pprint(reply)

        # check route addition
        print("Routes from docker container:")
        pprint(
            subprocess.check_output(
                "docker exec test ip route show", shell=True
            ).decode()
        )

        # remote route
        reply = client.delete_configuration(linux_route_config)
        pprint(reply)

        # check route removal
        print("Routes from docker container:")
        pprint(
            subprocess.check_output(
                "docker exec test ip route show", shell=True
            ).decode()
        )

    # cleanup
    subprocess.check_call("docker rm -f $(docker ps -q -f name=test)", shell=True)


def wireguard_state_update_detection_example():
    """Example of how to detect changed state of Wireguard interface inside VPP.

    This example can be used to monitor Wireguard interface state in VPP and react for cases when it disables itself
    (some wireguard failure unrelated to DPDK interface failure that is detected by OSPF in failover use case)
    """
    with ExtendedVPPAPIClient() as client:
        # setup wireguard
        wireguard_interface_config = models.InterfaceConfigurationItem(
            name="my-wg",
            enabled=True,
            ip_addresses=["10.100.1.1/24"],
            type=models.InterfaceType.WIREGUARD_TUNNEL,
            mtu=1420,  # leaving some room for encryption encapsulation so that packet don't break into segments
            link=models.WireguardInterfaceLink(
                private_key="cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=",  # encoded in base64
                port=50000,
                src_addr=ipaddress.IPv4Address("10.100.0.1"),
            ),
        )
        wireguard_peer_config = models.WireguardPeerConfigurationItem(
            public_key="hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=",  # encoded in base64
            port=50000,
            endpoint=ipaddress.IPv4Address("10.100.0.2"),
            allowed_ips=["0.0.0.0/0"],
            wg_if_name=wireguard_interface_config.name,
        )
        reply = client.add_configuration(
            wireguard_interface_config, wireguard_peer_config
        )
        pprint(reply)

        # watch loop for interface state
        counter = 0
        print(
            "starting loop to get the actual state of all created wireguard interfaces:"
        )
        while True:
            # Note: While running this loop, change the state of interface from VPP CLI (i.e.
            # "set interface state wg0 down" or "set interface state wg0 up")
            counter += 1
            # NOTE: don't forget the sync_with_vpp=True as it is responsible for sync with vpp just before returning
            # server configuration state
            for item in client.get_configuration(sync_with_vpp=True).items:
                if (
                    isinstance(item.config, models.InterfaceConfigurationItem)
                    and isinstance(item.config.link, models.WireguardInterfaceLink)
                    and isinstance(
                        item.metadata[models.VPP_DUMP_KEY], models.SWInterfaceDetail
                    )
                ):
                    interface_detail = item.metadata[models.VPP_DUMP_KEY]
                    print(
                        f"loop run {counter} - wireguard interface {interface_detail.interface_name} has admin state "
                        f"{'UP' if interface_detail.is_admin_state_up() else 'DOWN'} and link state "
                        f"{'UP' if interface_detail.is_link_state_up() else 'DOWN'}"
                    )
                    # NOTE: remember that admin state is user-preferred configuration and link state is state of real
                    # link connection. By using VPP CLI to get interface down ("set interface state wg0 down") you set
                    # user/admin state and according to that also link state will be configured. So it seems as these
                    # states are interchangable, but for unexpected failure check for link state as that is the real
                    # link state.
            time.sleep(1)


def dhcp_example():
    """Example of how to configure DHCP running inside another docker.

    This is not VPP-related configuration, but is needed when we want to configure the topologies with DHCP by using
    the client API."""

    from client import ExtendedVPPAPIClient

    # Note: connection to DHCP must be configured so this examples work (launch PAPI++ server with correctly filled
    # --dhcp_socket parameters referring to DHCP control socket that is exposed from running DHCP docker container
    # by volume mounting)
    # for working example out-of-box see integration test in class DHCPTestCases (<repo root>/tests/test.py)
    with ExtendedVPPAPIClient() as client:
        dhcp_config = """{
    "Dhcp4": {
        "subnet4": [
            {
                "subnet": "10.0.1.0/24",
                "pools": [
                    {
                        "pool": "10.0.1.10-10.0.1.250"
                    }
                ],
                "interface": "lo",
                "reservations-global": false,
                "reservations-in-subnet": true,
                "reservations-out-of-pool": false,
                "reservations": [            
                    {
                        "hw-address": "54:bf:64:d4:f3:45",
                        "ip-address": "10.0.1.100",
                        "hostname": "usdn-client-01"
                    }
                ]
            }
        ],
        "interfaces-config": {
            "interfaces": [
                "lo"
            ],
            "dhcp-socket-type": "raw",
            "service-sockets-max-retries": 5,
            "service-sockets-require-all": true
        },
        "control-socket": {
            "socket-type": "unix",
            "socket-name": "/run/kea/control_socket_4"
        },
        "renew-timer": 1000,
        "rebind-timer": 2000,
        "valid-lifetime": 4000,
        "loggers": [
            {
                "name": "kea-dhcp4",
                "output_options": [
                    {
                        "output": "stdout"
                    }
                ],
                "severity": "DEBUG",
                "debuglevel": 7
            }
        ],
        "lease-database": {
            "type": "memfile",
            "persist": true,
            "name": "/var/lib/kea/dhcp4.leases"
        }
    }
}
        """

        reply = client.add_configuration(DHCPConfigurationItem(config=dhcp_config))
        print(reply)


if __name__ == "__main__":
    # all examples except one is commented out, change commenting sign to enable one example that
    # you are interested in

    # simple_example()
    # duplicated_config_example()
    # get_current_config_example()
    # wait_with_context_example()
    # route_delete_example()
    # acl_example()
    # nat_example()
    # wireguard_example()
    # frr_example()
    # failover_notification()
    # lcp_example()
    # update_dpdk_interface()
    # create_loop_interface()
    # packet_capturing_example()
    # from_docker_to_host_example()
    # linux_route_example()
    # wireguard_state_update_detection_example()
    #dhcp_example()
    vpp_stats_example() 

    
