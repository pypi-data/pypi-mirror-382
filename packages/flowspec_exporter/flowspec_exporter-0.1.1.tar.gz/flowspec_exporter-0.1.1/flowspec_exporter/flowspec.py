from collections import UserList
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import Self

from dataclasses_json import config, dataclass_json
from netaddr import IPNetwork


class Action(StrEnum):
    ACCEPT = "accept"
    DISCARD = "discard"
    RATE_LIMIT = "rate-limit"
    REDIRECT = "redirect"


class CommandType(IntEnum):
    DESTINATION_PREFIX = 1
    SOURCE_PREFIX = 2
    IP_PROTOCOL = 3
    PORT = 4
    DESTINATION_PORT = 5
    SOURCE_PORT = 6
    ICMP_TYPE = 7
    ICMP_CODE = 8
    TCP_FLAGS = 9
    PACKET_LENGTH = 10
    DSCP = 11
    FRAGMENT = 12

    @classmethod
    def from_str(cls, value: str) -> "CommandType":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid command type: {value}")

    def __str__(self) -> str:
        match self:
            case CommandType.DESTINATION_PREFIX:
                return "destination-prefix"
            case CommandType.SOURCE_PREFIX:
                return "source-prefix"
            case CommandType.IP_PROTOCOL:
                return "ip-protocol"
            case CommandType.PORT:
                return "port"
            case CommandType.DESTINATION_PORT:
                return "destination-port"
            case CommandType.SOURCE_PORT:
                return "source-port"
            case CommandType.ICMP_TYPE:
                return "icmp-type"
            case CommandType.ICMP_CODE:
                return "icmp-code"
            case CommandType.TCP_FLAGS:
                return "tcp-flags"
            case CommandType.PACKET_LENGTH:
                return "packet-length"
            case CommandType.DSCP:
                return "dscp"
            case CommandType.FRAGMENT:
                return "fragment"


@dataclass_json
@dataclass(eq=True)
class NumericOp:
    and_: bool = False
    lt: bool = False
    gt: bool = False
    eq: bool = False

    def set_and(self, value: bool) -> Self:
        self.and_ = value

        return self

    def __str__(self) -> str:
        s = ""

        match (self.lt, self.gt, self.eq):
            case (False, False, False):
                s = "false"
            case (False, False, True):
                s = "="
            case (False, True, False):
                s = ">"
            case (False, True, True):
                s = ">="
            case (True, False, False):
                s = "<"
            case (True, False, True):
                s = "<="
            case (True, True, False):
                s = "!="
            case (True, True, True):
                s = "true"

        return s


NumericOpFalse = NumericOp()

NumericOpEq = NumericOp(eq=True)

NumericOpGt = NumericOp(gt=True)

NumericOpGte = NumericOp(gt=True, eq=True)

NumericOpLt = NumericOp(lt=True)

NumericOpLte = NumericOp(lt=True, eq=True)

NumericOpNe = NumericOp(gt=True, lt=True)

NumericOpTrue = NumericOp(lt=True, gt=True, eq=True)


@dataclass_json
@dataclass(eq=True)
class BitmaskOp:
    and_: bool = False
    not_: bool = False
    match: bool = False

    def set_and(self, value: bool) -> Self:
        self.and_ = value

        return self

    def __str__(self) -> str:
        s = ""

        if self.not_:
            s += "!"

        if self.match:
            s += "="

        return s


class NumericValues(UserList[tuple[NumericOp, int]]):
    def __init__(self, *args: tuple[NumericOp, int]):
        super().__init__(args)

    def __str__(self) -> str:
        s = []

        for op, value in self.data:
            if op.and_:
                s += ["&", f"{op}{value}"]
            else:
                s += [" ", f"{op}{value}"]

        return "".join(s).strip()


class BitmaskValues(UserList[tuple[BitmaskOp, int]]):
    def __init__(self, *args: tuple[BitmaskOp, int]):
        super().__init__(args)

    def __str__(self) -> str:
        s = []

        for op, value in self.data:
            if op.and_:
                s += ["&", f"{op}0x{value:02x}"]
            else:
                s += [" ", f"{op}0x{value:02x}"]

        return "".join(s).strip()


def _str_encode(obj: object) -> str | None:
    if obj is None:
        return None
    return str(obj)


@dataclass_json
@dataclass
class FlowSpec:
    raw: str = ""
    destination_prefix: IPNetwork | None = field(
        default=None, metadata=config(encoder=_str_encode)
    )
    source_prefix: IPNetwork | None = field(
        default=None, metadata=config(encoder=_str_encode)
    )
    ip_protocol: NumericValues | None = None
    port: NumericValues | None = None
    destination_port: NumericValues | None = None
    source_port: NumericValues | None = None
    icmp_type: NumericValues | None = None
    icmp_code: NumericValues | None = None
    tcp_flags: BitmaskValues | None = None
    packet_length: NumericValues | None = None
    dscp: NumericValues | None = None
    fragment: BitmaskValues | None = None
    action: Action | None = None
    rate_limit_bps: int | None = None
    matched_packets: int | None = None
    matched_bytes: int | None = None
    transmitted_packets: int | None = None
    transmitted_bytes: int | None = None
    dropped_packets: int | None = None
    dropped_bytes: int | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    filter: str | None = None

    def str_filter(self) -> str:
        s = []

        for key in (
            "destination_prefix",
            "source_prefix",
            "ip_protocol",
            "port",
            "destination_port",
            "source_port",
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "packet_length",
            "dscp",
            "fragment",
        ):
            value = getattr(self, key)

            if value is not None:
                s.append(f"{CommandType.from_str(key)}: {value}")

        return ", ".join(s)


@dataclass_json
@dataclass
class FlowSpecs:
    flows: list[FlowSpec]


__all__ = [
    "Action",
    "CommandType",
    "NumericOp",
    "NumericOpFalse",
    "NumericOpEq",
    "NumericOpGt",
    "NumericOpGte",
    "NumericOpLt",
    "NumericOpLte",
    "NumericOpNe",
    "NumericOpTrue",
    "BitmaskOp",
    "NumericValues",
    "BitmaskValues",
    "FlowSpec",
]
