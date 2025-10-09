"""
All the model data classes and help constants/structures for public/inner API
"""

import base64
import ipaddress
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto, IntEnum
from typing import Dict, List, Any, Union

from dataclasses_json import dataclass_json, config
from marshmallow import fields

from vpp_vrouter.common import custom_marshmallow_fields

#################################
### Constants, variables
#################################

NO_INTERFACE_SW_INDEX = 0xFFFFFFFF
NO_ACL_INDEX = 0xFFFFFFFF
NO_WIREGUARD_PEER_INDEX = 0xFFFFFFFF
NOT_SET_MTU = -1
SW_IF_INDEX = "sw_if_index"
HOST_SW_IF_INDEX = "host_sw_if_index"
ACL_INDEX = "acl_index"
WIREGUARD_PEER_INDEX = "peer_index"
VPP_DUMP_KEY = "vpp_dump"
PCAP_ANY_INTERFACE = "any"
NO_PROTOCOL = -1

# Note: There is some problem with dynamic loading of "vl_api_if_status_flags_t" in VppEnum -> redefining constants
# from VPP API json files

IF_STATUS_API_FLAG_ADMIN_UP = (
    1  # VppEnum.vl_api_if_status_flags_t.IF_STATUS_API_FLAG_ADMIN_UP
)
IF_STATUS_API_FLAG_LINK_UP = (
    2  # VppEnum.vl_api_if_status_flags_t.IF_STATUS_API_FLAG_LINK_UP
)


class FibPathType:
    FIB_PATH_TYPE_NORMAL = 0
    FIB_PATH_TYPE_LOCAL = 1
    FIB_PATH_TYPE_DROP = 2
    FIB_PATH_TYPE_UDP_ENCAP = 3
    FIB_PATH_TYPE_BIER_IMP = 4
    FIB_PATH_TYPE_ICMP_UNREACH = 5
    FIB_PATH_TYPE_ICMP_PROHIBIT = 6
    FIB_PATH_TYPE_SOURCE_LOOKUP = 7
    FIB_PATH_TYPE_DVR = 8
    FIB_PATH_TYPE_INTERFACE_RX = 9
    FIB_PATH_TYPE_CLASSIFY = 10


class FibPathFlags:
    FIB_PATH_FLAG_NONE = 0
    FIB_PATH_FLAG_RESOLVE_VIA_ATTACHED = 1
    FIB_PATH_FLAG_RESOLVE_VIA_HOST = 2
    FIB_PATH_FLAG_POP_PW_CW = 4


class FibPathProto:
    FIB_PATH_NH_PROTO_IP4 = 0
    FIB_PATH_NH_PROTO_IP6 = 1
    FIB_PATH_NH_PROTO_MPLS = 2
    FIB_PATH_NH_PROTO_ETHERNET = 3
    FIB_PATH_NH_PROTO_BIER = 4
    FIB_PATH_NH_PROTO_NSH = 5


#################################
### Configuration models
#################################


class ConfigurationItem(ABC):
    """Abstraction of the smallest piece of configuration that can be applied to VPP/FRR/Linux namespace"""

    pass


class ConfigurationItemHandler(ABC):
    """Performs functionality related to one given class of ConfigurationItem.

    Covers interaction with VPP, dependency handling. It is inspired by descriptors in Ligato VPP-Agent repository
    (https://github.com/ligato/vpp-agent/blob/6c38360edf8285915202c8e4192e77a5efd71307/plugins/kvscheduler/api/kv_descriptor_api.go#L133)
    """

    @abstractmethod
    def add_to_vpp(self, configuration_item):
        """Applies configuration represented by configuration_item into VPP (or FRR or Linux namespace)"""
        pass

    @abstractmethod
    def remove_from_vpp(self, configuration_item):
        """Removes configuration represented by configuration_item from VPP (or FRR or Linux namespace)"""
        pass

    @abstractmethod
    def dump_from_vpp(self, configuration_item):
        """Retrieves configuration from VPP/FRR/Linux related to configuration represented by configuration_item"""
        pass

    @abstractmethod
    def is_handling_configuration_item(self, configuration_item):
        """Checks whenever this ConfigurationItemHandler handles given configuration_item. It can be used to find
        the correct ConfigurationItemHandler for given configuration_item or the guard method calls of given
        ConfigurationItemHandler against unexpected configuration_item input."""
        pass

    @abstractmethod
    def get_labels(self, configuration_item):
        """Provide labels for given configuration_item. Their presence represent correct application
        of the configuration_item into the VPP/FRR/Linux namespace. By referencing these labels, dependency connections
        can be established between configuration and correct ordering of configuration items can be achieved.
        (See get_dependency_labels(...))"""
        pass

    @abstractmethod
    def get_dependency_labels(self, configuration_item):
        """Provides labels of configuration items that given configuration item depends on. (see get_labels(...))"""
        pass


class VPPConfigUpdater(ABC):
    """Performs updates of existing ConfigurationItems already applied in VPP.

    This class should be used as alternative to delete correctly applied ConfigurationItem in VPP and that adding
    updated Configuration back to VPP. However, its main purpose is the make only necessary changes in VPP in compare
    to entire delete of entity and recreating it from scratch (i.e. update ip address of interface without deleting it
    and recreating it with new ip address)"""

    @abstractmethod
    def update_in_vpp(self, old_configuration_item, new_configuration_item):
        pass


class State(Enum):
    """State of configuration item that is sent to server from user using API."""

    RECEIVED = auto()
    """Just received, not processed yet. Initial state"""
    BLOCKED = auto()
    """Applying of configuration item to VPP/FRR/Linux namespace is blocked due to configuration dependency that 
    is not met yet. Waiting until all the dependencies are satisfied and only then trying to apply it."""
    BLOCKED_BY_ADD_APPLY_FAILURE = auto()
    """Similar as BLOCKED, but the reason is for blocking further action is failure/error from applying(adding) 
    to VPP/FRR/Linux namespace"""
    BLOCKED_BY_REMOVE_APPLY_FAILURE = auto()
    """Similar as BLOCKED, but the reason is for blocking further action is failure/error from applying(removing) 
    to VPP/FRR/Linux namespace"""
    BLOCKED_BY_UPDATE_APPLY_FAILURE = auto()
    """Similar as BLOCKED, but the reason is for blocking further action is failure/error from applying(updating) 
    to VPP/FRR/Linux namespace"""
    APPLIED = auto()
    """Configuration item is successfully applied to VPP/FRR/Linux namespace."""


