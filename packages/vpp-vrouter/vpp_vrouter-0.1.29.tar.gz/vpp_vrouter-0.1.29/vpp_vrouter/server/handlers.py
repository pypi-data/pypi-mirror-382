"""
Handlers provide configuration-item-related functionality. See models.ConfigurationItemHandler .
"""

import base64
import ipaddress
import json
import os
import re
import socket
import subprocess
import time
import traceback
from datetime import datetime
from ipaddress import ip_address
from typing import List

from Pyro5.client import Proxy
from vpp_papi import VppEnum

from vpp_vrouter.common import serializers
from vpp_vrouter.common.models import (
    ConfigurationItemHandler,
    InterfaceConfigurationItem,
    ApplyReply,
    InterfaceType,
    SW_IF_INDEX,
    SWInterfaceDetail,
    RouteConfigurationItem,
    NO_INTERFACE_SW_INDEX,
    FibPathProto,
    FibPathType,
    FibPathFlags,
    IPRouteDetail,
    RouteType,
    ACLConfigurationItem,
    ACL_INDEX,
    ACLRuleConfigurationItem,
    ACLAction,
    OtherProtocol,
    ICMPProtocol,
    TCPProtocol,
    UDPProtocol,
    NO_ACL_INDEX,
    ACLDetails,
    DNat44ConfigurationItem,
    Nat44InterfaceConfigurationItem,
    Nat44AddressPoolConfigurationItem,
    NAT44AddressDetails,
    NAT44InterfaceDetails,
    NAT44StaticMappingDetails,
    NAT44IdentityMappingDetails,
    GREInterfaceLink,
    GRELinkType,
    WireguardInterfaceLink,
    WireguardPeerConfigurationItem,
    WIREGUARD_PEER_INDEX,
    NO_WIREGUARD_PEER_INDEX,
    WireguardPeerDetail,
    FRRConfigurationItem,
    LCPGlobalsConfigurationItem,
    LCPPairConfigurationItem,
    HOST_SW_IF_INDEX,
    LCPHostInterfaceTypeEnum,
    LCPPairDetail,
    VPPConfigUpdater,
    NOT_SET_MTU,
    RunningPacketCapture,
    PCAP_ANY_INTERFACE,
    L2PacketMatchingRule,
    L3PacketMatchingRule,
    NO_PROTOCOL,
    LinuxDockerVethTunnelConfigurationItem,
    LinuxRouteConfigurationItem,
    DHCPConfigurationItem,
    KeaConfigRequest,
    KeaConfigResponse,
)
from vpp_vrouter.common.utils import get_main_logger

logger = get_main_logger()
enabled_nat44_ed = False


def enforce_enabled_nat_in_vpp(function):
    """Decorator for enforcing NAT (NAT44ed) to be enabled in VPP"""

    def wrapper(*args, **kwds):
        self = args[0]
        global enabled_nat44_ed
        if not enabled_nat44_ed:
            reply = self.vpp_client.api.nat44_ed_plugin_enable_disable(enable=1)
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error="Failed to enable endpoint dependant nat44."
                    + get_vpp_error_log_message(reply.retval),
                )
            enabled_nat44_ed = True
        return function(*args, **kwds)

    return wrapper


def validate_config_item(function):
    """Decorator for checking configuration item argument to be handled by handler that is called"""

    def wrapper(*args, **kwds):
        self = args[0]
        configuration_item = args[1]
        if not self.is_handling_configuration_item(configuration_item):
            raise ValueError(
                f"configuration item is not handled by this handler ({self.__class__.__name__})"
            )
        return function(*args, **kwds)

    return wrapper


def validate_multiple_config_items(function):
    """Decorator for checking multiple configuration item arguments to be handled by handler that is called"""

    def wrapper(*args, **kwds):
        self = args[0]
        configuration_item = args[1]
        if not self.is_handling_configuration_item(configuration_item):
            raise ValueError(
                f"first configuration item is not handled by this handler ({self.__class__.__name__})"
            )
        configuration_item = args[2]
        if not self.is_handling_configuration_item(configuration_item):
            raise ValueError(
                f"second configuration item is not handled by this handler ({self.__class__.__name__})"
            )
        return function(*args, **kwds)

    return wrapper


vpp_error_codes_to_messages = {
    -1: "Unspecified Error",
    -2: "Invalid sw_if_index",
    -3: "No such FIB  VRF ",
    -4: " No such inner FIB  VRF  ",
    -5: " No such label",
    -6: "No such entry",
    -7: "Invalid value",
    -8: "Invalid value 2",
    -9: "Unimplemented",
    -10: "Invalid sw_if_index 2",
    -11: "System call error 1",
    -12: " System call error 2",
    -13: "System call error 3",
    -14: "System call error 4",
    -15: "System call error 5",
    -16: "System call error 6",
    -17: "System call error 7",
    -18: "System call error 8",
    -19: "System call error 9",
    -20: "System call error 10",
    -30: "Feature disabled by configuration",
    -31: "Invalid registration",
    -50: "Next hop not in FIB",
    -51: "Unknown destination",
    -52: "No paths specified in route",
    -53: " Next hop not found multipath",
    -54: "No matching interface for probe",
    -55: " Invalid VLAN",
    -56: "VLAN subif already exists",
    -57: "Invalid src address",
    -58: "Invalid dst address",
    -59: "Address length mismatch ",
    -60: "Address not found for interface",
    -61: "Address not deletable  ",
    -62: "ip6 not enabled",
    -63: "No such graph node",
    -64: "No such graph node 2",
    -65: " No such table",
    -66: "No such table 2",
    -67: "No such table 3",
    -68: "Subinterface already exists",
    -69: "Subinterface creation failed ",
    -70: "Invalid memory size requested",
    -71: "Invalid interface",
    -72: "Invalid number of tags for requested operation",
    -73: " Invalid argument",
    -74: "Unexpected interface state ",
    -75: " Tunnel already exists  ",
    -76: "Invalid decapnext",
    -77: "Response not ready ",
    -78: " Not connected to the data plane ",
    -79: " Interface already exists    ",
    -80: "Operation not allowed on slave of BondEthernet",
    -81: "Value already exists",
    -82: "Source and destination are the same",
    -83: "IP6 multicast address required",
    -84: "Segment routing policy name required",
    -85: "Not running as root",
    -86: "Connection to the data plane already exists",
    -87: "Unsupported JNI version",
    -88: "IP prefix invalid masked bits set in address",
    -89: " Invalid worker thread",
    -90: "LISP is disabled",
    -91: "Classify table not found",
    -92: " Unsupported LISP EID type",
    -93: "Cannot create pcap file ",
    -94: "Invalid adjacency type for this operation",
    -95: "Operation would exceed configured capacity of ranges",
    -96: "Operation would exceed capacity of number of ports",
    -97: "Invalid address family ",
    -98: "Invalid subinterface sw_if_index",
    -99: "Table too big",
    -100: "Cannot enabledisable feature ",
    -101: "Duplicate BFD object",
    -102: "No such BFD object ",
    -103: "BFD object in use ",
    -104: "BFD feature not supported",
    -105: "Address in use",
    -106: "Address not in use ",
    -107: "Queue full ",
    -108: "Unsupported application config",
    -109: "URI FIFO segment create failed ",
    -110: "RLOC address is local",
    -111: "BFD object cannot be manipulated at this time",
    -112: "Invalid GPE mode ",
    -113: "LISP GPE entries are present",
    -114: "Address found for interface ",
    -115: "Session failed to connect",
    -116: "Entry already exists  ",
    -117: "Svm segment create fail",
    -118: "Application not attached",
    -119: "Bridge domain already exists",
    -120: "Bridge domain has member interfaces  ",
    -121: "Bridge domain 0 cant be deletedmodified",
    -122: "Bridge domain ID exceeds 16M limit",
    -123: " Subinterface doesnt exist ",
    -124: "Client already exist for L2 MACs events",
    -125: "Invalid queue ",
    -126: "Unsupported",
    -127: "Address already present on another interface",
    -128: " Invalid application namespace",
    -129: "Wrong app namespace secret ",
    -130: "Connect scope  ",
    -131: " App already attached",
    -132: "Redirect failed ",
    -133: "Illegal name ",
    -134: "No name servers configured    ",
    -135: "Name server not found  ",
    -136: "Name resolution not enabled ",
    -137: "Server format error bug ",
    -138: "No such name",
    -139: "No addresses available",
    -140: "Retry with new server",
    -141: "Connect was filtered",
    -142: "Inbound ACL in use ",
    -143: "Outbound ACL in use ",
    -144: "Initialization Failed ",
    -145: " Netlink error",
    -146: "BIER bitstringlength unsupported",
    -147: "Instance in use",
    -148: "Session ID out of range",
    -149: " ACL in use by a lookup context",
    -150: " Invalid value 3",
    -151: "Interface is not an Ethernet interface   ",
    -152: "Bridge domain already has a BVI interface ",
    -153: "Invalid Protocol",
    -154: "Invalid Algorithm",
    -155: "Resource In Use ",
    -156: "invalid Key Length ",
    -157: "Unsupported FIB Path protocol",
    -159: "Endian mismatch detected ",
    -160: "No change in table",
    -161: "Missing certifcate or key  ",
    -162: "limit exceeded ",
    -163: "port not managed by IKE",
    -164: "UDP port already taken",
    -165: "Retry stream call with cursor",
    -166: "Invalid value 4 ",
    -167: "Busy",
    -168: "Bug",
}


