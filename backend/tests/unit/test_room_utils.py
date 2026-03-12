import pytest
from app.room import utils


def test_sort_addresses_returns_sorted_pair():
    addr1 = "0xbbb"
    addr2 = "0xaaa"
    sorted1, sorted2 = utils.sort_addresses(addr1, addr2)
    assert sorted1 == "0xaaa"
    assert sorted2 == "0xbbb"
