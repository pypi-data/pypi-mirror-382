import ipaddress
import time
from pprint import pprint
from threading import Thread

from vpp_vrouter.client import ExtendedVPPAPIClient, BasicVPPAPIClient
from vpp_vrouter.common import models


def simple_example():
    with ExtendedVPPAPIClient() as client:
        # reply = client.add_configuration(
        #     # adding configuration in wrong order just to see if dependencies work
        #     models.RouteConfigurationItem(
        #         destination_network="10.1.3.0/24",
        #         next_hop_address="192.0.3.1",
        #         outgoing_interface="my-tap"
        #     )
        # )
        # pprint(reply)
        reply = client.add_configuration(
            models.InterfaceConfigurationItem(
                type=models.InterfaceType.TAP,
                name="GigabitEthernet3/0/0",
                enabled=True,
                ip_addresses=["10.100.0.1/24"],
            )
        )
        pprint(reply)

    # Python VPP API distributed with VPP (non-extended/original PAPI)
    with BasicVPPAPIClient() as client:
        pass
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

        # reply = client.delete_configuration(
        #     tcp_service_config, tap_in_nat_config, tap_out_nat_config
        # )
        # pprint(reply)


def wireguard_example():
    with ExtendedVPPAPIClient() as client:
        wireguard_interface_config = models.InterfaceConfigurationItem(
            name="my-wg",
            enabled=True,
            ip_addresses=["172.32.0.10/30"],
            type=models.InterfaceType.WIREGUARD_TUNNEL,
            link=models.WireguardInterfaceLink(
                private_key="WOysjzDd3oGVhi/FAXZTMUwFbWIb0xzjEQtQh30LhVg=",  # encoded in base64
                port=50869,
                src_addr=ipaddress.IPv4Address("10.10.1.1"),
            ),
        )
        wireguard_peer_config = models.WireguardPeerConfigurationItem(
            public_key="CV+HC1xgxWSojYJ0h8Jh1JxF7Lr3QL8WFmJjCrJzfGc=",  # encoded in base64
            port=50869,
            endpoint=ipaddress.IPv4Address("10.10.1.2"),
            allowed_ips=["0.0.0.0/0"],
            wg_if_name=wireguard_interface_config.name,
        )

        wireguard_route_config = models.RouteConfigurationItem(
            destination_network="172.32.0.9/32", outgoing_interface="my-wg"
        )
        reply = client.add_configuration(
            wireguard_interface_config, wireguard_peer_config, wireguard_route_config
        )
        print(reply)

        # reply = client.delete_configuration(wireguard_interface_config, wireguard_peer_config)
        # pprint(reply)


def frr_example():
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
            [frr_init_config],
            [
                models.FRRConfigurationItem(
                    config=frr_init_config.config + append_to_frr_config
                )
            ],
        )
        pprint(reply, width=260)


def failover_notification():
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
            print(client.get_configuration().items)
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


def update_dpdk_interface():
    """Example showing how to update state and ip address of DPDK interface(interface not created by API, but created
    automatically from VPP's startup configuration)."""

    # Note: for example to work, you need to configure VPP with one dpdk interface in startup.conf and name it
    # "my-dpdk-interface" (see ../dev-setup/startup.conf)
    with ExtendedVPPAPIClient() as client:
        dpdk_init_config = [
            item.config
            for item in client.get_configuration().items
            if item.config.name == "GigabitEthernet3/0/0"
        ][0]
        reply = client.update_configuration(
            dpdk_init_config,
            models.InterfaceConfigurationItem(
                name=dpdk_init_config.name,
                type=dpdk_init_config.type,
                enabled=True,
                ip_addresses=["10.10.1.1/24"],
            ),
        )
        pprint(reply)


if __name__ == "__main__":
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

    update_dpdk_interface()

    # wireguard_example()
    # nat_example()
