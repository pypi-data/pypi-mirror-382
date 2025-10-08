import re

from .. import _GraphAPIMethods

def is_valid_email_regex(email: str) -> bool:
    """
    Checks if an email address has a valid format using a regular expression.
    """
    # A common regex for email validation (can be more strict or lenient)
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}$'
    return bool(re.fullmatch(regex, email))

from .mod_list_messages import list_sent_messages_to_person, list_received_messages_from_person, list_messages_with_person, list_conversations_with_person
from .mod_get_messages import get_conversation