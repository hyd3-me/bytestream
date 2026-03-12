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