class InterfaceType(Enum):
    UNDEFINED_TYPE = 0
    SUB_INTERFACE = 1
    SOFTWARE_LOOPBACK = 2
    DPDK = 3
    MEMIF = 4
    TAP = 5
    AF_PACKET = 6
    VXLAN_TUNNEL = 7
    IPSEC_TUNNEL = (
        8  # Deprecated in VPP 20.01 +.Use IPIP_TUNNEL + ipsec.TunnelProtection instead.
    )
    VMXNET3_INTERFACE = 9
    BOND_INTERFACE = 10
    GRE_TUNNEL = 11
    GTPU_TUNNEL = 12
    IPIP_TUNNEL = 13
    WIREGUARD_TUNNEL = 14
    RDMA = 15

    @staticmethod
    def get_from_vpp_str(vpp_if_type_str):
        match vpp_if_type_str:
            case "RDMA interface":
                return InterfaceType.RDMA
            case "local" | "loop":
                return InterfaceType.SOFTWARE_LOOPBACK
            case "memif":
                return InterfaceType.MEMIF
            case "tap" | "tun":
                return InterfaceType.TAP
            case "host":
                return InterfaceType.AF_PACKET
            case "vxlan":
                return InterfaceType.VXLAN_TUNNEL
            case "ipsec":
                return InterfaceType.IPSEC_TUNNEL
            case "vmxnet3":
                return InterfaceType.VMXNET3_INTERFACE
            case "Bond":
                return InterfaceType.BOND_INTERFACE
            case "gtpu":
                return InterfaceType.GTPU_TUNNEL
            case "ipip":
                return InterfaceType.IPIP_TUNNEL
            case "wireguard":
                return InterfaceType.WIREGUARD_TUNNEL
            case "dpdk":
                return InterfaceType.DPDK
            case "virtio":
                return (
                    InterfaceType.TAP
                )  # FIXME there could be non-tap virtio interfaces
            case _:
                return InterfaceType.DPDK


class GRELinkType(Enum):
    L3 = 0
    """L3 GRE - the tunnel is in L3 mode"""
    TEB = 1
    """Transaparent Ethernet Bridging - the tunnel is in L2 mode"""
    ERSPAN = 2
    """ERSPAN - the tunnel is for port mirror SPAN output"""


@dataclass_json
@dataclass
class GREInterfaceLink:
    type: GRELinkType = GRELinkType.L3
    """Type of GRE tunnel"""
    src_addr: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Source IP address"""
    dst_addr: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Destination IP address"""
    outer_fib_id: int = 0
    """Encapsulation FIB table ID"""
    session_id: int = 0
    """Session for tunnel of ERSPAN type, range 0-1023"""


@dataclass_json
@dataclass
class WireguardInterfaceLink:
    private_key: str = ""
    """Private-key encoded in base64"""
    port: int = 0
    """Listen UDP port"""
    src_addr: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Source IP address"""


@dataclass_json
@dataclass
class InterfaceConfigurationItem(ConfigurationItem):
    name: str
    type: InterfaceType = InterfaceType.TAP
    enabled: bool = True
    ip_addresses: List[str] = field(default_factory=lambda: [])
    mtu: int = NOT_SET_MTU
    """ MTU (Maximum Transmission Unit) of this interface"""
    # phys_address: str = '' # not used -> ignored
    link: Union[GREInterfaceLink, WireguardInterfaceLink, None] = None
    """Link defines configuration for specific interface types."""


class RouteType(Enum):
    INTRA_VRF = 0
    """Forwarding is being done in the specified vrf_id only, or according to
       the specified outgoing interface."""
    # INTER_VRF = 1
    # """ Forwarding is being done by lookup into a different VRF,
    #     specified as via_vrf_id field. In case of these routes, the outgoing
    #     interface should not be specified. The next hop IP address
    #     does not have to be specified either, in that case VPP does full
    #     recursive lookup in the via_vrf_id VRF."""
    DROP = 2
    """ Drops the network communication designated for specific IP address."""


@dataclass_json
@dataclass
class RouteOutputPath:
    """Output path part of route. It should be used to define multiple output possibilities for route. That means when
    you want to steer some packets for given network prefix into route loadbalancer that uses multiple outputs (i.e.
    multiple wg tunnels)"""

    next_hop_address: str = ""
    """ Next hop ip address """
    outgoing_interface: str = ""
    """ Name of outgoing interface that should be used for this route. """
    weight: int = 1
    """ Weight is used for unequal cost load balancing (uint32 in vpp)."""  # OSPF learned paths can use this


@dataclass_json
@dataclass
class RouteConfigurationItem(ConfigurationItem):
    type: RouteType = RouteType.INTRA_VRF
    """ Type of route defining route behaviour. See RouteType."""
    destination_network: str = ""
    """ Destination ip network for steering traffic using this route. 
    It has format <ip address>/<prefix> (i.e. "10.1.2.0/24)."""
    next_hop_address: str = ""
    """ Next hop ip address """
    outgoing_interface: str = ""
    """ Name of outgoing interface that should be used for this route. """
    weight: int = 1
    """ Weight is used for unequal cost load balancing (uint32 in vpp)."""  # OSPF learned paths can use this
    multi_output_paths: List[RouteOutputPath] = field(default_factory=lambda: [])
    """ Definition for multiple output paths for route. If output path is only one, use the direct fields 
    in RouteConfigurationItem. When this field is used, the direct duplicated direct fields in RouteConfigurationItem 
    will be ignored and only multi_output_paths will be used."""
    # NOT USED or MEANINGLESS for given usecases:
    #
    # vrf_id: int = 0 # ignored as all routes should use vrf 0
    #
    # preference:int
    # """ Preference defines path preference. Lower preference is preferred.
    # Only paths with the best preference contribute to forwarding (a poor man's primary and backup).
    # It is uint32 in vpp."""
    #
    # via_vrf_id: int
    # """ Specifies VRF ID for the next hop lookup / recursive lookup. It is uint32 in vpp."""


class ACLAction(Enum):
    DENY = 0
    PERMIT = 1
    REFLECT = 2


@dataclass_json
@dataclass
class ICMPRange:
    """Range for ICMP codes and types
    See https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml"""

    first: int = 0  # minimum: 0 maximum: 255
    last: int = 255  # minimum: 0 maximum: 255


@dataclass_json
@dataclass
class ICMPProtocol:
    icmpv6: bool = False
    """ICMPv6 flag, if false ICMPv4 will be used"""
    icmp_code_range: ICMPRange = field(default_factory=lambda: ICMPRange())
    """Inclusive range representing icmp codes to be used"""
    icmp_type_range: ICMPRange = field(default_factory=lambda: ICMPRange())
    """Inclusive range representing icmp types to be used"""


@dataclass_json
@dataclass
class PortRange:
    """Inclusive range representing destination ports to be used.
    When only lower-port is present, it represents a single port."""

    lower_port: int = 0  # minimum: 0 maximum: 65535
    upper_port: int = 65535  # minimum: 0 maximum: 65535


@dataclass_json
@dataclass
class TCPProtocol:
    destination_port_range: PortRange = field(default_factory=lambda: PortRange())
    source_port_range: PortRange = field(default_factory=lambda: PortRange())
    tcp_flags_mask: int = 0  # minimum: 0 maximum: 255
    """ Binary mask for tcp flags to match. MSB order (FIN at position 0).
    Applied as logical AND to tcp flags field of the packet being matched,
    before it is compared with tcp-flags-value.
    """
    tcp_flags_value: int = 0  # minimum: 0 maximum: 255
    """ Binary value for tcp flags to match. MSB order (FIN at position 0).
    Before tcp-flags-value is compared with tcp flags field of the packet being matched,
    tcp-flags-mask is applied to packet field value.
    """


@dataclass_json
@dataclass
class UDPProtocol:
    destination_port_range: PortRange = field(default_factory=lambda: PortRange())
    source_port_range: PortRange = field(default_factory=lambda: PortRange())


