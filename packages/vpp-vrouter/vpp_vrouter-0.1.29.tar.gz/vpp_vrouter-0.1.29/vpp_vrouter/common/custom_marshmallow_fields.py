"""
Custom field types used in modeled API(dataclasses) so that the Pyro5 framework can serialize the content correctly
"""

import ipaddress

from marshmallow.fields import Field


class IPNetwork(Field):
    """A IPNetwork field."""

    default_error_messages = {"invalid_ip_network": "Not a valid IP network."}

    DESERIALIZATION_CLASS = None  # type: typing.Optional[typing.Type]

    def __init__(self, *args, exploded: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.exploded = exploded

    def _serialize(self, value, attr, obj, **kwargs) -> str | None:
        if value is None:
            return None
        if self.exploded:
            return value.exploded
        return value.compressed

    def _deserialize(
        self, value, attr, data, **kwargs
    ) -> None | (ipaddress.IPv4Network | ipaddress.IPv6Network):
        def ensure_text_type(val: str | bytes) -> str:
            if isinstance(val, bytes):
                val = val.decode("utf-8")
            return str(val)

        if value is None:
            return None
        try:
            return (self.DESERIALIZATION_CLASS or ipaddress.ip_network)(
                ensure_text_type(value)
            )
        except (ValueError, TypeError) as error:
            raise self.make_error("invalid_ip_network") from error


class IPv4Network(IPNetwork):
    """A IPv4 Network field."""

    default_error_messages = {"invalid_ip_network": "Not a valid IPv4 network."}

    DESERIALIZATION_CLASS = ipaddress.IPv4Network


class IPv6Network(IPNetwork):
    """A IPv6 Network field."""

    default_error_messages = {"invalid_ip_network": "Not a valid IPv6 network."}

    DESERIALIZATION_CLASS = ipaddress.IPv6Network
