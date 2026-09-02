from functools import lru_cache
from web3 import Web3


@lru_cache
def get_web3() -> Web3:
    return Web3()