@dataclass_json
@dataclass
class OtherProtocol:
    """ACL rule's packet selector based on IP protocol.
    For ICMP,TCP,UDP protocol selection use custome designed packet selectors (ICMPProtocol,TCPProtocol,UDPProtocol).
    """

    protocol: int = 0
    """ IP protocol number (http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml) defining protocol 
    filtering for ACL rules"""


@dataclass_json
@dataclass
class IPAddresses:
    destination_network: ipaddress.IPv4Network = field(
        default_factory=lambda: ipaddress.IPv4Network("0.0.0.0/0")
    )  # FIXME no support for IPv6 in ACL
    """ Destination IPv4/IPv6 network address (<ip>/<network>) """
    source_network: ipaddress.IPv4Network = field(
        default_factory=lambda: ipaddress.IPv4Network("0.0.0.0/0")
    )
    """ Destination IPv4/IPv6 network address (<ip>/<network>) """


@dataclass_json
@dataclass
class IPSpecification:
    addresses: Union[IPAddresses, None] = None
    protocol: Union[ICMPProtocol, TCPProtocol, UDPProtocol, OtherProtocol, None] = None


@dataclass_json
@dataclass
class ACLRuleConfigurationItem:
    action: ACLAction = ACLAction.DENY
    refinement: Union[IPSpecification, None] = None
    # Note: ignoring MAC ACL rules(MAcSpecification) as they are not
    # needed for failover case->ACLRuleConfigurationItem=IP-based Rule


@dataclass_json
@dataclass
class ACLConfigurationItem(ConfigurationItem):
    name: str = ""
    rules: List[ACLRuleConfigurationItem] = field(
        default_factory=lambda: [ACLRuleConfigurationItem()]
    )
    egress: List[str] = field(
        default_factory=lambda: []
    )  # TODO map ACL to interfaces in implementation
    """Names of egress interfaces"""
    ingress: List[str] = field(default_factory=lambda: [])
    """Names of ingress interfaces"""


# NAT44 parts ignored from Ligato's vpp-agent nat44 proto models:
# message Nat44Global {
#     // Enable/disable forwarding. By default it is disabled.
#     bool forwarding = 1;
#     // Enable/disable endpoint-independent mode. by default disabld.
#     bool endpoint_independent = 5;
#     // Virtual reassembly for IPv4.
#     VirtualReassembly virtual_reassembly = 4;
# }


# numbers from: http://www.iana.org/assignments/protocol-numbers
# defined for VPP v22.10.1 in file src/vnet/ip/protocols.def
class ProtocolInNAT(IntEnum):
    """Available protocols that can be used in NAT configuration"""

    TCP = 6
    UDP = 17
    ICMP = 1


@dataclass_json
@dataclass
class LocalIP:
    """LocalIP defines a local IP addresses."""

    # We use only one VRF in failover case
    # vrf_id:int = 0
    # """VRF (table) ID. Non-zero VRF has to be explicitly created (see api/models/vpp/l3/vrf.proto)."""
    local_ip: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Local IP address"""
    local_port: int = 0
    """Port (do not set for address mapping)."""
    probability: int = 0
    """Probability level for load-balancing mode."""


@dataclass_json
@dataclass
class StaticMapping:
    """StaticMapping defines a list of static mappings in DNAT."""

    external_interface: str = ""
    """Interface to use external IP from; preferred over external_ip."""
    external_ip: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """External IPV4 address."""
    external_port: int = 0
    """Port (do not set for address mapping)."""
    local_ips: List[LocalIP] = field(default_factory=lambda: [])
    """List of local IP addresses. If there is more than one entry, load-balancing is enabled."""
    protocol: ProtocolInNAT = ProtocolInNAT.TCP
    """Protocol used for static mapping."""

    # Not using twice-nat in failover case
    # class TwiceNatMode(Enum):
    #     DISABLED = 0
    #     ENABLED = 1
    #     SELF = 2
    #
    # twice_nat:TwiceNatMode = TwiceNatMode.DISABLED
    # """Enable/disable (self-)twice NAT."""
    # twice_nat_pool_ip:str = ''
    # """IP address from Twice-NAT address pool that should be used as source IP in twice-NAT processing.
    #    This is override for default behaviour of choosing the first IP address from twice-NAT pool that
    #    has available at least one free port (NAT is tracking translation sessions and exhausts free ports
    #    for given IP address). This is needed for example in use cases when multiple twice-NAT
    #    translations need to use different IP Addresses as source IP addresses.
    #    This functionality works with VPP 20.09 and newer. It also needs to have twice_nat set to ENABLED.
    #    It doesn't work for load-balanced static mappings (=local_ips has multiple values)."""

    # Not used in failover case
    # session_affinity:int = 0
    # """Session affinity. 0 means disabled, otherwise client IP affinity sticky time in seconds."""


@dataclass_json
@dataclass
class IdentityMapping:
    """IdentityMapping defines an identity mapping in DNAT."""

    # We use only one VRF in failover case
    # vrf_id:int = 0
    # """VRF (table) ID. Non-zero VRF has to be explicitly created (see api/models/vpp/l3/vrf.proto)."""
    interface: str = ""
    """Name of the interface to use address from; preferred over ip_address."""
    ip_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """IPv4 address"""
    port: int = 0
    """Port (do not set for address mapping)"""
    protocol: ProtocolInNAT = ProtocolInNAT.TCP
    """Protocol used for identity mapping."""


@dataclass_json
@dataclass
class DNat44ConfigurationItem(ConfigurationItem):
    """DNat44 defines destination NAT44 configuration."""

    label: str = ""
    """Unique identifier for the DNAT configuration."""
    static_mappings: List[StaticMapping] = field(default_factory=lambda: [])
    """A list of static mappings in DNAT."""
    identity_mappings: List[IdentityMapping] = field(default_factory=lambda: [])
    """A list of identity mappings in DNAT."""


@dataclass_json
@dataclass
class Nat44InterfaceConfigurationItem(ConfigurationItem):
    """Nat44Interface defines a local network interfaces enabled for NAT44."""

    name: str = ""
    """interface name (logical)."""
    nat_inside: bool = False
    """Enable/disable NAT on inside."""
    nat_outside: bool = False
    """Enable/disable NAT on outside."""
    output_feature: bool = False
    """Enable/disable output feature."""


