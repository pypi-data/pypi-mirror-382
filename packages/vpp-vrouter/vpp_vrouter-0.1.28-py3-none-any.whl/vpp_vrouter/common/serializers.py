"""
Serialization utilities/fixes for Pyro5 serialization of data structures flowing between client and server
"""

import ipaddress
import typing
import warnings
from dataclasses import is_dataclass, fields

import Pyro5.api
from vpp_papi import macaddress, vpp_serializer

from vpp_vrouter.common import models

PYRO_SERIALIZED_CLASS_NAME_KEY = "__class__"
SERIALIZED_CLASS_VALUE_KEY = "json"


def convert_mac_dict_to_class(class_name, mac_dict):
    return macaddress.MACAddress(mac_dict["mac"])


def convert_mac_class_to_dict(mac_class):
    return {
        PYRO_SERIALIZED_CLASS_NAME_KEY: "vpp_papi.macaddress.MACAddress",
        "mac": str(mac_class),
    }


def convert_ipv4address_dict_to_class(class_name, ipv4addr_dict):
    return ipaddress.IPv4Address(ipv4addr_dict["ipv4_address"])


def convert_ipv4address_class_to_dict(ipv4addr_class):
    return {
        PYRO_SERIALIZED_CLASS_NAME_KEY: "ipaddress.IPv4Address",
        "ipv4_address": ipv4addr_class.exploded,
    }


def convert_ipv4network_dict_to_class(class_name, ipv4net_dict):
    return ipaddress.IPv4Network(ipv4net_dict["ipv4_network"])


def convert_ipv4network_class_to_dict(ipv4net_class):
    return {
        PYRO_SERIALIZED_CLASS_NAME_KEY: "ipaddress.IPv4Network",
        "ipv4_network": ipv4net_class.exploded,
    }


def convert_vpp_serializer_value_error_dict_to_class(class_name, error_dict):
    return vpp_serializer.VPPSerializerValueError(error_dict["VPPSerializerValueError"])


def convert_vpp_serializer_value_error_class_to_dict(clazz):
    return {
        PYRO_SERIALIZED_CLASS_NAME_KEY: "vpp_papi.vpp_serializer.VPPSerializerValueError",
        "VPPSerializerValueError": str(clazz),
    }


def convert_marshmallow_validation_error_dict_to_class(class_name, error_dict):
    from marshmallow.exceptions import ValidationError
    # ValidationError can have different structures - handle both cases
    if "messages" in error_dict:
        return ValidationError(error_dict["messages"], field_name=error_dict.get("field_name"), data=error_dict.get("data"))
    elif "message" in error_dict:
        return ValidationError(error_dict["message"], field_name=error_dict.get("field_name"), data=error_dict.get("data"))
    else:
        # If neither, use the entire dict as the message
        print(f"DEBUG: ValidationError dict structure: {error_dict}")
        return ValidationError(str(error_dict))


def convert_marshmallow_validation_error_class_to_dict(clazz):
    return {
        PYRO_SERIALIZED_CLASS_NAME_KEY: "marshmallow.exceptions.ValidationError",
        "messages": clazz.messages,
        "field_name": getattr(clazz, 'field_name', None),
        "data": getattr(clazz, 'data', None),
    }


dataclass_name_to_class = dict()
nondataclass_name_to_dict_to_class_function = dict()


def register_serialization_for_dataclass(class_name, dataclass):
    """Custom serialization for dataclasses"""

    dataclass_name_to_class[class_name] = dataclass
    Pyro5.api.SerializerBase.register_class_to_dict(
        dataclass,
        lambda dataclass_instance: {
            PYRO_SERIALIZED_CLASS_NAME_KEY: class_name,
            SERIALIZED_CLASS_VALUE_KEY: dataclass.schema().dump(dataclass_instance),
        },
    )
    Pyro5.api.SerializerBase.register_dict_to_class(
        class_name,
        lambda class_name, dataclass_dict: dataclass_inner_deserialization(
            dataclass.schema().load(dataclass_dict[SERIALIZED_CLASS_VALUE_KEY])
        ),
    )


