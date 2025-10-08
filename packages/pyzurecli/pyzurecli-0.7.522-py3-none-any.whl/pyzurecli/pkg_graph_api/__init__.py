_DEBUG = True
PREFIX = "GraphAPI"
from loguru import logger as log

def debug(msg: str):
    if not isinstance(msg, str): raise TypeError(f"Msg not str, got {msg.__class__} instead")
    if _DEBUG: log.debug(f"[{PREFIX}]: {msg}")

#Before Graph importation
from .pkg_type_check_emails import type_check_emails
from .mod_util import validate_range

from .class_graph_api import _GraphAPIInit, _GraphAPIProperties, _GraphAPIMethods, GraphAPI

#AFTER Graph importation
from .pkg_messages import list_sent_messages_to_person, list_received_messages_from_person, list_messages_with_person
from .pkg_filters import email_filters