@dataclass_json
@dataclass
class Nat44AddressPoolConfigurationItem(ConfigurationItem):
    """Nat44AddressPool defines an address pool used for NAT44."""

    name: str = ""
    """Unique name for address pool"""
    # We use only one VRF in failover case
    # vrf_id: int = 0
    # """ VRF id of tenant, 0xFFFFFFFF means independent of VRF.
    # Non-zero (and not all-ones) VRF has to be explicitly created (see api/models/vpp/l3/vrf.proto)."""
    first_ip: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """First IP address of the pool"""
    last_ip: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Last IP address of the pool. Should be higher than first_ip or empty."""
    # Not using twice-nat in failover case
    # twice_nat: bool = False
    # """Enable/disable twice NAT."""


class WireguardPeerFlags(IntEnum):
    NO_FLAGS = 0
    STATUS_DEAD = 1
    ESTABLISHED = 2


@dataclass_json
@dataclass
class WireguardPeerConfigurationItem(ConfigurationItem):
    public_key: str = ""
    """Public-key base64"""
    port: int = 0
    """Peer UDP port"""
    endpoint: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    """Endpoint IP"""
    allowed_ips: List[str] = field(default_factory=lambda: [])
    """Allowed IPs for peer. Use ip address prefixes, i.e. ["10.1.2.0/24"]. To enable all ip addresses use 
    ["0.0.0.0/0"]"""
    wg_if_name: str = ""
    """The name of the wireguard interface to which this peer belongs"""
    flags: int = int(WireguardPeerFlags.NO_FLAGS)
    """Flags. Like int(WireguardPeerFlags.STATUS_DEAD)"""
    persistent_keepalive: int = 10
    """Keepalive interval (sec)"""


@dataclass_json
@dataclass
class FRRConfigurationItem(ConfigurationItem):
    """Configuration of FRR instance"""

    config: str = ""
    """String that represent the whole FRR configuration file content."""


@dataclass_json
@dataclass
class KeaConfigRequest:
    """Request sent to KEA DHCP server."""

    command: str
    arguments: Dict = field(default_factory=lambda: (dict()))


@dataclass_json
@dataclass
class KeaConfigResponse:
    """Response from KEA DHCP server to some request(see KeaConfigRequest)"""

    result: int
    """	Status code of the request processing. Zero means success and non-zero failure (see 
    https://kea.readthedocs.io/en/kea-2.5.0/arm/ctrl-channel.html#data-syntax)
    """

    text: str = ""
    """ Description of the occurred error """

    arguments: Dict = field(default_factory=lambda: (dict()))
    """ Additional data, i.e. whole config in case of "config-get" command in request """


@dataclass_json
@dataclass
class DHCPConfigurationItem(ConfigurationItem):
    """Configuration of DHCP instance"""

    config: str = ""
    """String that represent the whole DHCP configuration file content."""

    restart_before_config_apply: bool = False
    """Switch for restarting the DHCP before applying the config field. This is workaround for DHCP server not able to 
    pickup interface created after its start. This is false by default, because normally only initial configuration 
    will need this (DHCP starts before interface creation linking it to VPP)."""

    strip_comment_lines: bool = True
    """Strips comment lines (every line with // inside) from config string before applying it to DHCP server. This is 
    needed because config input is pure JSON and this format there are not comments allowed. Comment stripping can be 
    also done on client side if needed (and turning server-side comment stripping off). """


@dataclass_json
@dataclass
class LCPGlobalsConfigurationItem(ConfigurationItem):
    """Global settings for LCP"""

    default_namespace: str = ""
    lcp_sync: bool = True
    """Enables copying of changes made in VPP into their Linux counterpart"""
    lcp_auto_subint: bool = False
    """When enabled, sub-interface creation in VPP automatically creates a Linux Interface Pair(LIP) and 
    its companion Linux network interface"""


class LCPHostInterfaceTypeEnum(IntEnum):  # vl_api_lcp_itf_host_type_t
    TAP = 0
    TUN = 1


@dataclass_json
@dataclass
class LCPPairConfigurationItem(ConfigurationItem):
    interface: str = ""
    """Interface in VPP that should be mirrored into linux namespace"""
    mirror_interface_host_name: str = ""
    """Name of host(linux) interface (host end of tap/tun tunnel from VPP) that is mirroring of VPP interface 
    (LCPPairConfigurationItem.interface)"""
    mirror_interface_type: LCPHostInterfaceTypeEnum = LCPHostInterfaceTypeEnum.TAP
    """Interface type of host(linux) interface (host end of tap/tun tunnel from VPP) that is mirroring of VPP interface 
    (LCPPairConfigurationItem.interface)"""
    host_namespace: str = ""
    """Host/Linux namespace where the VPP interface(LCPPairConfigurationItem.interface) should be mirrored"""


@dataclass_json
@dataclass
class L2PacketMatchingRule:
    src_physical_address: str = ""
    """Frame source physical address to match by. Leave empty you don't want to match frames by this."""
    dest_physical_address: str = ""
    """Frame destination physical address to match by. Leave empty you don't want to match frames by this."""
    protocol: int = NO_PROTOCOL
    """L2 protocol number to match by (see https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def 
    for L2 protocol numbers). Use NO_PROTOCOL to not filted by protocol. Use decimal format of protocol numbers."""


@dataclass_json
@dataclass
class L3PacketMatchingRule:
    src_ipv4_address: str = ""
    """Packet source IPv4 address to match by. Leave empty you don't want to match frames by this."""
    dest_ipv4_address: str = ""
    """Packet destination IPv4 address to match by. Leave empty you don't want to match frames by this."""
    protocol: int = NO_PROTOCOL
    """L3 protocol number to match by (see https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml 
    for protocol numbers). Use NO_PROTOCOL to not filted by protocol. Use decimal format of protocol numbers."""


@dataclass_json
@dataclass
class RunningPacketCapture(ConfigurationItem):
    """Configuration of running packet capturing.

    By adding this configuration, packet capturing is started with given configuration settings. By removing it,
    the packet capturing is stopped and content of local packet buffer written to output file.
    Check VPP documentation for further configuration explanation:
    https://s3-docs.fd.io/vpp/22.06/cli-reference/clis/clicmd_src_vnet.html#pcap-trace,
    https://s3-docs.fd.io/vpp/22.06/developer/corearchitecture/vnet.html?highlight=pcap#pcap-rx-tx-and-drop-tracing
    https://s3-docs.fd.io/vpp/22.06/developer/corearchitecture/vnet.html?highlight=pcap#terse-description-of-the-mask-syntax

    (Note: documentation is outdated, therefore not all CLI calls can work in VPP 22.06)
    """

    output_file_prefix: str = "pcap-capture"
    """Prefix for packet capture output file. The resulting file will be in format 
    /tmp/<output_file_prefix>-<datetime-suffix>.pcap (the /tmp folder is fixed by VPP 22.06 implementation)"""

    max_packets_to_capture: int = 1000  # 1000 packets is VPP default
    """Packet-depth of local data buffer. Once the local buffer gets full, no more packets are captured. By removing 
    this whole configuration the packets capturing will be stopped and content of local buffer is flushed to file.
    
    Note: official VPP documentation tells that local buffer is flushed to file when it gets full, but that never 
    happens in VPP 22.02"""  # TODO Note still applies for VPP 22.10.1 that is used now ?
    max_bytes_per_packet: int = 9000
    """Maximum number of bytes to capture for each packet. Must be >= 32, <= 9000."""
    preallocate_data_buffer: bool = True
    """Preallocate the data buffer, to avoid vector expansion delays during pcap capture"""
    free_data_buffer: bool = False
    """Free the data buffer. Ordinarily it’s a feature to retain the data buffer so this option is seldom used."""

    # packet capture options (can use multiple of them at the same time to specify what packets you want to capture)

    capture_rx_packets: bool = True
    capture_tx_packets: bool = True
    capture_dropped_packets: bool = True
    capture_only_from_interface: str = PCAP_ANY_INTERFACE
    """Limiting capturing of packets to given interface (or using traffic from all interfaces if 
    PCAP_ANY_INTERFACE is used)"""
    capture_by_matching_rules: List[
        Union[L2PacketMatchingRule, L3PacketMatchingRule]
    ] = field(default_factory=lambda: [])
    """Match rules that will be applied for capturing packets. Only packets that match all rules(together with other 
    capturing restrictions from other RunningPacketCapture's fields) will be captured. You can combine multiple 
    L2/L3 rules."""  # (NOTE: There are L4 matching rules according to documentation, but they didn't work in VPP, giving error while defining any L4 rule)


@dataclass_json
@dataclass
class LinuxDockerVethTunnelConfigurationItem(ConfigurationItem):
    """Configuration for creating veth tunnel in linux (with one end in default linux namespace and other in docker
    container)"""

    docker_container_name: str = ""
    """Name of the docker container that should have one end of the veth tunnel"""
    host_interface_name: str = "host-veth"
    docker_interface_name: str = "veth"
    host_interface_ip_addresses: List[str] = field(default_factory=lambda: [])
    docker_interface_ip_addresses: List[str] = field(default_factory=lambda: [])


@dataclass_json
@dataclass
class LinuxRouteConfigurationItem(ConfigurationItem):
    """Configuration of static route in linux namespace (default linux namespace or docker container linux namespace)"""

    docker_container_name: str = ""
    """ Name of docker container into which you want to put linux route. Use empty string if the default linux network 
    namespace(linux host) should be used."""
    destination_network: str = ""
    """ Destination ip network for steering traffic using this route. 
    It has format <ip address>/<prefix> (i.e. "10.1.2.0/24)."""
    next_hop_address: str = ""
    """ Next hop ip address """
    outgoing_interface: str = ""
    """ Name of outgoing interface that should be used for this route. """


#################################
### API reply models
#################################


@dataclass_json
@dataclass
class ApplyReply:
    """Reply when applying configuration_item in handlers"""

    success: bool = False
    """Whether the appying was successfull or not"""
    error: str = ""
    """Error message if not success"""
    vpp_data: Dict[str, any] = field(default_factory=lambda: (dict()))
    """Additional data linked to the reply"""


@dataclass_json
@dataclass
class ConfigurationItemDetail:
    """ConfigurationItemRecord (internal configuration data structure) stripped of internal fields and ready for
    publishing to user through client API (get_configuration)"""

    # Note: normally ConfigurationItem should be used but that is prevented by serialization/deserialization
    # problems with combination of used libraries (Pyro5, dataclass-json) -> must list
    # all children of ConfigurationItem in Union
    config: Union[
        InterfaceConfigurationItem,
        RouteConfigurationItem,
        ACLConfigurationItem,
        Nat44AddressPoolConfigurationItem,
        Nat44InterfaceConfigurationItem,
        DNat44ConfigurationItem,
        WireguardPeerConfigurationItem,
        LCPGlobalsConfigurationItem,
        LCPPairConfigurationItem,
        FRRConfigurationItem,
        LinuxDockerVethTunnelConfigurationItem,
        LinuxRouteConfigurationItem,
        DHCPConfigurationItem,
    ]
    state: State
    metadata: Dict[str, Any] = field(default_factory=lambda: (dict()))


@dataclass_json
@dataclass
class ConfigurationItemReply(ConfigurationItemDetail):
    """ConfigurationItemDetail with added error from applying configuration item to VPP/FRR/Linux namespace"""

    error: str = ""


@dataclass_json
@dataclass
class AddConfigurationItemsReply:
    """Reply from applying configuration item using client.add_configuration"""

    processing_error: str = ""
    """Error that doesn't come from VPP/FRR/Linux namespace call, but is related to server processing of the request 
    (i.e. invalid input)"""
    all_added_items_applied_to_vpp: bool = True
    """Whether all configuration items given on client.add_configuration input were applied to VPP/FRR/Linux namespace 
    successfully (without any error). It is computed from added_items field."""
    added_items: List[ConfigurationItemDetail] = field(default_factory=lambda: [])
    """Server state of input configuration items after processing in server (see ConfigurationItemDetail). It can be 
    used to get current state of configuration items and more."""
    vpp_apply_success: bool = True
    """Whether all configuration in vpp_apply_attempted_items was applied or not. It is computed 
    from vpp_apply_attempted_items field."""
    vpp_apply_attempted_items: List[ConfigurationItemReply] = field(
        default_factory=lambda: []
    )
    """Server state of all configuration that can be applied (either was unblocked by satisfying configuration 
    dependencies or are new configuration items that are not blocked by dependency restriction). This configuration is 
    applied and you can use this inner server state (that is after applying) to check from success and more."""


@dataclass_json
@dataclass
class DeleteConfigurationItemsReply:
    """Reply from applying configuration item using client.delete_configuration"""

    processing_error: str = ""
    """Error that doesn't come from VPP/FRR/Linux namespace call, but is related to server processing of the request 
    (i.e. invalid input)"""
    vpp_apply_success: bool = True
    """Whether all configuration items given on client.delete_configuration input were applied(removal) 
    to VPP/FRR/Linux namespace successfully (without any error). It is computed from vpp_apply_attempted_items field."""
    vpp_apply_attempted_items: List[ConfigurationItemReply] = field(
        default_factory=lambda: []
    )
    """Server state of input configuration items after processing in server (see ConfigurationItemDetail). It can be 
    used to get current state of configuration items and more. These information (in case of successfully removal) are 
    removed from server and will be missing from retrieved data from get_configuration() call."""


@dataclass_json
@dataclass
class UpdateConfigurationItemsReply:
    """Reply from applying configuration item using client.update_configuration"""

    processing_error: str = ""
    """Error that doesn't come from VPP/FRR/Linux namespace call, but is related to server processing of the request 
    (i.e. invalid input)"""
    all_updated_items_applied_to_vpp: bool = True
    """Similar to AddConfigurationItemsReply.all_added_items_applied_to_vpp"""
    updated_items: List[ConfigurationItemDetail] = field(default_factory=lambda: [])
    """Similar to AddConfigurationItemsReply.added_items"""
    vpp_apply_success: bool = True
    """Similar to (AddConfigurationItemsReply.vpp_apply_success and DeleteConfigurationItemsReply.vpp_apply_success)"""
    vpp_apply_attempted_items: List[ConfigurationItemReply] = field(
        default_factory=lambda: []
    )
    """Similar to (AddConfigurationItemsReply.vpp_apply_attempted_items and 
    DeleteConfigurationItemsReply.vpp_apply_attempted_items)"""


@dataclass_json
@dataclass
class GetConfigurationItemsReply:
    """Reply from applying configuration item using client.get_configuration"""

    items: List[ConfigurationItemDetail] = field(default_factory=lambda: [])
    """Server state of all configuration items that server currently knows."""


@dataclass_json
@dataclass
class ProcessCallReply:
    """Reply that transport subprocess run result"""

    return_code: int = 0
    """subprocess run result code"""
    stdout: str = ""
    """subprocess run's stdout"""
    stderr: str = ""
    """subprocess run's stderr"""


#################################
### Dump models
#################################


@dataclass_json
@dataclass
class SWInterfaceDetail:
    b_dmac: str = ""
    b_smac: str = ""
    b_vlanid: int = 0
    context: int = 0
    flags: int = 0
    i_sid: int = 0
    interface_dev_type: str = ""
    interface_name: str = ""
    l2_address: str = ""
    link_duplex: int = 0  # i.e. <vl_api_link_duplex_t.LINK_DUPLEX_API_UNKNOWN: 0>
    link_mtu: int = 0
    link_speed: int = 0
    mtu: list[int] = field(default_factory=lambda: [])
    outer_tag: int = 0
    sub_id: int = 0
    sub_if_flags: int = 0
    sub_inner_vlan_id: int = 0
    sub_number_of_tags: int = 0
    sub_outer_vlan_id: int = 0
    sup_sw_if_index: int = 0
    sw_if_index: int = 0
    tag: str = ""
    type: int = 0  # i.e. <vl_api_if_type_t.IF_API_TYPE_HARDWARE: 0>
    vtr_op: int = 0
    vtr_push_dot1q: int = 0
    vtr_tag1: int = 0
    vtr_tag2: int = 0

    def is_link_state_up(self):
        return True if self.flags & IF_STATUS_API_FLAG_LINK_UP else False

    def is_admin_state_up(self):
        return True if self.flags & IF_STATUS_API_FLAG_ADMIN_UP else False

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return SWInterfaceDetail(
            b_dmac=obj.b_dmac,
            b_smac=obj.b_smac,
            b_vlanid=obj.b_vlanid,
            context=obj.context,
            i_sid=obj.i_sid,
            interface_dev_type=obj.interface_dev_type,
            interface_name=obj.interface_name,
            l2_address=obj.l2_address,
            link_mtu=obj.link_mtu,
            link_speed=obj.link_speed,
            outer_tag=obj.outer_tag,
            sub_id=obj.sub_id,
            sub_inner_vlan_id=obj.sub_inner_vlan_id,
            sub_number_of_tags=obj.sub_number_of_tags,
            sub_outer_vlan_id=obj.sub_outer_vlan_id,
            sup_sw_if_index=obj.sup_sw_if_index,
            sw_if_index=obj.sw_if_index,
            tag=obj.tag,
            vtr_op=obj.vtr_op,
            vtr_push_dot1q=obj.vtr_push_dot1q,
            vtr_tag1=obj.vtr_tag1,
            vtr_tag2=obj.vtr_tag2,
            link_duplex=int(
                obj.link_duplex
            ),  # i.e. <vl_api_link_duplex_t.LINK_DUPLEX_API_UNKNOWN: 0>
            type=int(obj.type),  # i.e. <vl_api_if_type_t.IF_API_TYPE_HARDWARE: 0>
            flags=int(obj.flags),  # typing.Set[VppEnum.vl_api_if_status_flags_t]
            mtu=obj.mtu,
            sub_if_flags=int(
                obj.sub_if_flags
            ),  # typing.Set[VppEnum.vl_api_sub_if_flags_t]
        )


@dataclass_json
@dataclass
class FibPathNextHop:  # vl_api_fib_path_nh_t
    ipv4_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    ipv6_address: ipaddress.IPv6Address = field(
        default_factory=lambda: ipaddress.IPv6Address("::"),
        metadata=config(mm_field=fields.IPv6()),
    )

    classify_table_index: int = 0
    obj_id: int = 0
    via_label: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return FibPathNextHop(
            ipv4_address=obj.address.ip4,
            ipv6_address=obj.address.ip6,
            classify_table_index=obj.classify_table_index,
            obj_id=obj.obj_id,
            via_label=obj.via_label,
        )


@dataclass_json
@dataclass
class FibPath:  # vl_api_fib_path_t
    flags: int = 0  # vl_api_fib_path_flags_t
    # label_stack: List[vl_api_fib_mpls_label_t]
    # n_labels: int = 0
    nh: typing.Union[FibPathNextHop, None] = None
    preference: int = 0
    proto: int = 0  # vl_api_fib_path_nh_proto_t
    rpf_id: int = 0
    sw_if_index: int = 4294967295
    table_id: int = 0
    type: int = 0  # vl_api_fib_path_type_t
    weight: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return FibPath(
            flags=int(obj.flags),
            nh=(
                FibPathNextHop.get_from_basic_vpp_client_equivalent_obj(obj.nh)
                if obj.nh
                else None
            ),
            preference=int(obj.preference),
            proto=int(obj.proto),
            rpf_id=int(obj.rpf_id),
            sw_if_index=int(obj.sw_if_index),
            table_id=int(obj.table_id),
            type=int(obj.type),
            weight=int(obj.weight),
        )


@dataclass_json
@dataclass
class IPRouteDetail:  # ignoring context, using only route field of type vl_api_ip_route_t
    n_paths: int = 0
    paths: List[FibPath] = field(default_factory=lambda: [])
    prefix: ipaddress.IPv4Network = field(
        default_factory=lambda: ipaddress.IPv4Network("0.0.0.0/0"),
        metadata=config(
            mm_field=custom_marshmallow_fields.IPv4Network()  # missing in builtin marshmallow fields
        ),
    )
    stats_index: int = 0
    table_id: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return IPRouteDetail(
            n_paths=obj.route.n_paths,
            paths=[
                FibPath.get_from_basic_vpp_client_equivalent_obj(path)
                for path in obj.route.paths
            ],
            prefix=obj.route.prefix,
            stats_index=obj.route.stats_index,
            table_id=obj.route.table_id,
        )


@dataclass_json
@dataclass
class ACLRule:  # vl_api_acl_rule_t
    is_permit: int = 0  # vl_api_acl_action_t
    dst_prefix: ipaddress.IPv4Network = ipaddress.IPv4Network("0.0.0.0/0")
    src_prefix: ipaddress.IPv4Network = ipaddress.IPv4Network("0.0.0.0/0")
    dstport_or_icmpcode_first: int = 0
    dstport_or_icmpcode_last: int = 0
    srcport_or_icmptype_first: int = 0
    srcport_or_icmptype_last: int = 0
    proto: int = 0  # vl_api_ip_proto_t
    tcp_flags_mask: int = 0
    tcp_flags_value: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return ACLRule(
            is_permit=obj.is_permit,
            dst_prefix=obj.dst_prefix,
            src_prefix=obj.src_prefix,
            dstport_or_icmpcode_first=obj.dstport_or_icmpcode_first,
            dstport_or_icmpcode_last=obj.dstport_or_icmpcode_last,
            srcport_or_icmptype_first=obj.srcport_or_icmptype_first,
            srcport_or_icmptype_last=obj.srcport_or_icmptype_last,
            proto=obj.proto,
            tcp_flags_mask=obj.tcp_flags_mask,
            tcp_flags_value=obj.tcp_flags_value,
        )


@dataclass_json
@dataclass
class ACLDetails:  # acl_details
    acl_index: int = 0
    tag: str = ""
    count: int = 0  # rules count
    r: List[ACLRule] = field(default_factory=lambda: [])  # rules

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return ACLDetails(
            acl_index=obj.acl_index,
            tag=obj.tag,
            count=obj.count,
            r=[
                ACLRule.get_from_basic_vpp_client_equivalent_obj(rule) for rule in obj.r
            ],
        )


@dataclass_json
@dataclass
class NAT44AddressDetails:  # nat44_address_details
    flags: int = 0  # vl_api_nat_config_flags_t
    ip_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )

    # vrf_id: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return NAT44AddressDetails(
            flags=int(obj.flags),
            ip_address=obj.ip_address,
        )


