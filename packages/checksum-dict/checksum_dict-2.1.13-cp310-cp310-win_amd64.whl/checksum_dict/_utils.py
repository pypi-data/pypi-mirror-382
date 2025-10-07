"""
This library was built to have minimal dependencies, to minimize dependency conflicts for users.
The following code was ripped out of eth-brownie on 2022-Aug-06.
A big thanks to the many maintainers and contributors for their valuable work!
"""

from typing import TYPE_CHECKING, Dict, Final, Type, Union

import cchecksum
from eth_typing import ChecksumAddress

from checksum_dict import _typing

if TYPE_CHECKING:
    from brownie import Contract
    from y import ERC20


# I do this hacky thing to help out mypyc.
# If I try to conditionally define `Contract` and `ERC20` the compiler fails.
# So I do this instead.
_KNOWN_CHECKSUMMED_TYPES: Final[Dict[type, bool]] = {}

# must not be Final so it can be redefined with lru cache in ypricemagic
to_checksum_address = cchecksum.to_checksum_address


def attempt_checksum(value: Union[str, bytes, "Contract", "ERC20"]) -> ChecksumAddress:
    # sourcery skip: merge-duplicate-blocks
    if isinstance(value, str):
        return checksum_or_raise(value)
    elif (valtype := type(value)) is bytes:  # only actual bytes type, mypyc will optimize this
        return checksum_or_raise(value.hex())
    elif _type_has_checksum_addr(valtype):
        return value.address  # type: ignore [union-attr, return-value]
    elif hasattr(valtype, "address"):
        return checksum_or_raise(value.address)  # type: ignore [union-attr]
    else:  # other bytes types, mypyc will not optimize this
        return checksum_or_raise(value.hex())


def checksum_or_raise(string: str) -> ChecksumAddress:
    try:
        return to_checksum_address(string)
    except ValueError as e:
        raise ValueError(f"'{string}' is not a valid ETH address") from e


def _type_has_checksum_addr(typ: Type) -> bool:  # type: ignore [type-arg]
    has_checksum_addr = _KNOWN_CHECKSUMMED_TYPES.get(typ)
    if has_checksum_addr is None:
        has_checksum_addr = typ.__name__ in {"Contract", "ERC20"} and typ.__module__.split(".")[
            0
        ] in {"brownie", "dank_mids", "y"}
        _KNOWN_CHECKSUMMED_TYPES[typ] = has_checksum_addr
    return has_checksum_addr