def get_vpp_error_message(error_code: int) -> str:
    message = vpp_error_codes_to_messages.get(error_code)
    if message is None:
        return ""
    return message


def get_vpp_error_log_message(error_code: int) -> str:
    return f"VPP return error message: {get_vpp_error_message(error_code)} (return code {error_code})."


class InterfaceHandler(VPPConfigUpdater, ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, InterfaceConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return {f"interface/{configuration_item.name}"}

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        match configuration_item.type:
            case InterfaceType.TAP:
                reply = self.vpp_client.api.tap_create_v2()
            case InterfaceType.GRE_TUNNEL:
                gre_type_config_to_vpp = {
                    GRELinkType.L3: 0,
                    GRELinkType.TEB: 1,
                    GRELinkType.ERSPAN: 2,
                }
                if not isinstance(configuration_item.link, GREInterfaceLink):
                    return ApplyReply(
                        success=False,
                        error="Failed to create a GRE interface, because no "
                        "GRE-specific information (InterfaceConfigurationItem.link) "
                        "was present",
                    )
                reply = self.vpp_client.api.gre_tunnel_add_del(
                    is_add=1,
                    tunnel={
                        "src": configuration_item.link.src_addr,
                        "dst": configuration_item.link.dst_addr,
                        "outer_table_id": configuration_item.link.outer_fib_id,
                        "instance": 0xFFFFFFFF,
                        "type": gre_type_config_to_vpp[configuration_item.link.type],
                        "session_id": configuration_item.link.session_id,
                        # "mode": ...
                        # "flags": ...
                    },
                )
                if reply.retval == 0:
                    reply_from_tagging = self._add_tag_to_interface(
                        tag=configuration_item.name,
                        sw_if_index=reply.sw_if_index,
                        is_add=True,
                    )
                    if reply_from_tagging.retval != 0:
                        return ApplyReply(
                            success=False,
                            error="Failed to tag GRE interface."
                            + get_vpp_error_log_message(reply_from_tagging.retval),
                        )
            case InterfaceType.WIREGUARD_TUNNEL:
                if not isinstance(configuration_item.link, WireguardInterfaceLink):
                    return ApplyReply(
                        success=False,
                        error="Failed to create wireguard interface, because "
                        "no wireguard-specific information ("
                        "InterfaceConfigurationItem.link) was present",
                    )
                reply = self.vpp_client.api.wireguard_interface_create(
                    interface={
                        "user_instance": 0xFFFFFFFF,
                        "port": configuration_item.link.port,
                        "src_ip": configuration_item.link.src_addr,
                        "private_key": base64.b64decode(
                            configuration_item.link.private_key
                        ),
                        # 'public_key': ...
                        # 'sw_if_index': ...
                    },
                    generate_key=False,
                )
                if reply.retval == 0:
                    reply_from_tagging = self._add_tag_to_interface(
                        tag=configuration_item.name,
                        sw_if_index=reply.sw_if_index,
                        is_add=True,
                    )
                    if reply_from_tagging.retval != 0:
                        return ApplyReply(
                            success=False,
                            error="Failed to tag wireguard interface."
                            + get_vpp_error_log_message(reply_from_tagging.retval),
                        )
            case InterfaceType.SOFTWARE_LOOPBACK:
                reply = self.vpp_client.api.create_loopback()
            case _:
                return ApplyReply(
                    success=False,
                    error="Interface type {} is not supported".format(
                        configuration_item.type
                    ),
                )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create interface."
                + get_vpp_error_log_message(reply.retval),
            )

        if_index = reply.sw_if_index
        if configuration_item.enabled:
            reply = self.vpp_client.api.sw_interface_set_flags(
                sw_if_index=if_index,
                flags=1,  # for dump use VppEnum.vl_api_if_status_flags_t.IF_STATUS_API_FLAG_LINK_UP
            )
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error=f"Failed to enable interface(sw_if_index {if_index}). "
                    + get_vpp_error_log_message(reply.retval),
                )

        if configuration_item.ip_addresses:
            for ip_address in configuration_item.ip_addresses:
                reply = self.vpp_client.api.sw_interface_add_del_address(
                    sw_if_index=if_index,
                    is_add=True,
                    prefix=ip_address,  # i.e. "10.10.10.10/16"
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to add ip address {ip_address} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )

        if configuration_item.mtu != NOT_SET_MTU:
            # Note: there are multiple MTU settings, see https://docs.fd.io/vpp/19.01/md_src_vnet_MTU.html
            # Ligato's VPP-agent sets only HW MTU, but we need to setup also Wireguard MTU and that interface is
            # virtual, so only SW MTU can be configured
            if not self._supports_setting_hw_mtu(configuration_item.type):
                # setting of HW MTU is unsupported -> setting up SW MTU
                reply = self.vpp_client.api.sw_interface_set_mtu(
                    sw_if_index=if_index,
                    mtu=[
                        configuration_item.mtu,  # L3 MTU
                        configuration_item.mtu,  # IPv4 MTU
                        configuration_item.mtu,  # IPv6 MTU
                        configuration_item.mtu,  # MPLS MTU
                    ],
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to set SW MTU {configuration_item.mtu} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )
            else:
                # Note: setting up VPP's HW MTU -> all SW MTUs will be set to HW MTU
                reply = self.vpp_client.api.hw_interface_set_mtu(
                    sw_if_index=if_index, mtu=configuration_item.mtu
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to set HW MTU {configuration_item.mtu} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )

        return ApplyReply(success=True, vpp_data={SW_IF_INDEX: if_index})

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        sw_if_index = self._get_sw_if_index(configuration_item.name)
        if sw_if_index == NO_INTERFACE_SW_INDEX:
            return ApplyReply(
                success=False,
                error=f"Can't find index for interface {configuration_item.name}. ",
            )

        match configuration_item.type:
            case InterfaceType.TAP:
                reply = self.vpp_client.api.tap_delete_v2(sw_if_index=sw_if_index)
            case InterfaceType.GRE_TUNNEL:
                gre_type_config_to_vpp = {
                    GRELinkType.L3: 0,
                    GRELinkType.TEB: 1,
                    GRELinkType.ERSPAN: 2,
                }
                reply = self.vpp_client.api.gre_tunnel_add_del(
                    is_add=0,
                    tunnel={
                        "src": configuration_item.link.src_addr,
                        "dst": configuration_item.link.dst_addr,
                        "outer_table_id": configuration_item.link.outer_fib_id,
                        "instance": 0xFFFFFFFF,
                        "type": gre_type_config_to_vpp[configuration_item.link.type],
                        "session_id": configuration_item.link.session_id,
                        # "mode": ...
                        # "flags": ...
                    },
                )
                if reply.retval == 0:
                    reply_from_untagging = self._add_tag_to_interface(
                        tag=configuration_item.name, is_add=False
                    )
                    if reply_from_untagging.retval != 0:
                        return ApplyReply(
                            success=False,
                            error="Failed to untag GRE interface."
                            + get_vpp_error_log_message(reply_from_untagging.retval),
                        )
            case InterfaceType.WIREGUARD_TUNNEL:
                reply = self.vpp_client.api.wireguard_interface_delete(
                    sw_if_index=sw_if_index
                )
                if reply.retval == 0:
                    reply_from_untagging = self._add_tag_to_interface(
                        tag=configuration_item.name, is_add=False
                    )
                    if reply_from_untagging.retval != 0:
                        return ApplyReply(
                            success=False,
                            error="Failed to untag wireguard interface."
                            + get_vpp_error_log_message(reply_from_untagging.retval),
                        )
            case InterfaceType.SOFTWARE_LOOPBACK:
                reply = self.vpp_client.api.delete_loopback(sw_if_index=sw_if_index)
            case _:
                return ApplyReply(
                    success=False,
                    error="Removal of interface type {} is not supported".format(
                        configuration_item.type
                    ),
                )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error=f"Failed to remove interface {configuration_item.name}."
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)

    @validate_multiple_config_items
    def update_in_vpp(self, old_configuration_item, new_configuration_item):
        # test whether only supported changes are made
        old = old_configuration_item.to_dict()
        old.update(
            {"enabled": True, "ip_addresses": [], "mtu": NOT_SET_MTU}
        )  # fill updatable fields with equal values
        new = new_configuration_item.to_dict()
        new.update(
            {"enabled": True, "ip_addresses": [], "mtu": NOT_SET_MTU}
        )  # fill updatable fields with equal values
        if old != new:
            return ApplyReply(
                success=False,
                error="Only update in fields 'enabled', 'ip_addresses', 'mtu' are supported",
            )

        # set status (if changed)
        if_index = self._get_sw_if_index(new_configuration_item.name)
        if old_configuration_item.enabled != new_configuration_item.enabled:
            reply = self.vpp_client.api.sw_interface_set_flags(
                sw_if_index=if_index, flags=1 if new_configuration_item.enabled else 0
            )
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error=f"Failed to enable/disable interface(sw_if_index {if_index}). "
                    + get_vpp_error_log_message(reply.retval),
                )
        # set ip addresses (if changed)
        for addr in (
            old_configuration_item.ip_addresses + new_configuration_item.ip_addresses
        ):
            if (
                addr in new_configuration_item.ip_addresses
                and addr not in old_configuration_item.ip_addresses
            ):
                reply = self.vpp_client.api.sw_interface_add_del_address(
                    sw_if_index=if_index,
                    is_add=True,
                    prefix=addr,  # i.e. "10.10.10.10/16"
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to add ip address {addr} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )
            elif (
                addr not in new_configuration_item.ip_addresses
                and addr in old_configuration_item.ip_addresses
            ):
                reply = self.vpp_client.api.sw_interface_add_del_address(
                    sw_if_index=if_index,
                    is_add=False,
                    prefix=addr,  # i.e. "10.10.10.10/16"
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to remove ip address {addr} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )
        if (
            old_configuration_item.mtu != new_configuration_item.mtu
            and new_configuration_item.mtu != NOT_SET_MTU
        ):
            if not self._supports_setting_hw_mtu(new_configuration_item.type):
                # setting of HW MTU is unsupported -> setting up SW MTU
                reply = self.vpp_client.api.sw_interface_set_mtu(
                    sw_if_index=if_index,
                    mtu=[
                        new_configuration_item.mtu,  # L3 MTU
                        new_configuration_item.mtu,  # IPv4 MTU
                        new_configuration_item.mtu,  # IPv6 MTU
                        new_configuration_item.mtu,  # MPLS MTU
                    ],
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to update SW MTU {new_configuration_item.mtu} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )
            else:
                # Note: setting up VPP's HW MTU -> all SW MTUs will be set to HW MTU
                reply = self.vpp_client.api.hw_interface_set_mtu(
                    sw_if_index=if_index, mtu=new_configuration_item.mtu
                )
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to update HW MTU {new_configuration_item.mtu} to "
                        + f"interface(sw_if_index {if_index}). "
                        + get_vpp_error_log_message(reply.retval),
                    )

        return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        sw_if_index = self._get_sw_if_index(configuration_item.name)
        for interface_detail in self.vpp_client.api.sw_interface_dump():
            if interface_detail.sw_if_index == sw_if_index:
                return SWInterfaceDetail.get_from_basic_vpp_client_equivalent_obj(
                    interface_detail
                )
        return dict()

    def _add_tag_to_interface(
        self, tag, sw_if_index=NO_INTERFACE_SW_INDEX, is_add=True
    ):
        return self.vpp_client.api.sw_interface_tag_add_del(
            tag=tag,
            is_add=1 if is_add else 0,
            # For some reason, if deleting tag, the software interface index has to be 0 and only name should be set.
            # Otherwise reply returns with error core -2 (incorrect sw_if_idx)
            sw_if_index=sw_if_index if is_add else 0,
        )

    def _supports_setting_hw_mtu(self, interface_type):
        # Note: virtual interfaces have no HW, hence can't set HW MTU
        return interface_type not in (
            InterfaceType.UNDEFINED_TYPE,
            InterfaceType.VXLAN_TUNNEL,
            InterfaceType.IPSEC_TUNNEL,
            InterfaceType.GRE_TUNNEL,
            InterfaceType.WIREGUARD_TUNNEL,
            InterfaceType.SOFTWARE_LOOPBACK,
            InterfaceType.SUB_INTERFACE,
        )


class RouteHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, RouteConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone, but it is normally something like this:
        # {f"route/vrf/<vrf_id>/if/<out_if>/dest/<dest_network>/gw/<next_hop>"}

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        if configuration_item.multi_output_paths:
            deps = set()
            for multipath in configuration_item.multi_output_paths:
                if multipath.outgoing_interface:
                    deps.add(f"interface/{multipath.outgoing_interface}")
            return deps
        if configuration_item.outgoing_interface:
            return {f"interface/{configuration_item.outgoing_interface}"}
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        return self._add_delete_route_in_vpp(configuration_item, is_add=True)

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        return self._add_delete_route_in_vpp(configuration_item, is_add=False)

    def _add_delete_route_in_vpp(self, configuration_item, is_add):
        path_type = (
            FibPathType.FIB_API_PATH_TYPE_DROP
            if configuration_item.type == RouteType.DROP
            else FibPathType.FIB_PATH_TYPE_NORMAL
        )
        sw_if_index = 0

        route = {
            "table_id": 0,  # hardcoded as there are not used multiple VRFs
            "prefix": configuration_item.destination_network,
            "n_paths": 0,
            "paths": [],
        }
        if not configuration_item.multi_output_paths:  # single path
            if configuration_item.type == RouteType.INTRA_VRF:
                sw_if_index = NO_INTERFACE_SW_INDEX
                if configuration_item.outgoing_interface:
                    sw_if_index = self._get_sw_if_index(
                        configuration_item.outgoing_interface
                    )
            path = {
                "weight": configuration_item.weight,
                "preference": 0,
                "table_id": 0,
                "next_hop_id": 0xFFFFFFFF,  # INVALID_INDEX
                "sw_if_index": sw_if_index,
                "rpf_id": 0,
                "proto": FibPathProto.FIB_PATH_NH_PROTO_IP4,
                "type": path_type,
                "flags": FibPathFlags.FIB_PATH_FLAG_NONE,
                "n_labels": 0,
                "label_stack": [{}] * 16,
            }
            if configuration_item.next_hop_address:
                path["nh"] = {
                    "address": {
                        "ip4": ip_address(str(configuration_item.next_hop_address))
                    }
                }
            route["n_paths"] = 1
            route["paths"].append(path)
        else:  # multipath
            for config_path in configuration_item.multi_output_paths:
                if configuration_item.type == RouteType.INTRA_VRF:
                    sw_if_index = NO_INTERFACE_SW_INDEX
                    if config_path.outgoing_interface:
                        sw_if_index = self._get_sw_if_index(
                            config_path.outgoing_interface
                        )
                path = {
                    "weight": config_path.weight,
                    "preference": 0,
                    "table_id": 0,
                    "next_hop_id": 0xFFFFFFFF,  # INVALID_INDEX
                    "sw_if_index": sw_if_index,
                    "rpf_id": 0,
                    "proto": FibPathProto.FIB_PATH_NH_PROTO_IP4,
                    "type": path_type,
                    "flags": FibPathFlags.FIB_PATH_FLAG_NONE,
                    "n_labels": 0,
                    "label_stack": [{}] * 16,
                }
                if config_path.next_hop_address:
                    path["nh"] = {
                        "address": {
                            "ip4": ip_address(str(config_path.next_hop_address))
                        }
                    }
                route["paths"].append(path)
            route["n_paths"] = len(route["paths"])

        reply = self.vpp_client.api.ip_route_add_del(
            is_add=1 if is_add else 0,
            is_multipath=1 if configuration_item.multi_output_paths else 0,
            route=route,
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create route."
                + get_vpp_error_log_message(reply.retval),
            )

        return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        outgoing_interface_index = NO_INTERFACE_SW_INDEX
        if configuration_item.outgoing_interface:
            outgoing_interface_index = self._get_sw_if_index(
                configuration_item.outgoing_interface
            )

        dump = self.vpp_client.api.ip_route_dump()
        try:
            for route_detail in dump:
                if (
                    route_detail.route.table_id == 0
                    and route_detail.route.prefix
                    == ipaddress.IPv4Network(configuration_item.destination_network)
                ):
                    return IPRouteDetail.get_from_basic_vpp_client_equivalent_obj(
                        route_detail
                    )
        except Exception:
            logger.exception(f"route detail dumping failed for {configuration_item}")

        return dict()


class ACLHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index, get_acl_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index
        self._get_acl_index = get_acl_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, ACLConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        dependencies = set()
        for egress_interface_name in configuration_item.egress:
            dependencies.add(f"interface/{egress_interface_name}")
        for ingress_interface_name in configuration_item.ingress:
            dependencies.add(f"interface/{ingress_interface_name}")
        return dependencies

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        # create ACL in VPP
        rules = ACLHandler._transform_rules_to_vpp_rules(configuration_item.rules)
        if not rules:
            return ApplyReply(
                success=False, error=f"No rules found for ACL {configuration_item.name}"
            )
        reply = self.vpp_client.api.acl_add_replace(
            acl_index=0xFFFFFFFF,  # to make new Entry
            tag=configuration_item.name,
            count=len(rules),
            r=rules,
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create ACL." + get_vpp_error_log_message(reply.retval),
            )

        # link interfaces to ACL
        acl_index = reply.acl_index
        reply = self.link_unlink_acl_interfaces(
            configuration_item, acl_index, is_add=True
        )
        if not reply.success:
            return reply

        return ApplyReply(success=True, vpp_data={ACL_INDEX: acl_index})

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        acl_index = self._get_acl_index(configuration_item.name)
        if acl_index == NO_ACL_INDEX:
            return ApplyReply(
                success=False,
                error=f"Can't get index for ACL {configuration_item.name}",
            )

        # unlink interfaces linked to ACL
        reply = self.link_unlink_acl_interfaces(
            configuration_item, acl_index, is_add=False
        )
        if not reply.success:
            return reply

        # remove ACL from VPP
        reply = self.vpp_client.api.acl_del(acl_index=acl_index)
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to remove ACL {configuration_item.name}. "
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True, vpp_data={ACL_INDEX: acl_index})

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        acl_index = self._get_acl_index(configuration_item.name)
        if acl_index == NO_ACL_INDEX:
            return dict()

        reply = self.vpp_client.api.acl_dump(acl_index=acl_index)
        if len(reply) == 1:
            return ACLDetails.get_from_basic_vpp_client_equivalent_obj(reply[0])
        # TODO dumping ACL interfaces? we get only their sw_if_index and we have that remembered, so real value is only
        #  simple boolean check that it is there
        # self.vpp_client.api.acl_interface_list_dump(...)
        return dict()

    def link_unlink_acl_interfaces(self, configuration_item, acl_index, is_add=True):
        link_unlink = "link" if is_add else "unlink"
        for interface_name in configuration_item.egress:
            reply = self.vpp_client.api.acl_interface_add_del(
                is_add=is_add,
                acl_index=acl_index,
                sw_if_index=self._get_sw_if_index(interface_name),
                is_input=False,
            )
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error=f"Failed to {link_unlink} interface {interface_name} to ACL "
                    f"{configuration_item.name} as egress interface. "
                    + get_vpp_error_log_message(reply.retval),
                )
        for interface_name in configuration_item.ingress:
            reply = self.vpp_client.api.acl_interface_add_del(
                is_add=is_add,
                acl_index=acl_index,
                sw_if_index=self._get_sw_if_index(interface_name),
                is_input=True,
            )
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error=f"Failed to {link_unlink} interface {interface_name} to ACL "
                    f"{configuration_item.name} as ingress interface. "
                    + get_vpp_error_log_message(reply.retval),
                )
        return ApplyReply(success=True)

    @staticmethod
    def _transform_rules_to_vpp_rules(
        config_rules: List[ACLRuleConfigurationItem],
    ) -> List:
        config_action_to_vpp_action = {
            # Note: coincidentally ACLAction int value is the needed
            # VPP constant, but lets not interchange these 2 logically different things
            ACLAction.DENY: 0,
            ACLAction.PERMIT: 1,
            ACLAction.REFLECT: 2,
        }
        vpp_rules = []
        for config_rule in config_rules:
            vpp_rule = {"is_permit": config_action_to_vpp_action[config_rule.action]}
            if (
                config_rule.refinement is not None
            ):  # further refinement/narrowing of traffic that this rule is for
                if config_rule.refinement.addresses is not None:
                    vpp_rule["src_prefix"] = (
                        config_rule.refinement.addresses.source_network
                    )
                    vpp_rule["dst_prefix"] = (
                        config_rule.refinement.addresses.destination_network
                    )
                match config_rule.refinement.protocol:
                    case ICMPProtocol(
                        icmpv6=icmpv6,
                        icmp_code_range=icmp_code_range,
                        icmp_type_range=icmp_type_range,
                    ):
                        vpp_rule["proto"] = (
                            VppEnum.vl_api_ip_proto_t.IP_API_PROTO_ICMP6
                            if icmpv6
                            else VppEnum.vl_api_ip_proto_t.IP_API_PROTO_ICMP
                        )
                        vpp_rule["srcport_or_icmptype_first"] = icmp_type_range.first
                        vpp_rule["srcport_or_icmptype_last"] = icmp_type_range.last
                        vpp_rule["dstport_or_icmpcode_first"] = icmp_code_range.first
                        vpp_rule["dstport_or_icmpcode_last"] = icmp_code_range.last
                    case TCPProtocol(
                        destination_port_range=destination_port_range,
                        source_port_range=source_port_range,
                        tcp_flags_mask=tcp_flags_mask,
                        tcp_flags_value=tcp_flags_value,
                    ):
                        vpp_rule["proto"] = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
                        vpp_rule["srcport_or_icmptype_first"] = (
                            source_port_range.lower_port
                        )
                        vpp_rule["srcport_or_icmptype_last"] = (
                            source_port_range.upper_port
                        )
                        vpp_rule["dstport_or_icmpcode_first"] = (
                            destination_port_range.lower_port
                        )
                        vpp_rule["dstport_or_icmpcode_last"] = (
                            destination_port_range.upper_port
                        )
                        vpp_rule["tcp_flags_mask"] = tcp_flags_mask
                        vpp_rule["tcp_flags_value"] = tcp_flags_value
                    case UDPProtocol(
                        destination_port_range=destination_port_range,
                        source_port_range=source_port_range,
                    ):
                        vpp_rule["proto"] = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
                        vpp_rule["srcport_or_icmptype_first"] = (
                            source_port_range.lower_port
                        )
                        vpp_rule["srcport_or_icmptype_last"] = (
                            source_port_range.upper_port
                        )
                        vpp_rule["dstport_or_icmpcode_first"] = (
                            destination_port_range.lower_port
                        )
                        vpp_rule["dstport_or_icmpcode_last"] = (
                            destination_port_range.upper_port
                        )
                    case OtherProtocol(protocol=protocol):
                        vpp_rule["proto"] = protocol  # VppEnum.vl_api_ip_proto_t
            vpp_rules.append(vpp_rule)
        return vpp_rules


class Nat44AddressPoolHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client):
        self.vpp_client = vpp_client

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, Nat44AddressPoolConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        # ignoring vrf dependency as only one default vrf is used
        # ignoring need for NAT's endpoint-dependent mode as that is the default run of VPP
        return set()

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def add_to_vpp(self, configuration_item):
        return self.add_del_to_vpp(configuration_item, is_add=True)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def remove_from_vpp(self, configuration_item):
        return self.add_del_to_vpp(configuration_item, is_add=False)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def dump_from_vpp(self, configuration_item):
        return [
            NAT44AddressDetails.get_from_basic_vpp_client_equivalent_obj(address_detail)
            for address_detail in self.vpp_client.api.nat44_address_dump()
            if configuration_item.first_ip <= address_detail.ip_address
            and address_detail.ip_address <= configuration_item.last_ip
        ]

    def add_del_to_vpp(self, configuration_item, is_add=True):
        reply = self.vpp_client.api.nat44_add_del_address_range(
            is_add=1 if is_add else 0,
            first_ip_address=configuration_item.first_ip,
            last_ip_address=configuration_item.last_ip,
            vrf_id=0,  # we use only vrf 0 for failover case
            # not using twice-nat -> not configuring it
            # flags=VppEnum.vl_api_nat_config_flags_t.NAT_IS_TWICE_NAT if configuration_item.twice_nat else 0
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create NAT44 address pool."
                + get_vpp_error_log_message(reply.retval),
            )

        return ApplyReply(success=True)


