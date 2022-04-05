import re


def to_int_key(user_id: str):
    """
    Bases like MongoDb only work with int-based keys.
    Hence, dialogic user ids should be reformatted as int-castable strings.
    """
    all_ints: list = re.findall(r"[0-9]", user_id)
    int_key = "".join(all_ints)
    return int_key
