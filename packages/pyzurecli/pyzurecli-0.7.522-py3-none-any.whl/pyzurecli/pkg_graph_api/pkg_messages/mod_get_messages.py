from typing import Annotated

import html2text

from .. import _GraphAPIMethods, validate_range, type_check_emails

self: _GraphAPIMethods


async def get_conversation(self: _GraphAPIMethods, conversation_id: str, get_message_content: bool = True, top: Annotated[int, validate_range(1, 999)] = 999):
    if not conversation_id.strip(): raise TypeError(f"Invalid conversation_id, got {conversation_id} instead")
    if get_message_content:
        email_filters = self.email_filters + f",{",".join(["bccRecipients", "ccRecipients", "uniqueBody", "webLink", "attachments", "isRead"])}"
    else:
        email_filters = self.email_filters
    response = await self.safe_request(
        method="GET",
        path=f'https://graph.microsoft.com/v1.0/me/messages?$filter=conversationId eq \'{conversation_id}\'&$select={email_filters}&$top={top}'
    )
    emails = type_check_emails(response.body)
    if not (my_email := self.me.displayName): raise KeyError(f"Couldn't find user's email from '/me'")
    if get_message_content:
        for email in emails:
            if not (unique_body := email.get("uniqueBody")):
                raise KeyError(f"While get_message_content was '{get_message_content}', could not find body "
                               f"and/or unique body, got {email} instead... "
                               f"Do you have Mail.ReadWrite enabled?")
            else:
                try:
                    text_body = html2text.html2text(unique_body.get("content"))
                    email["content"] = text_body
                    del email["uniqueBody"]
                except Exception as e: raise RuntimeError(f"Could not compile text from html: {e}")
                if not (sender := email.get("sender").get("emailAddress").get("address")): raise KeyError(f"Could not find 'sender.emailAddress.address' in {email}")
                if sender == my_email: email["isFromMe"] = True
    return emails

async def message(self, id: str) -> dict:
    response = await self.safe_request(method="get", path=f"/me/messages/{id}")
    val = response.body.get("value")
    return val
