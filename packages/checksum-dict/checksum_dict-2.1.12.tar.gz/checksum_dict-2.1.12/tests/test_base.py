import pytest
from brownie import Contract

from checksum_dict import ChecksumAddressDict


@pytest.mark.parametrize(
    "seed, expected",
    [
        (
            {"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True},
            {"0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB": True},
        ),  # id: seed-dict
        (None, {}),  # id: seed-none
        (
            [("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb", True)],
            {"0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB": True},
        ),  # id: seed-iterable
        ([], {}),  # id: seed-empty-iterable
    ],
)
def test_checksum_address_dict_init(seed, expected):
    # Act
    cad = ChecksumAddressDict(seed)

    # Assert
    assert dict(cad) == expected


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb", True, True),  # id: set-and-get-lowercase
        ("0xB47E3CD837DDF8E4C57F05D70AB865DE6E193BBB", False, False),  # id: set-and-get-uppercase
        ("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb", 123, 123),  # id: set-and-get-checksummed
        (
            Contract("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"),
            123,
            123,
        ),  # id: set-and-get-contract
    ],
)
def test_checksum_address_dict_set_and_get(key, value, expected):
    # Act
    cad = ChecksumAddressDict()
    cad[key] = value

    # Assert
    assert cad[key] == expected


@pytest.mark.parametrize(
    "key, expected_error",
    [
        ("0x123", ValueError),  # id: invalid-address-length
        (123, AttributeError),  # id: invalid-address-type
    ],
)
def test_checksum_address_dict_get_error(key, expected_error):
    # Arrange
    cad = ChecksumAddressDict()

    # Act & Assert
    with pytest.raises(expected_error):
        cad[key]


@pytest.mark.parametrize(
    "key, value",
    [
        ("0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb", True),  # id: set-nochecksum-valid
    ],
)
def test_checksum_address_dict_set_and_get_nochecksum(key, value):
    # Arrange
    cad = ChecksumAddressDict()

    # Act
    cad._setitem_nochecksum(key, value)

    # Assert
    assert cad._getitem_nochecksum(key) == value
    assert cad[key] == value


@pytest.mark.parametrize(
    "key, value, expected_error",
    [
        ("0x123", True, ValueError),  # id: set-nochecksum-invalid-address
        (
            "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb123",
            True,
            ValueError,
        ),  # id: set-nochecksum-invalid-address-length
        (123, True, ValueError),  # id: set-nochecksum-invalid-address-type
    ],
)
def test_checksum_address_dict_set_nochecksum_error(key, value, expected_error):
    # Arrange
    cad = ChecksumAddressDict()

    # Act & Assert
    with pytest.raises((expected_error, AttributeError)):
        cad._setitem_nochecksum(key, value)


def test_checksum_address_dict_repr():
    # Arrange
    cad = ChecksumAddressDict({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    representation = repr(cad)

    # Assert
    assert (
        representation
        == "ChecksumAddressDict({'0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB': True})"
    )


def test_checksum_address_dict_keys():
    # Arrange
    cad = ChecksumAddressDict({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    keys = cad.keys()

    # Assert
    assert list(keys) == ["0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"]


def test_checksum_address_dict_values():
    # Arrange
    cad = ChecksumAddressDict({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    values = cad.values()

    # Assert
    assert list(values) == [True]


def test_checksum_address_dict_items():
    # Arrange
    cad = ChecksumAddressDict({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    items = cad.items()

    # Assert
    assert list(items) == [("0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB", True)]


def test_subclass_dict_keys():
    # Arrange
    class Subclass(ChecksumAddressDict):
        pass

    subcls = Subclass({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    keys = subcls.keys()

    # Assert
    assert list(keys) == ["0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"]


def test_subclass_dict_values():
    # Arrange
    class Subclass(ChecksumAddressDict):
        pass

    subcls = Subclass({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    values = subcls.values()

    # Assert
    assert list(values) == [True]


def test_subclass_dict_items():
    # Arrange
    class Subclass(ChecksumAddressDict):
        pass

    subcls = Subclass({"0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb": True})

    # Act
    items = subcls.items()

    # Assert
    assert list(items) == [("0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB", True)]