@dataclass_json
@dataclass
class NAT44InterfaceDetails:  # nat44_interface_details
    flags: int = 0  # vl_api_nat_config_flags_t
    sw_if_index: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return NAT44InterfaceDetails(
            flags=int(obj.flags),
            sw_if_index=obj.sw_if_index,
        )


@dataclass_json
@dataclass
class NAT44StaticMappingDetails:  # nat44_static_mapping_details
    external_sw_if_index: int = 0
    external_ip_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    external_port: int = 0
    local_ip_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    local_port: int = 0
    protocol: int = 0
    tag: str = ""
    flags: int = 0  # vl_api_nat_config_flags_t

    # vrf_id: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return NAT44StaticMappingDetails(
            external_sw_if_index=obj.external_sw_if_index,
            external_ip_address=obj.external_ip_address,
            external_port=obj.external_port,
            local_ip_address=obj.local_ip_address,
            local_port=obj.local_port,
            protocol=obj.protocol,
            tag=obj.tag,
            flags=obj.flags,
        )


@dataclass_json
@dataclass
class NAT44IdentityMappingDetails:  # nat44_identity_mapping_details
    sw_if_index: int = 0
    ip_address: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    port: int = 0
    protocol: int = 0
    tag: str = ""
    flags: int = 0  # vl_api_nat_config_flags_t

    # vrf_id: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return NAT44IdentityMappingDetails(
            sw_if_index=obj.sw_if_index,
            ip_address=obj.ip_address,
            port=obj.port,
            protocol=obj.protocol,
            tag=obj.tag,
            flags=obj.flags,
        )


