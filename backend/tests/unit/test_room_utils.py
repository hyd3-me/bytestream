import pytest
from app.room import utils


def test_sort_addresses_returns_sorted_pair():
    addr1 = "0xbbb"
    addr2 = "0xaaa"
    sorted1, sorted2 = utils.sort_addresses(addr1, addr2)
    assert sorted1 == "0xaaa"
    assert sorted2 == "0xbbb"


def test_get_dm_room_id_returns_deterministic_id():
    addr_a = "0xbbb"
    addr_b = "0xaaa"
    room_id = utils.get_dm_room_id(addr_a, addr_b)
    assert room_id == "dm:0xaaa:0xbbb"


def test_is_valid_eth_address_valid():
    assert utils.is_valid_eth_address("0x" + "1" * 40) is True
    assert utils.is_valid_eth_address("0x" + "a" * 40) is True
    valid_checksum = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
    assert utils.is_valid_eth_address(valid_checksum) is True


def test_is_valid_eth_address_invalid():
    assert utils.is_valid_eth_address("0x" + "1" * 39) is False  # too short
    assert (
        utils.is_valid_eth_address("1" * 40) is True
    )  # web3 accepts addresses without 0x
    assert utils.is_valid_eth_address("0x" + "g" * 40) is False  # invalid hex
    assert utils.is_valid_eth_address("0x" + "1" * 41) is False  # too long
