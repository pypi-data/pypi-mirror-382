from typing import Annotated, Any

from loguru import logger as log

from . import _GraphAPIMethods, is_valid_email_regex
from .. import debug, validate_range
from ..pkg_type_check_emails import type_check_emails


async def list_received_messages_from_person(self: _GraphAPIMethods, person: str,
                                             top: Annotated[int, validate_range(1, 999)] = 999):
    if not is_valid_email_regex(person): raise TypeError("Not a valid email, got {person} instead")
    response = await self.safe_request(
        method="GET",
        path=f"/me/messages?$filter=(from/emailAddress/address) eq '{person}'&$select={self.email_filters}&$top={top}"
    )
    log.debug(f"{self}: Collected raw response:\n {response.body}")
    return type_check_emails(response.body)


async def list_sent_messages_to_person(self: _GraphAPIMethods, person: str,
                                       top: Annotated[int, validate_range(1, 999)] = 999):
    if not is_valid_email_regex(person): raise TypeError("Not a valid email, got {person} instead")
    response = await self.safe_request(
        method="GET",
        path=f'/me/mailFolders/SentItems/messages?$search="to:{person}"&$select={self.email_filters}&$top={top}'
    )
    log.debug(f"{self}: Collected raw response:\n {response.body}")
    return type_check_emails(response.body)


async def list_messages_with_person(self: _GraphAPIMethods, person: str,
                                    top: Annotated[int, validate_range(1, 999)] = 999) -> dict:
    if not is_valid_email_regex(person): raise TypeError("Not a valid email, got {person} instead")
    msgs_from = await self.list_received_messages_from_person(person, top)
    if not msgs_from: msgs_from = []
    msgs_to = await self.list_sent_messages_to_person(person, top)
    if not msgs_to: msgs_to = []
    total = {
        "messages_from": msgs_from,
        "messages_to": msgs_to
    }
    top = len(msgs_from) + len(msgs_to)
    debug(f"Found {top} messages with {person}")
    return total


async def list_conversations_with_person(self: _GraphAPIMethods, person: str,
                                         top: Annotated[int, validate_range(1, 999)] = 999) -> list[dict]:
    if not is_valid_email_regex(person): raise TypeError("Not a valid email, got {person} instead")
    messages_from = await self.list_received_messages_from_person(person, top)
    if not messages_from: messages_from = []
    messages_to = await self.list_sent_messages_to_person(person, top)
    if not messages_to: messages_to = []
    conversations = []
    earliest_messages = {}

    def process_group(messages, is_from_you: bool):
        sender = self.me.displayName if is_from_you else person

        for message in messages:
            conversation_id = message.get("conversationId")
            if not conversation_id:
                raise KeyError(f"Missing key, 'conversationId' in {message}")

            message_date = message.get("receivedDateTime")
            subject = message.get("subject")

            if conversation_id not in conversations:
                conversations.append(conversation_id)
                earliest_messages[conversation_id] = (message_date, subject, sender)
            else:
                current_earliest = earliest_messages[conversation_id][0]
                if message_date and (not current_earliest or message_date < current_earliest):
                    earliest_messages[conversation_id] = (message_date, subject, sender)

    process_group(messages_from, False)
    process_group(messages_to, True)

    conversations_list = [
        {
            "id": conv_id,
            "timestamp": earliest_messages[conv_id][0],
            "title": earliest_messages[conv_id][1],
            "lastMessage": earliest_messages[conv_id][1],
            "sender": earliest_messages[conv_id][2]
        }
        for conv_id in conversations
    ]

    num_of_conversations = len(conversations_list)
    num_of_messages = len(messages_from) + len(messages_to)
    average_messages = (num_of_messages / num_of_conversations) if num_of_conversations > 0 else 0
    log.debug(
        f"[organize_into_conversations]: Got {num_of_conversations} conversations from {num_of_messages} messages, with an average of {average_messages} messages per conversation.")

    return conversations_list