@dataclass_json
@dataclass
class WireguardPeerDetail:  # vl_api_wireguard_peer_t (=peer attribute from dump returning wireguard_peers_details)
    endpoint: ipaddress.IPv4Address = field(
        default_factory=lambda: ipaddress.IPv4Address("0.0.0.0"),
        metadata=config(mm_field=fields.IPv4()),
    )
    port: int = 0
    n_allowed_ips: int = 0
    allowed_ips: List[ipaddress.IPv4Network] = field(default_factory=lambda: [])
    public_key: str = ""
    """Base64 encoded public key"""
    sw_if_index: int = 0
    persistent_keepalive: int = 0
    flags: int = 0  # vl_api_wireguard_peer_flags_t
    table_id: int = 0

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return WireguardPeerDetail(
            endpoint=obj.endpoint,
            port=obj.port,
            n_allowed_ips=obj.n_allowed_ips,
            allowed_ips=obj.allowed_ips,
            public_key=base64.b64encode(obj.public_key).decode(),
            sw_if_index=obj.sw_if_index,
            persistent_keepalive=obj.persistent_keepalive,
            flags=int(obj.flags),
            table_id=obj.table_id,
        )


@dataclass_json
@dataclass
class LCPPairDetail:  # lcp_itf_pair_details
    phy_sw_if_index: int = 0
    host_sw_if_index: int = 0
    vif_index: int = (0,)
    host_if_name: str = ""
    host_if_type: int = 0  # vl_api_lcp_itf_host_type_t
    netns: str = ""

    @staticmethod
    def get_from_basic_vpp_client_equivalent_obj(obj):
        """Static conversion of non-persistable result of VPP dump call into modeled and persistable version
        of the same data"""

        return LCPPairDetail(
            phy_sw_if_index=obj.phy_sw_if_index,
            host_sw_if_index=obj.host_sw_if_index,
            vif_index=obj.vif_index,
            host_if_name=obj.host_if_name,
            host_if_type=int(obj.host_if_type),  # vl_api_lcp_itf_host_type_t
            netns=obj.netns,
        )


