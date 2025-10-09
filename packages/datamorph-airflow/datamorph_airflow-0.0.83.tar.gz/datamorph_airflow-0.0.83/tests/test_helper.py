from typing import Dict, Any


def check_dict_key(item_dict: Dict[str, Any], key: str) -> bool:
    return bool(key in item_dict and item_dict[key] is not None)