class Nat44InterfaceHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, Nat44InterfaceConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return {f"interface/{configuration_item.name}"}

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def add_to_vpp(self, configuration_item):
        return self.add_del_to_vpp(configuration_item, is_add=True)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def remove_from_vpp(self, configuration_item):
        return self.add_del_to_vpp(configuration_item, is_add=False)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def dump_from_vpp(self, configuration_item):
        interface_index = self._get_sw_if_index(configuration_item.name)
        for detail in self.vpp_client.api.nat44_interface_dump():
            if detail.sw_if_index == interface_index:
                return NAT44InterfaceDetails.get_from_basic_vpp_client_equivalent_obj(
                    detail
                )

    def add_del_to_vpp(self, configuration_item, is_add=True):
        if configuration_item.nat_inside:
            reply = self.enable_nat44_interface(
                configuration_item.name,
                True,
                configuration_item.output_feature,
                is_add=is_add,
            )
            if not reply.success:
                return reply
        if configuration_item.nat_outside:
            reply = self.enable_nat44_interface(
                configuration_item.name,
                False,
                configuration_item.output_feature,
                is_add=is_add,
            )
            if not reply.success:
                return reply
        if (
            configuration_item.output_feature
            and not configuration_item.nat_inside
            and not configuration_item.nat_outside
        ):
            reply = self.enable_nat44_interface(
                configuration_item.name,
                False,
                configuration_item.output_feature,
                is_add=is_add,
            )
            if not reply.success:
                return reply
        return ApplyReply(success=True)

    def enable_nat44_interface(self, name, is_inside, is_output_feature, is_add=True):
        create_delete = "create" if is_add else "delete"
        add_del_feature = self.vpp_client.api.nat44_interface_add_del_feature
        if is_output_feature:
            add_del_feature = self.vpp_client.api.nat44_interface_add_del_output_feature
        reply = add_del_feature(
            sw_if_index=self._get_sw_if_index(name),
            flags=VppEnum.vl_api_nat_config_flags_t.NAT_IS_INSIDE if is_inside else 0,
            is_add=is_add,
        )
        if reply.retval != 0:
            output_feature = " (output feature)" if is_output_feature else ""
            return ApplyReply(
                success=False,
                error="Failed to {create_delete} nat interface{output_feature}. "
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)


class DNat44Handler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, DNat44ConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        # ignoring need for NAT's endpoint-dependent mode as that is the default run of VPP
        # ignoring nat pool dependency for twice-nat as not used in failover use case
        # ignoring vrf dependency as only one vrf is used and that is the default one that is always present
        needed_interfaces = {
            sm.external_interface
            for sm in configuration_item.static_mappings
            if sm.external_interface != ""
        }.union(
            {
                im.interface
                for im in configuration_item.identity_mappings
                if im.interface != ""
            }
        )
        return {
            f"interface/{needed_interface_name}"
            for needed_interface_name in needed_interfaces
        }

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def add_to_vpp(self, configuration_item):
        return self.add_delete_from_vpp(configuration_item, is_add=True)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def remove_from_vpp(self, configuration_item):
        return self.add_delete_from_vpp(configuration_item, is_add=False)

    @validate_config_item
    @enforce_enabled_nat_in_vpp
    def dump_from_vpp(self, configuration_item):
        return {
            "static_mappings": [
                NAT44StaticMappingDetails.get_from_basic_vpp_client_equivalent_obj(
                    static_mapping
                )
                for static_mapping in self.vpp_client.api.nat44_static_mapping_dump()
                if static_mapping.tag == configuration_item.label
            ],
            "identity_mappings": [
                NAT44IdentityMappingDetails.get_from_basic_vpp_client_equivalent_obj(
                    identity_mapping
                )
                for identity_mapping in self.vpp_client.api.nat44_identity_mapping_dump()
                if identity_mapping.tag == configuration_item.label
            ],
        }

    def add_delete_from_vpp(self, configuration_item, is_add=True):
        for identity_mapping in configuration_item.identity_mappings:
            reply = self.add_del_identity_mapping(
                identity_mapping, configuration_item.label, is_add=is_add
            )
            if not reply.success:
                return reply
        for static_mapping in configuration_item.static_mappings:
            reply = self.add_del_static_mapping(
                static_mapping, configuration_item.label, is_add=is_add
            )
            if not reply.success:
                return reply
        return ApplyReply(success=True)

    def add_del_identity_mapping(self, identity_mapping, nat_label, is_add=True):
        interface_sw_index = NO_INTERFACE_SW_INDEX
        if identity_mapping.interface:
            interface_sw_index = self._get_sw_if_index(identity_mapping.interface)
            if (
                interface_sw_index == NO_INTERFACE_SW_INDEX
            ):  # not found index for interface name
                return ApplyReply(
                    success=False,
                    error=f"Can't find sw_if_index for interface with name {identity_mapping.interface}",
                )
        reply = self.vpp_client.api.nat44_add_del_identity_mapping(
            is_add=1 if is_add else 0,
            tag=nat_label,
            flags=(
                VppEnum.vl_api_nat_config_flags_t.NAT_IS_ADDR_ONLY
                if identity_mapping.port == 0
                else 0
            ),
            ip_address=(
                identity_mapping.ip_address
                if not identity_mapping.interface
                else ipaddress.IPv4Address("0.0.0.0")
            ),
            port=identity_mapping.port,
            protocol=int(identity_mapping.protocol),
            sw_if_index=interface_sw_index,
            vrf_id=0,  # using always vrf 0 for failover use case
        )
        if reply.retval != 0:
            add_remove = "add" if is_add else "remove"
            return ApplyReply(
                success=False,
                error=f"Failed to {add_remove} identity mapping ({identity_mapping}). "
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)

    def add_del_static_mapping(self, static_mapping, nat_label, is_add=True):
        if not static_mapping.local_ips:
            return ApplyReply(success=False, error="No local address provided")
        if len(static_mapping.local_ips) > 1:
            # Note: we should not need it in failover use case
            return ApplyReply(success=False, error="Loadbalanced NAT is not supported")

        external_interface_sw_index = 0  # NOTE: This is a workaround, because NO_INTERFACE_SW_INDEX crashes VPP 22.02 # TODO still problem with currently used VPP 22.10.1 ?
        if static_mapping.external_interface:
            external_interface_sw_index = self._get_sw_if_index(
                static_mapping.external_interface
            )
            if (
                external_interface_sw_index == NO_INTERFACE_SW_INDEX
            ):  # not found index for interface name
                return ApplyReply(
                    success=False,
                    error=f"Can't find sw_if_index for interface with name "
                    f"{static_mapping.external_interface}",
                )

        # ignoring twicenat flags as twice nat is not needed for failover case
        # isTwiceNat:     mapping.TwiceNat == nat.DNat44_StaticMapping_ENABLED,
        # isSelfTwiceNat: mapping.TwiceNat == nat.DNat44_StaticMapping_SELF,
        # NOTE: Removed NAT_IS_OUT2IN_ONLY flag due to VPP 25.06 compatibility issues
        # with nat44_add_del_static_mapping_v2 API
        flags = 0
        if (
            static_mapping.local_ips[0].local_port == 0
            and static_mapping.external_port == 0
        ):
            flags |= VppEnum.vl_api_nat_config_flags_t.NAT_IS_ADDR_ONLY

        # Determine which external address to use
        # Priority: explicit external_ip > interface-based IP
        # When external_ip is set (not 0.0.0.0), use it and set sw_if_index to 0xFFFFFFFF
        # to avoid VPP using the interface
        use_explicit_ip = (
            static_mapping.external_ip 
            and static_mapping.external_ip != ipaddress.IPv4Address("0.0.0.0")
        )
        
        if use_explicit_ip:
            # Use explicit IP - don't let VPP use interface by setting index to NO_INTERFACE
            final_external_ip = static_mapping.external_ip
            final_external_sw_if_index = NO_INTERFACE_SW_INDEX
            logger.info(f"NAT static mapping: Using explicit IP {final_external_ip}, "
                       f"sw_if_index={hex(final_external_sw_if_index)} (NO_INTERFACE_SW_INDEX)")
        else:
            # Use interface-based IP
            final_external_ip = ipaddress.IPv4Address("0.0.0.0")
            final_external_sw_if_index = external_interface_sw_index
            logger.info(f"NAT static mapping: Using interface-based, "
                       f"sw_if_index={final_external_sw_if_index} (external_ip=0.0.0.0)")

        reply = self.vpp_client.api.nat44_add_del_static_mapping_v2(
            is_add=is_add,
            tag=nat_label,
            local_ip_address=static_mapping.local_ips[0].local_ip,
            external_ip_address=final_external_ip,
            protocol=int(static_mapping.protocol),
            external_sw_if_index=final_external_sw_if_index,
            vrf_id=0,  # only VRF 0 is used in failover use case
            flags=flags,
            local_port=static_mapping.local_ips[0].local_port,
            external_port=static_mapping.external_port,
            # Note: not setting twiceNat pool ip as twice nat is not needed for failover case
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error=f"Failed to create static mapping ({static_mapping}). "
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)


class WireguardPeerHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index, get_wireguard_peer_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index
        self._get_wireguard_peer_index = get_wireguard_peer_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, WireguardPeerConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        if configuration_item.wg_if_name:
            return {f"interface/{configuration_item.wg_if_name}"}
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        reply = self.vpp_client.api.wireguard_peer_add(
            peer={
                "public_key": base64.b64decode(configuration_item.public_key),
                "port": configuration_item.port,
                "endpoint": configuration_item.endpoint,
                "n_allowed_ips": len(configuration_item.allowed_ips),
                "allowed_ips": configuration_item.allowed_ips,
                "sw_if_index": self._get_sw_if_index(configuration_item.wg_if_name),
                "persistent_keepalive": configuration_item.persistent_keepalive,
                # ignoring: flags, table_id, peer_index
            }
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create wireguard peer."
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(
            success=True, vpp_data={WIREGUARD_PEER_INDEX: reply.peer_index}
        )

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        peer_index = self._get_wireguard_peer_index(configuration_item)
        if peer_index == NO_WIREGUARD_PEER_INDEX:
            ApplyReply(success=False, error="Peer index not found")
        reply = self.vpp_client.api.wireguard_peer_remove(peer_index=peer_index)
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error=f"Failed to remove wireguard peer (peer_index {peer_index}). "
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        peer_index = self._get_wireguard_peer_index(configuration_item)
        if peer_index == NO_WIREGUARD_PEER_INDEX:
            logger.warning(
                f"can't find index for wireguard peer {configuration_item.name} and "
                f"therefore no vpp dump will be available"
            )
            return dict()
        reply = self.vpp_client.api.wireguard_peers_dump(peer_index=peer_index)
        if not reply:
            logger.warning(
                f"vpp can't find data for given wireguard peer index {peer_index} and "
                f"therefore no vpp dump will be available"
            )
            return dict()
        return WireguardPeerDetail.get_from_basic_vpp_client_equivalent_obj(
            reply[0].peer
        )


class LCPHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(
            configuration_item, LCPGlobalsConfigurationItem
        ) or isinstance(configuration_item, LCPPairConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # noone uses it

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        if isinstance(configuration_item, LCPPairConfigurationItem):
            return {f"interface/{configuration_item.interface}"}
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        if isinstance(configuration_item, LCPPairConfigurationItem):
            return self.add_del_lcp_pair_to_vpp(configuration_item, is_add=True)

        # add LCP Global settings
        reply = self.vpp_client.api.cli_inband(
            cmd=f"lcp default netns {configuration_item.default_namespace}"
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to set default namespace for LCP."
                + get_vpp_error_log_message(reply.retval),
            )
        reply = self.vpp_client.api.cli_inband(
            cmd="lcp lcp-sync {}".format("on" if configuration_item.lcp_sync else "off")
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to set lcp-sync."
                + get_vpp_error_log_message(reply.retval),
            )
        reply = self.vpp_client.api.cli_inband(
            cmd="lcp lcp-auto-subint {}".format(
                "on" if configuration_item.lcp_auto_subint else "off"
            )
        )
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to set lcp-auto-subint."
                + get_vpp_error_log_message(reply.retval),
            )
        return ApplyReply(success=True)

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        if isinstance(configuration_item, LCPPairConfigurationItem):
            return self.add_del_lcp_pair_to_vpp(configuration_item, is_add=False)
        # there is no remove for LCPGlobals (they can be only set and we don't "unset" them for delete)
        return ApplyReply(success=True)

    def add_del_lcp_pair_to_vpp(self, configuration_item, is_add=True):
        # the binary api for linux-cp's pair add/del is broken (https://lists.fd.io/g/vpp-dev/topic/lcp_plugin_api_issue_report/89972222?p=)
        # reply = self.vpp_client.api.lcp_itf_pair_add_del_v2(
        #     is_add=1 if is_add else 0,
        #     sw_if_index=self._get_sw_if_index(configuration_item.interface),
        #     host_if_name=configuration_item.mirror_interface_host_name,
        #     host_if_type=int(configuration_item.mirror_interface_type),
        #     netns=configuration_item.host_namespace
        # )
        # using CLI instead (CLI )
        #   lcp create <sw_if_index>|<if-name> host-if <host-if-name> netns <namespace> [tun]
        #    <sw_if_index>|<if-name>
        if is_add:
            cmd = "lcp create {} host-if {}{}{}".format(
                self._get_sw_if_index(configuration_item.interface),
                configuration_item.mirror_interface_host_name,
                (
                    f" netns {configuration_item.host_namespace}"
                    if configuration_item.host_namespace
                    else ""
                ),
                (
                    " tun"
                    if configuration_item.mirror_interface_type
                    == LCPHostInterfaceTypeEnum.TUN
                    else ""
                ),
            ).strip()
        else:
            cmd = "lcp delete {}".format(
                self._get_sw_if_index(configuration_item.interface)
            )
        reply = self.vpp_client.api.cli_inband(cmd=cmd)
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error="Failed to create lcp pair."
                + get_vpp_error_log_message(reply.retval),
            )

        if is_add:
            dump = self.dump_from_vpp(configuration_item)
            if not isinstance(dump, LCPPairDetail):
                logger.warning(
                    "can't retrieve host_sw_if_index (VPP interface part of tunneling from VPP to linux networking "
                    "namespace (LCP interface mirroring)): can't retrieve lcp pair listing"
                )
                return ApplyReply(success=True)
            return ApplyReply(
                success=True, vpp_data={HOST_SW_IF_INDEX: dump.host_sw_if_index}
            )
        else:
            return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        if isinstance(configuration_item, LCPPairConfigurationItem):
            reply = self.vpp_client.api.lcp_itf_pair_get()
            try:  # the binary api is a mess in VPP 22.02 (fixed in newer VPP?), so to prevent unexpected things i just use try/except # TODO still problem with currently used VPP 22.10.1 ?
                if reply[0].retval != 0:
                    logger.warning("can't retrieve lcp pairs")
                    return dict()

                phy_sw_if_index = self._get_sw_if_index(configuration_item.interface)
                for pair_detail in reply[1]:
                    if (
                        pair_detail.host_if_name
                        == configuration_item.mirror_interface_host_name
                        and pair_detail.phy_sw_if_index == phy_sw_if_index
                    ):
                        return LCPPairDetail.get_from_basic_vpp_client_equivalent_obj(
                            pair_detail
                        )
            except Exception:
                logger.exception("can't handle retrieval of lcp pairs")
            return dict()

        # the binary api for linux-cp's default namespage getting is broken too
        # reply = self.vpp_client.api.lcp_default_ns_get()
        return dict()


class FRRAgentClient(Proxy):
    def __init__(self, frr_agent_host: str = "0.0.0.0", frr_agent_port: int = 9999):
        """Creates and initializes FRR Agent client

        :param frr_agent_host: hostname/ip address of the FRR Agent's Pyro5 nameserver
        :param frr_agent_port: port of the FRR Agent's Pyro5 nameserver
        """
        serializers.import_pyro5_serializers()  # fix for serializing of custom types
        super().__init__(f"PYRONAME:frr.api@{frr_agent_host}:{frr_agent_port}")


class FRRHandler(ConfigurationItemHandler):
    def __init__(self, frr_agent_host, frr_agent_port):
        self._frr_agent_host = frr_agent_host
        self._frr_agent_port = frr_agent_port

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, FRRConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        with FRRAgentClient(
            frr_agent_host=self._frr_agent_host, frr_agent_port=self._frr_agent_port
        ) as client:
            reply = client.load_vtysh_configuration(configuration_item.config)
            if reply.return_code:
                ApplyReply(success=False, error="return code " + reply.return_code)
        return ApplyReply(success=True)

    def remove_from_vpp(self, configuration_item):
        return ApplyReply(
            success=True
        )  # do nothing, only by applying new config to FRR changes something inside FRR

    def dump_from_vpp(self, configuration_item):
        with FRRAgentClient(
            frr_agent_host=self._frr_agent_host, frr_agent_port=self._frr_agent_port
        ) as client:
            reply = client.run_vtysh_command("write terminal")
            if reply.return_code:
                FRRConfigurationItem()
            start_index = reply.stdout.find("!")
            if start_index < 0:
                start_index = 0
            end_index = reply.stdout.rfind("end")
            if end_index < 0:
                end_index = len(reply.stdout)
            return FRRConfigurationItem(config=reply.stdout[start_index:end_index])


