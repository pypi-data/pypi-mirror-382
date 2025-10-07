from typing import TYPE_CHECKING, Any, Protocol, Union

from eth_typing import Address, ChecksumAddress, HexAddress


# We need to assign mypyc has issues compiling TYPE_CHECKING
# TODO: PR to mypyc to fix this
if TYPE_CHECKING:
    import brownie
    import y

    Contract = brownie.Contract
    ERC20 = y.ERC20

else:

    class Contract(Protocol):
        address: ChecksumAddress

    class ERC20(Protocol):
        address: ChecksumAddress


AnyAddressOrContract = Union[Address, HexAddress, ChecksumAddress, Contract, ERC20]  # type: ignore [valid-type]
