from typing import TypeVar

T = TypeVar("T")

def dict_has_nonempty_str(obj: dict, key: str) -> bool:
    """Test if a dict has a specified key and that key has a non-empty string value.

    Args:
        obj (dict): Dict object to test.
        key (str): Key to validate.

    Returns:
        bool: True if key has a non-empty string value, else false.
    """
    assert isinstance(obj, dict)
    if key in obj:
        testval = obj[key]
        if isinstance(testval, str) and testval: # str evaluates falsy if empty
            return True
    return False


def empty_instance(value: T) -> T:
    """Create an empty instance of the same value type.

    Args:
        value (T): Value to get the type from.

    Returns:
        T: New empty/blank instance of the same type.
    """
    if value is None:
        return None
    return type(value)()
