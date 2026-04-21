import random
import string

from bson import ObjectId

# general utility functions
# copied from stackoverflow mostly, cleaned up a bit


def format_date(dt):
    """format a datetime object for api responses"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_discount(quantity, total):
    """returns discount amount (not discounted total)"""
    # 10% discount when ordering 10 or more items
    if quantity >= 10:
        return total * 0.10
    return 0


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """
    check if a status change is allowed
    TODO: wire this up in the orders route - currently not called anywhere
    """
    valid_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["shipped", "cancelled"],
        "shipped": ["done"],
        "done": [],
        "cancelled": [],
    }

    allowed = valid_transitions.get(current_status, [])
    return new_status in allowed


def generate_order_ref():
    """generate a random order reference string"""
    chars = string.ascii_uppercase + string.digits
    return "ORD-" + "".join(random.choices(chars, k=8))


def is_valid_object_id(id_str: str) -> bool:
    """check if a string is a valid mongodb objectid"""
    # copied from stackoverflow
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False