# VPP Stats related models

class VPPStatsType(Enum):
    """Types of VPP statistics that can be collected"""
    SCALAR = "scalar"
    COUNTER_VECTOR_SIMPLE = "counter_vector_simple"
    COUNTER_VECTOR_COMBINED = "counter_vector_combined"
    ERROR_INDEX = "error_index"
    NAME_VECTOR = "name_vector"


@dataclass_json
@dataclass

@dataclass_json
@dataclass
class VPPStatsQuery:
    """Transient (non-persisted) VPP statistics query.

    This model supersedes VPPStatsConfigurationItem for one-off stats retrieval via
    ExtendedVPPAPIClient.get_vpp_stats(). It is NOT a ConfigurationItem and is never
    stored server-side.

    Parameters:
      patterns: Optional explicit list of stat name prefixes/regex (as accepted by VPP stats API) to request.
      interface_names: When provided, interface specific paths will be auto-generated (both modern
                       '/interfaces/<if>/(rx|tx|drops|error|punt|ip4|ip6)?' and legacy '/if/(rx|tx|drops)' forms
                       for compatibility, unless disable_legacy_interface_paths is True).
      stats_socket_path: Path to the VPP stats Unix socket.
      include_error_counters: Include '/err/' error counters (per thread) automatically.
      disable_legacy_interface_paths: Do not include legacy '/if/' paths when True.
    """
    patterns: List[str] = field(default_factory=list)
    interface_names: List[str] = field(default_factory=list)
    stats_socket_path: str = "/run/vpp/stats.sock"
    include_error_counters: bool = True
    disable_legacy_interface_paths: bool = False
    debug: bool = False
   

@dataclass_json
@dataclass
class VPPCounterValue:
    """Represents a single counter value with metadata"""
    packets: int = 0
    bytes: int = 0
    

@dataclass_json
@dataclass
class VPPStatsEntry:
    """Single statistics entry from VPP"""
    name: str = ""
    """Name/path of the statistic (e.g., '/if/rx', '/err/ip4-input')"""
    type: VPPStatsType = VPPStatsType.SCALAR
    """Type of the statistic"""
    
    # For scalar values
    scalar_value: float = 0.0
    
    # For simple counter vectors (per-thread, per-interface arrays)
    simple_counter_vec: List[List[int]] = field(default_factory=lambda: [])
    
    # For combined counter vectors (packets + bytes per-thread, per-interface)
    combined_counter_vec: List[List[VPPCounterValue]] = field(default_factory=lambda: [])
    
    # For error counters (per-thread arrays)
    error_vector: List[int] = field(default_factory=lambda: [])
    
    # For name vectors
    name_vector: List[str] = field(default_factory=lambda: [])


