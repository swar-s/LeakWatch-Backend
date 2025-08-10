import re


def validate_email(email):
    """
    Validates if the input string is a valid email address.
    """
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None


def merge_all_parsed(h, d, i):
    """
    Merge parsed results from HIBP, DeHashed, and IntelX into one list.
    """
    return {
        "all_breaches": h + d + i
    }
