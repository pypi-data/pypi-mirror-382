import time
import socket
import datetime
import readline
from omgui.spf import spf


def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available on the given host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def next_avail_port(host: str = "localhost", port: int = 8024) -> int:
    """
    Returns the next available port starting with 8024.

    This lets us avoid multiple apps trying to run on the same port.

    Note: Binding our server to the 0.0.0.0 interface would
    allow it to accept connections from any network interface
    on the host machine, in other words from external devices.
    """

    # Check if a port is open
    def _is_port_open(host, port):
        try:
            # Create a socket object and attempt to connect
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # Set a timeout for the connection attempt
                s.connect((host, port))
            return False  # Port is occupied
        except (ConnectionRefusedError, socket.timeout):
            return True  # Port is available

    while not _is_port_open(host, port):
        port += 1
    return port


def wait_for_port(host, port, timeout=5.0, interval=0.1):
    """
    Pauses the process until a given port
    starts accepting TCP connections.

    timeout & interval are expressed in seconds.
    """

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=interval):
                return True
        except OSError:
            # Keep retrying until the deadline is reached
            time.sleep(interval)
    # Timed out
    return False


# Confirm promt for True or False Questions
def confirm_prompt(question: str = "", default=False) -> bool:
    reply = None
    while reply not in ("y", "n"):
        try:
            spf(f"💭 <yellow>{question}</yellow>")
            reply = input("(y/n): ").casefold()
            readline.remove_history_item(readline.get_current_history_length() - 1)
        except KeyboardInterrupt:
            print("\n")
            return default
    if reply == "y":
        return True
    return False


def pretty_date(timestamp=None, style="log", include_time=True):
    """
    Prettify a timestamp.
    """
    # If no timestamp provided, use the current time
    if not timestamp:
        timestamp = time.time()

    # Choose the output format
    fmt = None
    if style == "log":
        fmt = "%d-%m-%Y"  # 07-01-2024
        if include_time:
            fmt += ", %H:%M:%S"  # 07-01-2024, 15:12:45
    elif style == "pretty":
        fmt = "%b %d, %Y"  # Jan 7, 2024
        if include_time:
            fmt += " at %H:%M"  # Jan 7, 2024 at 15:12
    else:
        raise ValueError(f"Invalid '{style}' style parameter")

    # Parse date/time string
    date_time = datetime.datetime.fromtimestamp(timestamp)
    return date_time.strftime(fmt)


def is_numeric(str_or_nr):
    """
    Check if a variable (string or number) is numeric.
    """
    try:
        float(str_or_nr)
        return True
    except ValueError:
        return False


def merge_dict_lists(list1, list2):
    """
    Merge two lists of dictionaries while avoiding duplicates.
    """
    # Convert dictionaries to tuples of sorted items
    list1_tuples = [tuple(sorted(d.items())) for d in list1]
    list2_tuples = [tuple(sorted(d.items())) for d in list2]

    # Perform set operations to merge the lists while avoiding duplicates
    merged_tuples = list1_tuples + list(set(list2_tuples) - set(list1_tuples))

    # Convert the tuples back to dictionaries
    merged_list = [dict(t) for t in merged_tuples]

    return merged_list


def encode_uri_component(string):
    """
    Python equivalent of JavaScript's encodeURIComponent.
    """
    from urllib.parse import quote

    return quote(string.encode("utf-8"), safe="~()*!.'")


def deep_merge(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    """

    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            deep_merge(dict1[key], value)
        else:
            # Otherwise, update or add the key-value pair
            dict1[key] = value
    return dict1


def is_dates(strings: list[str]) -> bool:
    """
    Checks if list of strings are all valid dates.

    Args:
        strings (list[str]): A list of strings to check.

    Returns:
        bool: True if all strings are valid dates, False otherwise.
    """
    from dateutil.parser import parse

    if not strings:
        return False

    for s in strings:
        try:
            parse(s, fuzzy=False)
        except (ValueError, TypeError):
            return False

    return True


def hash_data(data: dict) -> str:
    """
    Hashes a dictionary to create a deterministic ID.
    """
    import json
    import hashlib

    data_string = json.dumps(data, sort_keys=True)
    full_hash = hashlib.sha256(data_string.encode("utf-8")).hexdigest()

    # For a 8 character hash, you need 23.7 million items to have
    # a 50% chance of collision, which is acceptable considering
    # this is not a multi-user high volume application.
    return full_hash[:8]


def prune_dict(options: dict):
    """
    Remove None values from options dict.
    """
    return {k: v for k, v in options.items() if v is not None}