@dataclass_json
@dataclass
class VPPStatsReply:
    """Reply containing collected VPP statistics"""
    success: bool = True
    error: str = ""
    timestamp: str = ""
    """ISO timestamp when statistics were collected"""
    entries: List[VPPStatsEntry] = field(default_factory=lambda: [])
    """List of collected statistics entries"""
    debug_info: List[str] = field(default_factory=list)
    """Optional debug lines with raw data shape / conversion info when debug enabled"""
    
    def get_interface_counters(self, interface_index: int = 0, thread_index: int = 0) -> Dict[str, Any]:
        """Helper method to extract interface counters for a specific interface and thread"""
        counters = {}
        for entry in self.entries:
            if entry.name.startswith('/if/'):
                counter_type = entry.name.split('/')[-1]  # rx, tx, drops, etc.
                if entry.type == VPPStatsType.COUNTER_VECTOR_SIMPLE:
                    if (thread_index < len(entry.simple_counter_vec) and 
                        interface_index < len(entry.simple_counter_vec[thread_index])):
                        counters[counter_type] = entry.simple_counter_vec[thread_index][interface_index]
                elif entry.type == VPPStatsType.COUNTER_VECTOR_COMBINED:
                    if (thread_index < len(entry.combined_counter_vec) and 
                        interface_index < len(entry.combined_counter_vec[thread_index])):
                        counter_val = entry.combined_counter_vec[thread_index][interface_index]
                        counters[counter_type] = {
                            'packets': counter_val.packets,
                            'bytes': counter_val.bytes
                        }
        return counters
        
    def get_interface_counters_by_name(self, interface_name: str) -> Dict[str, Any]:
        """Helper method to extract interface counters for a specific interface by name (e.g., 'wg0')"""
        counters = {}
        
        # Look for interface-specific entries like /interfaces/wg0/rx, /interfaces/wg0/tx, etc.
        base_pattern = f"/interfaces/{interface_name}/"
        
        for entry in self.entries:
            if entry.name.startswith(base_pattern):
                counter_type = entry.name.replace(base_pattern, "")  # rx, tx, drops, etc.
                
                if entry.type == VPPStatsType.COUNTER_VECTOR_SIMPLE:
                    # Sum across all threads for this interface
                    total = 0
                    for thread_counters in entry.simple_counter_vec:
                        if thread_counters:  # Check if thread has data
                            total += sum(thread_counters)
                    counters[f"{counter_type}_packets"] = total
                    
                elif entry.type == VPPStatsType.COUNTER_VECTOR_COMBINED:
                    # Sum packets and bytes across all threads for this interface
                    total_packets = 0
                    total_bytes = 0
                    for thread_counters in entry.combined_counter_vec:
                        if thread_counters:  # Check if thread has data
                            for counter_val in thread_counters:
                                total_packets += counter_val.packets
                                total_bytes += counter_val.bytes
                    counters[f"{counter_type}_packets"] = total_packets
                    counters[f"{counter_type}_bytes"] = total_bytes
                    
                elif entry.type == VPPStatsType.SCALAR:
                    counters[counter_type] = entry.scalar_value
                    
        # Fallback: legacy aggregate vectors '/if/rx', '/if/tx', '/if/drops' + name vector '/if/names'
        if counters:
            return counters

        # Find name vector entry (list of interface names in order of indices)
        name_vec_entry = None
        for entry in self.entries:
            if entry.name in ("/if/names", "/if/name", "/if/interfaces") and entry.type == VPPStatsType.NAME_VECTOR:
                name_vec_entry = entry
                break
        if not name_vec_entry:
            return counters  # cannot map indices
        try:
            index = name_vec_entry.name_vector.index(interface_name)
        except ValueError:
            return counters  # interface name not present

        # Helper to aggregate combined counters per interface index
        def aggregate_combined(entry: 'VPPStatsEntry') -> Dict[str, int]:
            packets_total = 0
            bytes_total = 0
            for thread_list in entry.combined_counter_vec:
                if index < len(thread_list):
                    cv = thread_list[index]
                    packets_total += cv.packets
                    bytes_total += cv.bytes
            return {"packets": packets_total, "bytes": bytes_total}

        # Helper for simple counters
        def aggregate_simple(entry: 'VPPStatsEntry') -> int:
            total = 0
            for thread_list in entry.simple_counter_vec:
                if index < len(thread_list):
                    total += thread_list[index]
            return total

        # Scan legacy entries
        legacy_map = {e.name: e for e in self.entries if e.name.startswith("/if/")}
        rx_entry = legacy_map.get("/if/rx")
        tx_entry = legacy_map.get("/if/tx")
        drops_entry = legacy_map.get("/if/drops")

        if rx_entry and rx_entry.type == VPPStatsType.COUNTER_VECTOR_COMBINED:
            agg = aggregate_combined(rx_entry)
            counters["rx_packets"] = agg["packets"]
            counters["rx_bytes"] = agg["bytes"]
        if tx_entry and tx_entry.type == VPPStatsType.COUNTER_VECTOR_COMBINED:
            agg = aggregate_combined(tx_entry)
            counters["tx_packets"] = agg["packets"]
            counters["tx_bytes"] = agg["bytes"]
        if drops_entry and drops_entry.type == VPPStatsType.COUNTER_VECTOR_SIMPLE:
            counters["drops"] = aggregate_simple(drops_entry)

        return counters
        
    def get_error_counters(self) -> Dict[str, List[int]]:
        """Helper method to extract error counters"""
        errors = {}
        for entry in self.entries:
            if entry.name.startswith('/err/') and entry.type == VPPStatsType.ERROR_INDEX:
                error_name = entry.name.replace('/err/', '')
                errors[error_name] = entry.error_vector
        return errors

    def summarize_interface(self, interface_name: str) -> Dict[str, int]:
        """Return aggregated counters for a given interface.

        Combines data from per-interface paths (/interfaces/<if>/rx, etc.) if present;
        otherwise attempts legacy /if/* vector decoding using name vector mapping.
        Keys returned (if available): rx_packets, rx_bytes, tx_packets, tx_bytes, drops.
        """
        result = self.get_interface_counters_by_name(interface_name)
        if result:
            return result
        # Attempt legacy aggregation if not already populated
        name_vec = None
        for entry in self.entries:
            if entry.name in ("/if/names", "/if/name", "/if/interfaces") and entry.type == VPPStatsType.NAME_VECTOR:
                name_vec = entry.name_vector
                break
        if not name_vec:
            return result
        try:
            idx = name_vec.index(interface_name)
        except ValueError:
            return result
        # Locate legacy entries
        rx_entry = next((e for e in self.entries if e.name == "/if/rx" and e.type == VPPStatsType.COUNTER_VECTOR_COMBINED), None)
        tx_entry = next((e for e in self.entries if e.name == "/if/tx" and e.type == VPPStatsType.COUNTER_VECTOR_COMBINED), None)
        drops_entry = next((e for e in self.entries if e.name == "/if/drops" and e.type == VPPStatsType.COUNTER_VECTOR_SIMPLE), None)
        if rx_entry:
            rx_packets = rx_bytes = 0
            for thread_list in rx_entry.combined_counter_vec:
                if idx < len(thread_list):
                    rx_packets += thread_list[idx].packets
                    rx_bytes += thread_list[idx].bytes
            result["rx_packets"] = rx_packets
            result["rx_bytes"] = rx_bytes
        if tx_entry:
            tx_packets = tx_bytes = 0
            for thread_list in tx_entry.combined_counter_vec:
                if idx < len(thread_list):
                    tx_packets += thread_list[idx].packets
                    tx_bytes += thread_list[idx].bytes
            result["tx_packets"] = tx_packets
            result["tx_bytes"] = tx_bytes
        if drops_entry:
            drops_total = 0
            for thread_list in drops_entry.simple_counter_vec:
                if idx < len(thread_list):
                    drops_total += thread_list[idx]
            result["drops"] = drops_total
        return result


