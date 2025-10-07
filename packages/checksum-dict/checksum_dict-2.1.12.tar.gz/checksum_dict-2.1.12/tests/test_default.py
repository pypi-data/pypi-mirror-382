from checksum_dict import DefaultChecksumDict


def test_checksum_address_dict_keys():
    # Arrange
    dcd = DefaultChecksumDict(int)

    # Act
    keys = dcd.keys()

    # Assert
    assert list(keys) == []

    # Act
    dcd["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    keys = dcd.keys()

    # Assert
    assert list(keys) == ["0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"]


def test_checksum_address_dict_values():
    # Arrange
    dcd = DefaultChecksumDict(int)

    # Act
    values = dcd.values()

    # Assert
    assert list(values) == []

    # Act
    dcd["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    values = dcd.values()

    # Assert
    assert list(values) == [1]


def test_checksum_address_dict_items():
    # Arrange
    dcd = DefaultChecksumDict(int)

    # Act
    items = dcd.items()

    # Assert
    assert list(items) == []

    # Act
    dcd["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    items = dcd.items()

    # Assert
    assert list(items) == [("0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB", 1)]


def test_subclass_dict_keys():
    # Arrange
    class Subclass(DefaultChecksumDict[int]):
        def __init__(self):
            super().__init__(int)

    subcls = Subclass()

    # Act
    keys = subcls.keys()

    # Assert
    assert list(keys) == []

    # Act
    subcls["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    keys = subcls.keys()

    # Assert
    assert list(keys) == ["0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"]


def test_subclass_dict_values():
    # Arrange
    class Subclass(DefaultChecksumDict[int]):
        def __init__(self):
            super().__init__(int)

    subcls = Subclass()

    # Act
    values = subcls.values()

    # Assert
    assert list(values) == []

    # Act
    subcls["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    values = subcls.values()

    # Assert
    assert list(values) == [1]


def test_subclass_dict_items():
    # Arrange
    class Subclass(DefaultChecksumDict[int]):
        def __init__(self):
            super().__init__(int)

    subcls = Subclass()

    # Act
    items = subcls.items()

    # Assert
    assert list(items) == []

    # Act
    subcls["0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"] += 1
    items = subcls.items()

    # Assert
    assert list(items) == [("0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB", 1)]