def register_serialization_for_nondataclass(clazz, name, class_to_dict, dict_to_class):
    """Custom serialization for other classes than dataclasses"""

    nondataclass_name_to_dict_to_class_function[name] = dict_to_class
    Pyro5.api.SerializerBase.register_class_to_dict(clazz, class_to_dict)
    Pyro5.api.SerializerBase.register_dict_to_class(name, dict_to_class)
    # ignore dataclass-json converter warning because dataclass_inner_deserialization(...) will be used
    # to resolve types
    warnings.filterwarnings(
        action="ignore",
        message=".*{}.*It's advised to pass the correct marshmallow type.*".format(
            name.replace(".", "\\.")
        ),
    )


def import_pyro5_serializers():
    """Fixes Pyro5 serialization for client-server traffic by registering customized serializers"""

    # configuration items
    register_serialization_for_dataclass(
        "models.InterfaceConfigurationItem", models.InterfaceConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.RouteConfigurationItem", models.RouteConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.ACLConfigurationItem", models.ACLConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.Nat44AddressPoolConfigurationItem",
        models.Nat44AddressPoolConfigurationItem,
    )
    register_serialization_for_dataclass(
        "models.Nat44InterfaceConfigurationItem", models.Nat44InterfaceConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.DNat44ConfigurationItem", models.DNat44ConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.WireguardPeerConfigurationItem", models.WireguardPeerConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.LCPGlobalsConfigurationItem", models.LCPGlobalsConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.LCPPairConfigurationItem", models.LCPPairConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.FRRConfigurationItem", models.FRRConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.DHCPConfigurationItem", models.DHCPConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.RunningPacketCapture", models.RunningPacketCapture
    )
    register_serialization_for_dataclass(
        "models.LinuxDockerVethTunnelConfigurationItem",
        models.LinuxDockerVethTunnelConfigurationItem,
    )
    register_serialization_for_dataclass(
        "models.LinuxRouteConfigurationItem", models.LinuxRouteConfigurationItem
    )
    register_serialization_for_dataclass(
        "models.VPPStatsQuery", models.VPPStatsQuery
    )
    register_serialization_for_dataclass(
        "models.VPPStatsReply", models.VPPStatsReply
    )
    register_serialization_for_dataclass(
        "models.VPPStatsEntry", models.VPPStatsEntry
    )
    register_serialization_for_dataclass(
        "models.VPPCounterValue", models.VPPCounterValue
    )

    # replies
    register_serialization_for_dataclass("models.ApplyReply", models.ApplyReply)
    register_serialization_for_dataclass(
        "models.AddConfigurationItemsReply", models.AddConfigurationItemsReply
    )
    register_serialization_for_dataclass(
        "models.DeleteConfigurationItemsReply", models.DeleteConfigurationItemsReply
    )
    register_serialization_for_dataclass(
        "models.UpdateConfigurationItemsReply", models.UpdateConfigurationItemsReply
    )
    register_serialization_for_dataclass(
        "models.GetConfigurationItemsReply", models.GetConfigurationItemsReply
    )
    register_serialization_for_dataclass(
        "models.ConfigurationItemReply", models.ConfigurationItemReply
    )
    register_serialization_for_dataclass(
        "models.ConfigurationItemDetail", models.ConfigurationItemDetail
    )
    register_serialization_for_dataclass(
        "models.WireguardPeerDetail", models.WireguardPeerDetail
    )
    register_serialization_for_dataclass("models.LCPPairDetail", models.LCPPairDetail)
    register_serialization_for_dataclass(
        "models.ProcessCallReply", models.ProcessCallReply
    )

    # static models for dynamic api object from basic vpp client
    # (pyro5 handles serialization, modifier function using dataclass-json does deserialization)
    register_serialization_for_dataclass(
        "models.SWInterfaceDetail", models.SWInterfaceDetail
    )
    register_serialization_for_dataclass("models.IPRouteDetail", models.IPRouteDetail)
    register_serialization_for_dataclass("models.ACLRule", models.ACLRule)
    register_serialization_for_dataclass("models.ACLDetails", models.ACLDetails)
    register_serialization_for_dataclass(
        "models.NAT44AddressDetails", models.NAT44AddressDetails
    )
    register_serialization_for_dataclass(
        "models.NAT44InterfaceDetails", models.NAT44InterfaceDetails
    )
    register_serialization_for_dataclass(
        "models.NAT44StaticMappingDetails", models.NAT44StaticMappingDetails
    )
    register_serialization_for_dataclass(
        "models.NAT44IdentityMappingDetails", models.NAT44IdentityMappingDetails
    )

    # other objects that need serialization
    register_serialization_for_nondataclass(
        vpp_serializer.VPPSerializerValueError,
        "vpp_papi.vpp_serializer.VPPSerializerValueError",
        convert_vpp_serializer_value_error_class_to_dict,
        convert_vpp_serializer_value_error_dict_to_class,
    )

    # Marshmallow ValidationError
    from marshmallow.exceptions import ValidationError
    register_serialization_for_nondataclass(
        ValidationError,
        "marshmallow.exceptions.ValidationError",
        convert_marshmallow_validation_error_class_to_dict,
        convert_marshmallow_validation_error_dict_to_class,
    )

    # MAC Address
    register_serialization_for_nondataclass(
        macaddress.MACAddress,
        "vpp_papi.macaddress.MACAddress",
        convert_mac_class_to_dict,
        convert_mac_dict_to_class,
    )
    register_serialization_for_nondataclass(
        vpp_serializer.VPPSerializerValueError,
        "vpp_papi.vpp_serializer.VPPSerializerValueError",
        convert_vpp_serializer_value_error_class_to_dict,
        convert_vpp_serializer_value_error_dict_to_class,
    )
    register_serialization_for_nondataclass(
        ipaddress.IPv4Address,
        "ipaddress.IPv4Address",
        convert_ipv4address_class_to_dict,
        convert_ipv4address_dict_to_class,
    )
    register_serialization_for_nondataclass(
        ipaddress.IPv4Network,
        "ipaddress.IPv4Network",
        convert_ipv4network_class_to_dict,
        convert_ipv4network_dict_to_class,
    )


