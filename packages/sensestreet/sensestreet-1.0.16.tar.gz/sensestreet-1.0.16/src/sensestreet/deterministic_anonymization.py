import hashlib
from sensestreet.data.unique_first_names import FIRST_NAMES
from sensestreet.data.unique_last_names import LAST_NAMES
import base64
from typing import Tuple


def anonimize_to_hash(login, short=True):
    """
    Generate an anonymized hash representation of a given login.

    Args:
        login (str): The input string (e.g., username or email) to be anonymized.
        short (bool): If True, returns a Base85-encoded hash for compactness.
                      If False, returns a Base64-encoded hash.

    Returns:
        str: The anonymized hash of the login, encoded as Base85 or Base64.
    """
    hash_value = hashlib.sha512(login.encode()).digest()
    if short:
        return base64.b85encode(hash_value).decode()
    return base64.b64encode(hash_value).decode()

def anonimize_to_name(login) -> Tuple[str, str]:
    """
    Generate a deterministic first and last name based on a login hash.

    Args:
        login (str): The input string (e.g., username or email) to be anonymized.

    Returns:
        Tuple[str, str]: A tuple containing the anonymized first name and last name.
                         The names are selected deterministically from pre-defined lists.
    """
    hash_value = hashlib.sha512(login.encode()).hexdigest()

    first_index = int(hash_value[:64], 16) % len(FIRST_NAMES)
    last_index = int(hash_value[64:128], 16) % len(LAST_NAMES)

    first_name = FIRST_NAMES[first_index]
    last_name = LAST_NAMES[last_index]

    return first_name, last_name
