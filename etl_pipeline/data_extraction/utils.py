import json
import hashlib

def hash_dict(obj: dict) -> str:
    """
    Compute a stable SHA-256 hash of a JSON-like Python object.

    - sort_keys=True ensures consistent key order
    - separators=(',', ':') removes whitespace
    - ensure_ascii=False allows UTF-8 text to hash consistently
    """
    canonical_str = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()