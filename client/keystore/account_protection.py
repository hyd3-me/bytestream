_account_protection = {}
_attempts = {}



def get_protection_type(eth_address: str) -> dict:
    record = _account_protection.get(eth_address)
    if record is None:
        return {"type": "none"}
    return {"type": record["type"]}