class UnavailableDHCPSocketError(Exception):
    pass


class DHCPSocketConnetionError(Exception):
    pass


class DHCPRequestSendError(Exception):
    pass


class DHCPResponceReceiveError(Exception):
    pass


class DHCPResponceParsingError(Exception):
    pass


class DHCPHandler(ConfigurationItemHandler):

    def __init__(self, dhcp_socket):
        self._dhcp_socket = dhcp_socket

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, DHCPConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # not used by anyone

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        config = configuration_item.config

        # removing comments (not valid for json)
        if configuration_item.strip_comment_lines:
            config = "\n".join(line for line in config.splitlines() if "//" not in line)

        # local config validation
        try:
            config_dict = json.loads(config)
        except Exception as e:
            return ApplyReply(
                success=False,
                error="Config is not parsable json:"
                + repr(traceback.format_exception(e)),
            )

        # DHCP server restart (technically it is shutdown, but supervisord will start it again in docker!)
        # https://kea.readthedocs.io/en/kea-2.4.0/arm/ctrl-channel.html#the-shutdown-command
        # TODO test
        if configuration_item.restart_before_config_apply:
            try:
                response = self._send_request(
                    KeaConfigRequest(
                        command="shutdown",
                        arguments=dict(),
                    )
                )
            except Exception as e:
                return ApplyReply(
                    success=False,
                    error="Error while doing shutdown on DHCP server (part of restart):"
                    + repr(traceback.format_exception(e)),
                )
            if response.result != 0:
                return ApplyReply(
                    success=False,
                    error="DHCP server shutdown command failed (shutdown is part of restart):"
                    + repr(response.text),
                )
            # TODO some active checking of correct starting and if not detected in some time then error to client
            time.sleep(5)

        # remote config validation
        # (see https://kea.readthedocs.io/en/kea-2.4.0/arm/ctrl-channel.html#the-config-test-command)
        try:
            response = self._send_request(
                KeaConfigRequest(
                    command="config-test",
                    arguments=config_dict,
                )
            )
        except Exception as e:
            return ApplyReply(
                success=False,
                error="Error while testing config by DHCP server:"
                + repr(traceback.format_exception(e)),
            )
        if response.result != 0:
            return ApplyReply(
                success=False,
                error="Remote validation of config failed:" + repr(response.text),
            )
        # configure DHCP server with the checked config
        # (see https://kea.readthedocs.io/en/kea-2.4.0/arm/ctrl-channel.html#the-config-set-command)
        try:
            response = self._send_request(
                KeaConfigRequest(
                    command="config-set",
                    arguments=config_dict,
                )
            )
        except Exception as e:
            return ApplyReply(
                success=False,
                error="Error while applying config:"
                + repr(traceback.format_exception(e)),
            )
        if response.result != 0:
            return ApplyReply(
                success=False,
                error="Failed to set new configuration due to:" + repr(response.text),
            )
        return ApplyReply(success=True)

    def remove_from_vpp(self, configuration_item):
        return ApplyReply(
            success=True
        )  # do nothing, only by applying new config to DHCP changes something inside DHCP

    def dump_from_vpp(self, configuration_item):
        # configure DHCP server with the checked config
        # (see https://kea.readthedocs.io/en/kea-2.4.0/arm/ctrl-channel.html#the-config-get-command)
        try:
            response = self._send_request(
                KeaConfigRequest(
                    command="config-get",
                )
            )
        except Exception:
            logger.exception("Error while getting DHCP config")
            return dict()
        if response.result != 0:
            logger.warning(
                "Failed to get new DHCP configuration due to:" + repr(response.text)
            )
            return dict()
        return DHCPConfigurationItem(config=json.dumps(response.arguments))

    def _send_request(self, request: KeaConfigRequest) -> KeaConfigResponse:
        """Send request to KEA DHCP server using unix socket."""

        def recvall(socket):
            """Receive all data from unix socket"""
            data = []
            while True:
                chunk = socket.recv(4096)
                if not chunk:
                    break
                data.append(chunk)
            return b"".join(data)

        def wait_for_writable_dhcp_socket(timeout: int) -> bool:
            """Timeouted wait for DHCP socket file to be present and writable."""
            for _ in range(timeout * 2):
                if os.path.exists(self._dhcp_socket) and os.access(
                    self._dhcp_socket, os.W_OK
                ):
                    return True
                time.sleep(0.5)
            return False

        if not wait_for_writable_dhcp_socket(5):
            raise UnavailableDHCPSocketError(
                f"can't find or write DHCP control socket ({self._dhcp_socket}) within timeout "
            )

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            try:
                client.connect(self._dhcp_socket)
            except Exception as e:
                raise DHCPSocketConnetionError(self._dhcp_socket) from e

            try:
                req_encoded = request.to_json().encode()
            except Exception as e:
                raise ValueError("can't convert request to json and encode it") from e

            try:
                client.sendall(req_encoded)
            except Exception as e:
                raise DHCPRequestSendError() from e

            try:
                response = recvall(client)
            except Exception as e:
                raise DHCPResponceReceiveError() from e

            try:
                return KeaConfigResponse.from_json(response.decode())
            except Exception as e:
                raise DHCPResponceParsingError() from e
        finally:
            # Close the connection
            client.close()


class RunningPacketCaptureHandler(ConfigurationItemHandler):
    def __init__(self, vpp_client, get_sw_if_index, get_current_running_packet_capture):
        self.vpp_client = vpp_client
        self._get_sw_if_index = get_sw_if_index
        self._get_current_running_packet_capture = get_current_running_packet_capture

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, RunningPacketCapture)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # noone uses it

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        if configuration_item.capture_only_from_interface != PCAP_ANY_INTERFACE:
            return {f"interface/{configuration_item.capture_only_from_interface}"}
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        """Starts the packet capturing defined in configuration_item"""

        # check for bad case of running multiple packet capturing at the same time
        if self._get_current_running_packet_capture() is not None:
            return ApplyReply(
                success=False,
                error=f"There can be only one packet capturing running at the same time. The current "
                f"packet capturing running is {self._get_current_running_packet_capture()}",
            )

        # configure advanced filtering
        filter_cmds = []
        for rule in configuration_item.capture_by_matching_rules:
            match rule:
                case L2PacketMatchingRule(
                    src_physical_address=src, dest_physical_address=dst, protocol=proto
                ):
                    if not src and not dst and proto == NO_PROTOCOL:  # no matching
                        continue
                    filter_cmds.append(
                        "classify filter pcap mask l2 {}{}{}match l2{}{}{}".format(
                            "src " if src else "",
                            "dst " if dst else "",
                            "proto " if proto else "",
                            f" src {src}" if src else "",
                            f" dst {dst}" if dst else "",
                            f" proto {proto}" if proto else "",
                        )
                    )
                case L3PacketMatchingRule(
                    src_ipv4_address=src, dest_ipv4_address=dst, protocol=proto
                ):
                    if not src and not dst and proto == NO_PROTOCOL:  # no matching
                        continue
                    filter_cmds.append(
                        "classify filter pcap mask l3 ip4 {}{}{}match l3 ip4{}{}{}".format(
                            "src " if src else "",
                            "dst " if dst else "",
                            "proto " if proto else "",
                            f" src {src}" if src else "",
                            f" dst {dst}" if dst else "",
                            f" proto {proto}" if proto else "",
                        )
                    )
                case _:
                    logger.warning(f"Ignoring unknown packet matching rule: {rule}")
        if filter_cmds:
            reply = self.vpp_client.api.cli_inband(cmd="classify filter pcap del")
            if reply.retval != 0:
                return ApplyReply(
                    success=False,
                    error="Failed to clean classify filters."
                    + get_vpp_error_log_message(reply.retval),
                )
            for cmd in filter_cmds:
                reply = self.vpp_client.api.cli_inband(cmd=cmd)
                if reply.retval != 0:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to apply one of classify filters('{cmd}'). "
                        f"{get_vpp_error_log_message(reply.retval)}(CLI reply: {reply.reply})",
                    )

        # configure pcap capturing start
        interface_name = configuration_item.capture_only_from_interface
        if interface_name != PCAP_ANY_INTERFACE:
            sw_if_index = self._get_sw_if_index(interface_name)  # logical name to index
            interfaces = self.vpp_client.api.sw_interface_dump(sw_if_index=sw_if_index)
            if not interfaces:
                return ApplyReply(
                    success=False,
                    error=f"Failed to resolve VPP name for interface {interface_name}). "
                    + get_vpp_error_log_message(reply.retval),
                )
            interface_name = interfaces[0].interface_name  # get VPP name of interface

        pcap_start = "pcap trace {}{}{}max {} intfc {} file {} max-bytes-per-pkt {}{}{}{}".format(
            "rx " if configuration_item.capture_rx_packets else "",
            "tx " if configuration_item.capture_tx_packets else "",
            "drop " if configuration_item.capture_dropped_packets else "",
            configuration_item.max_packets_to_capture,
            interface_name,
            "{}-{}.pcap".format(
                configuration_item.output_file_prefix,
                datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f"),
            ),
            configuration_item.max_bytes_per_packet,
            " filter" if filter_cmds else "",
            " preallocate-data" if configuration_item.preallocate_data_buffer else "",
            " free-data" if configuration_item.free_data_buffer else "",
        )
        reply = self.vpp_client.api.cli_inband(cmd=pcap_start)
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error=f"Failed to start pcap capturing (CLI command: {pcap_start}). "
                f"{get_vpp_error_log_message(reply.retval)}(CLI reply: {reply.reply})",
            )

        return ApplyReply(success=True)

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        """Stops the packet capturing defined in configuration_item"""

        # check for bad case of stopping the wrong capturing
        if self._get_current_running_packet_capture() is not configuration_item:
            return ApplyReply(
                success=False,
                error=f"Only packet capturing that is currently running can be stopped (currently "
                f"running: {self._get_current_running_packet_capture()}, wanted to stop: "
                f"{configuration_item})",
            )

        # stop tracing
        reply = self.vpp_client.api.cli_inband(cmd="pcap trace off")
        if reply.retval != 0 and "No packets captured" not in reply.reply:
            return ApplyReply(
                success=False,
                error=f"Failed to stop pcap tracing. {get_vpp_error_log_message(reply.retval)}"
                f"(CLI reply: {reply.reply})",
            )

        # extract info from tracing stop
        captured_packets_count = 0
        filename = ""
        if "No packets captured" not in reply.reply:
            match re.findall(r"(\d*) packets to (\/[^,]*)", reply.reply):
                case [(packets, file)]:
                    try:
                        captured_packets_count = int(packets)
                    except ValueError:
                        return ApplyReply(
                            success=False,
                            error=f"Failed to parse packet count from string '{packets}'",
                        )
                    filename = file
                case _:
                    return ApplyReply(
                        success=False,
                        error=f"Failed to parse packet capturing stop output '{reply.reply}'",
                    )

        # cleanup advanced filtering
        reply = self.vpp_client.api.cli_inband(cmd="classify filter pcap del")
        if reply.retval != 0:
            return ApplyReply(
                success=False,
                error=f"Failed to clean classify filters. "
                f"{get_vpp_error_log_message(reply.retval)}(CLI reply: {reply.reply})",
            )

        return ApplyReply(
            success=True,
            vpp_data={
                "packet_capture_output_file": filename,
                "count_of_captured_packets": captured_packets_count,
            },
        )

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        return dict()