def dataclass_inner_deserialization(data):
    if type(data) is list:
        return [dataclass_inner_deserialization(e) for e in data]

    if type(data) is dict:
        return _handle_dict_value(data)

    if not is_dataclass(data):
        return data

    for field in fields(type(data)):
        is_opt = _is_optional_or_union_with_none(field.type)
        if is_opt:
            field_value = getattr(data, field.name, None)
            if field_value is None:
                continue
        else:
            field_value = getattr(data, field.name)

        if is_dataclass(field_value):
            setattr(data, field.name, dataclass_inner_deserialization(field_value))

        if type(field_value) is list:
            setattr(
                data,
                field.name,
                [dataclass_inner_deserialization(e) for e in field_value],
            )
            continue

        if type(field_value) is dict:
            setattr(data, field.name, _handle_dict_value(field_value))
            continue

        # do nothing for other types that we don't deserialize (literals, other types...)

    return data


def _is_optional_or_union_with_none(T):
    origin_type = getattr(T, "__origin__", None)
    type_args = getattr(T, "__args__", [])
    return origin_type is typing.Union and type_args and type_args[-1] is type(None)


def _handle_dict_value(dict_value):
    to_deserialize_class_name = dict_value.get(PYRO_SERIALIZED_CLASS_NAME_KEY)
    if to_deserialize_class_name is not None:
        clazz = dataclass_name_to_class.get(to_deserialize_class_name)
        if clazz is not None:
            deserialized_value = clazz.schema().load(
                dict_value.get(SERIALIZED_CLASS_VALUE_KEY)
            )  # still can have inner not deserialized dataclasses
        else:
            dict_to_class_function = nondataclass_name_to_dict_to_class_function.get(
                to_deserialize_class_name
            )
            deserialized_value = dict_to_class_function(
                to_deserialize_class_name, dict_value
            )
        value = dataclass_inner_deserialization(deserialized_value)
    else:
        value = {k: dataclass_inner_deserialization(e) for k, e in dict_value.items()}
    return value