class LinuxDockerVethTunnelHandler(ConfigurationItemHandler):
    def __init__(self):
        pass

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, LinuxDockerVethTunnelConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # noone uses it

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        if not configuration_item.docker_container_name:
            return ApplyReply(success=False, error="Container name must be filled")

        # prepare docker container (network namespace linking)
        try:
            container_pid = subprocess.check_output(
                "docker inspect -f '{{.State.Pid}}' "
                + configuration_item.docker_container_name,
                shell=True,
            ).decode()
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to get docker container id for docker container "
                f"{configuration_item.docker_container_name}. Error code {e.returncode} ({e})",
            )
        container_pid = container_pid.replace("\n", "")
        try:
            subprocess.check_call(
                f"sudo mkdir -p /var/run/netns;sudo ln -sf /proc/{container_pid}/ns/net "
                f'"/var/run/netns/{configuration_item.docker_container_name}"',
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to link docker network namespace into standard linux network namespace "
                f"directory. Docker container name: {configuration_item.docker_container_name}. "
                f"Error code {e.returncode} ({e})",
            )

        # create veth pair and position one end into docker container
        try:
            subprocess.check_call(
                f"sudo ip link add {configuration_item.host_interface_name} type veth "
                f"peer name {configuration_item.docker_interface_name}",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to create veth tunnel. Error code {e.returncode} ({e})",
            )

        try:
            subprocess.check_call(
                f"sudo ip link set {configuration_item.docker_interface_name} netns "
                f"{configuration_item.docker_container_name}",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to move one end of veth tunnel into dokcer container "
                f"{configuration_item.docker_container_name}. Error code {e.returncode} ({e})",
            )
        # set interface up
        try:
            subprocess.check_call(
                f"sudo ip netns exec {configuration_item.docker_container_name} ip link set "
                f"{configuration_item.docker_interface_name} up",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to enable docker end of veth tunnel. Error code {e.returncode} ({e})",
            )
        try:
            subprocess.check_call(
                f"sudo ip link set {configuration_item.host_interface_name} up",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to enable host end of veth tunnel. Error code {e.returncode} ({e})",
            )

        # configure ip addresses for both veth tunnel endpoints
        for ip_address in configuration_item.host_interface_ip_addresses:
            try:
                subprocess.check_call(
                    f"sudo ip addr add {ip_address} dev {configuration_item.host_interface_name}",
                    shell=True,
                )
            except subprocess.CalledProcessError as e:
                return ApplyReply(
                    success=False,
                    error=f"Failed to set address {ip_address} to host end of veth tunnel. "
                    f"Error code {e.returncode} ({e})",
                )
        for ip_address in configuration_item.docker_interface_ip_addresses:
            try:
                subprocess.check_call(
                    f"sudo ip netns exec {configuration_item.docker_container_name} ip addr add {ip_address} "
                    f"dev {configuration_item.docker_interface_name}",
                    shell=True,
                )
            except subprocess.CalledProcessError as e:
                return ApplyReply(
                    success=False,
                    error=f"Failed to set address {ip_address} to docker end of veth tunnel. "
                    f"Error code {e.returncode} ({e})",
                )

        return ApplyReply(success=True)

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        # disable veth tunnel ends
        try:
            subprocess.check_call(
                f"sudo ip netns exec {configuration_item.docker_container_name} ip link set "
                f"{configuration_item.docker_interface_name} down",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to disable docker end of veth tunnel. Error code {e.returncode} ({e})",
            )
        try:
            subprocess.check_call(
                f"sudo ip link set {configuration_item.host_interface_name} down",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to disable host end of veth tunnel. Error code {e.returncode} ({e})",
            )
        # remove veth tunnel
        try:
            subprocess.check_call(
                f"sudo ip link delete {configuration_item.host_interface_name}",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to remove veth tunnel. Error code {e.returncode} ({e})",
            )

        # unlink docker container network namespace
        try:
            subprocess.check_call(
                f"sudo unlink /var/run/netns/{configuration_item.docker_container_name}",
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to unlink docker container network namespace. "
                f"Error code {e.returncode} ({e})",
            )

        return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        return dict()


class LinuxRouteHandler(ConfigurationItemHandler):
    def __init__(self):
        pass

    def is_handling_configuration_item(self, configuration_item):
        return isinstance(configuration_item, LinuxRouteConfigurationItem)

    @validate_config_item
    def get_labels(self, configuration_item):
        return set()  # noone uses it

    @validate_config_item
    def get_dependency_labels(self, configuration_item):
        return set()

    @validate_config_item
    def add_to_vpp(self, configuration_item):
        return self.add_remove_route(configuration_item, is_add=True)

    @validate_config_item
    def remove_from_vpp(self, configuration_item):
        return self.add_remove_route(configuration_item, is_add=False)

    def add_remove_route(self, configuration_item, is_add=True):
        add_or_remove = "add" if is_add else "del"
        basecmd = "{}ip route {} {}".format(
            (
                f"docker exec {configuration_item.docker_container_name} "
                if configuration_item.docker_container_name
                else "sudo "
            ),
            add_or_remove,
            configuration_item.destination_network,
        )
        via = (
            "via " + configuration_item.next_hop_address
            if configuration_item.next_hop_address
            else ""
        )
        dev = (
            "dev " + configuration_item.outgoing_interface
            if configuration_item.outgoing_interface
            else ""
        )
        cmd = " ".join([basecmd, via, dev])
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            return ApplyReply(
                success=False,
                error=f"Failed to {add_or_remove} linux route (cmd='{cmd}'). "
                f"Error code {e.returncode} ({e})",
            )

        return ApplyReply(success=True)

    @validate_config_item
    def dump_from_vpp(self, configuration_item):
        return dict()
