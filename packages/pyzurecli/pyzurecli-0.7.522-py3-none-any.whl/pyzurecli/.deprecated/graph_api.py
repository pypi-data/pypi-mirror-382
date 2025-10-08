# from functools import cached_property
#
# import httpx
# import pandas as pd
# from loguru import logger as log
# from toomanyconfigs.simple_api import SimpleAPI, SimpleAPIResponse
#
# from src.pyzurecli.models import Email, Me, Organization, Person
#
#     def last_received_messages(self, num):
#         response = self.safe_request(method="get",
#                                      path=f"/me/messages?$filter=isDraft eq false and parentFolderId ne 'SentItems'&$select={self.email_filters}&$top={num}")
#         val = response.body.get("value")
#         return val
#
#     def last_sent_messages(self, num):
#         response = self.safe_request(method="get",
#                                      path=f"/me/mailFolders/SentItems/messages?$select={self.email_filters}&$top={num}")
#         val = response.body.get("value")
#         return val
#
#     def list_messages_to_person(self, email) -> list:
#         log.debug(f"{self}: Getting messages with {email}")
#         data = self.sent_messages
#         msgs = []
#         num = 0
#         for each in data:
#             # print(each)
#             receps: dict = each.get("toRecipients")
#             for person in receps:
#                 # print(person)
#                 target = person.get("emailAddress").get("address")
#                 if target == email:
#                     num = num + 1
#                     msgs.append(each)
#         log.debug(f"{self}: Found {num} messages sent to {email}")
#         return msgs
#
#     def list_messages_from_person(self, email) -> list:
#         log.debug(f"{self}: Getting messages from {email}")
#         data = self.received_messages
#         msgs = []
#         num = 0
#         for each in data:
#             # print(each)
#             target = each.get("sender").get("emailAddress").get("address")
#             if target == email:
#                 num = num + 1
#                 msgs.append(each)
#         log.debug(f"{self}: Found {num} messages from {email}")
#         return msgs
#
#     def list_messages_with_person(self, email) -> dict:
#         log.debug(f"{self}: Getting messages with {email}")
#         msgs_from = self.messages_from_person(email)
#         if not msgs_from: msgs_from = []
#         msgs_to = self.messages_to_person(email)
#         if not msgs_to: msgs_to = []
#         total = {
#             "target_email": email,
#             "messages_from": msgs_from,
#             "messages_to": msgs_to
#         }
#         num = len(msgs_from) + len(msgs_to)
#         log.debug(f"{self}: Found {num} messages with {email}")
#         return total
#
#     def dataframe_messages_to_person(self, email) -> pd.DataFrame:
#         log.debug(f"{self}: Getting messages to {email} as dataframe")
#         msgs = self.list_messages_to_person(email)
#
#         records = []
#         for msg in msgs:
#             records.append({
#                 'id': msg.get('id', ''),
#                 'subject': msg.get('subject', ''),
#                 'sender_name': msg.get('sender', {}).get('emailAddress', {}).get('name', ''),
#                 'sender_email': msg.get('sender', {}).get('emailAddress', {}).get('address', ''),
#                 'recipient_emails': [r.get('emailAddress', {}).get('address', '') for r in msg.get('toRecipients', [])],
#                 'date': msg.get('sentDateTime', '')[:10] if msg.get('sentDateTime') else '',
#                 'time': msg.get('sentDateTime', '')[11:].replace("Z", "") if msg.get('sentDateTime') else ''
#             })
#
#         df = pd.DataFrame(records)
#         log.debug(f"{self}: Created dataframe with {len(df)} records for {email}")
#         return df
#
#     def dataframe_messages_from_person(self, email) -> pd.DataFrame:
#         log.debug(f"{self}: Getting messages from {email} as dataframe")
#         msgs = self.list_messages_from_person(email)
#
#         records = []
#         for msg in msgs:
#             records.append({
#                 'id': msg.get('id', ''),
#                 'subject': msg.get('subject', ''),
#                 'sender_name': msg.get('sender', {}).get('emailAddress', {}).get('name', ''),
#                 'sender_email': msg.get('sender', {}).get('emailAddress', {}).get('address', ''),
#                 'recipient_emails': [r.get('emailAddress', {}).get('address', '') for r in msg.get('toRecipients', [])],
#                 'date': msg.get('sentDateTime', '')[:10] if msg.get('sentDateTime') else '',
#                 'time': msg.get('sentDateTime', '')[11:].replace("Z", "") if msg.get('sentDateTime') else ''
#             })
#
#         df = pd.DataFrame(records)
#         log.debug(f"{self}: Created dataframe with {len(df)} records for {email}")
#         return df
#
#     def dataframe_messages_with_person(self, email) -> pd.DataFrame:
#         log.debug(f"{self}: Getting messages with {email} as dataframe")
#
#         # Get messages from both directions
#         msgs_to = self.dataframe_messages_to_person(email)
#         msgs_from = self.dataframe_messages_from_person(email)
#
#         # Add direction column to distinguish message types
#         msgs_to['direction'] = 'sent'
#         msgs_from['direction'] = 'received'
#
#         # Combine DataFrames
#         combined_df = pd.concat([msgs_to, msgs_from], ignore_index=True)
#
#         # Sort by date and time for chronological order
#         combined_df['datetime'] = combined_df['date'] + ' ' + combined_df['time']
#         combined_df = combined_df.sort_values('datetime', ascending=False)
#         combined_df = combined_df.drop('datetime', axis=1)  # Remove temp column
#
#         log.debug(f"{self}: Created combined dataframe with {len(combined_df)} records for {email}")
#         return combined_df
#
#     def get_filtered_people(self, amt: int = 1000, filters: list = None):
#         """Simple request to get people from Graph API"""
#         log.debug(f"{self}: Getting {amt} people from People API")
#         me = self.me
#         my_email = str(me.userPrincipalName).rsplit("@")[1]
#         default_filter = ["NETORG"] + [my_email]
#         if filters:
#             if not isinstance(filters, list): raise TypeError(f"'Filters' must be a list, got {type(filters)} instead")
#             default_filter = default_filter + filters
#         log.debug(f"{self}: Filtering out '{default_filter}'")
#         response = self.safe_request(method="get",
#                                      path=f"me/people?$top={amt}&$select=id,displayName,userPrincipalName,scoredEmailAddresses")
#         val = response.body.get("value")
#         log.debug(f"{self}: Collected {len(val)} people from API")
#         filtered_people = []
#         excluded = 0
#         for person in val:
#             exclude = False
#             try: email = person.get("scoredEmailAddresses")[0].get("address").rsplit("@")[1]
#             except Exception:
#                 excluded = excluded + 1
#                 continue
#             for filter in default_filter:
#                 if filter in email:
#                     excluded = excluded + 1
#                     exclude = True
#                     break
#             if not exclude: filtered_people.append(person)
#
#         log.debug(f"{self}: Collected {len(filtered_people)} people, excluded {excluded}.")
#         return filtered_people
#
#         # # Convert to Person objects
#         # people = []
#         # for person_data in info['value']:
#         #     try:
#         #         person = Person(**person_data)
#         #         people.append(person)
#         #     except Exception as e:
#         #         log.error(f"{self}: Error creating Person object: {e}")
#         #         continue
#
#         # log.info(f"{self}: Found {len(people)} people")
#         # return people
#
#
#
#     # def _get_messages(self, filter_query=None, select_fields=None, order_by=None, top=None):
#     #     """
#     #     Base method to get messages with optional filtering
#     #
#     #     Args:
#     #         filter_query (str): OData filter string
#     #         select_fields (str): Comma-separated list of fields to select
#     #         order_by (str): Field to order by
#     #         top (int): Number of messages to return
#     #     """
#     #     params = {}
#     #
#     #     if filter_query:
#     #         params["$filter"] = filter_query
#     #     if select_fields:
#     #         params["$select"] = select_fields
#     #     if order_by:
#     #         params["$orderby"] = order_by
#     #     if not top:
#     #         params["$top"] = 1000
#     #
#     #     log.debug(f"Getting messages with params: {params}")
#     #
#     #     try:
#     #         info = self.request("get", "me/messages", params=params)
#     #     except Exception as e:
#     #         raise
#     #
#     #     if not info or 'value' not in info:
#     #         log.warning(f"{self}: No messages found or invalid response")
#     #         return []
#     #
#     #     # Get current user email for direction detection
#     #     current_user_email = self.me.userPrincipalName
#     #
#     #     # Convert each message to Email object
#     #     email_objects = []
#     #     for message_data in info['value']:
#     #         try:
#     #             email = Email(**message_data)
#     #             email_objects.append(email)
#     #         except Exception as e:
#     #             log.error(f"{self}: Error creating Email object: {e}")
#     #             raise
#     #
#     #     log.info(f"{self}: Converted {len(email_objects)} messages to Email objects")
#     #     return email_objects
#     #
#     # def get_messages_from_sender(self, sender_email):
#     #     """Get messages from a specific sender"""
#     #     filter_query = f"from/emailAddress/address eq '{sender_email}'"
#     #     return self._get_messages(filter_query=filter_query)
#     #
#     # def get_messages_to_recipient(self, recipient_email):
#     #     """Get messages sent to a specific recipient"""
#     #     # filter_query = f"toRecipients/any(r:(r/emailAddress/address eq '{recipient_email}'))"
#     #     return self.search_messages(f"'to: {recipient_email}'")
#     #
#     # def get_conversation_with(self, target_email):
#     #     """Get all messages in conversation with a specific email address"""
#     #     filter_query = f"(from/emailAddress/address eq '{target_email}') or (toRecipients/any(r: r/emailAddress/address eq '{target_email}')) or (ccRecipients/any(r: r/emailAddress/address eq '{target_email}'))"
#     #     return self._get_messages(filter_query=filter_query, order_by="sentDateTime desc")
#     #
#     # def get_all_messages_with(self, email_address):
#     #     """Get all messages either sent to or received from a specific email address"""
#     #     # Try getting messages from sender first
#     #     from_messages = self.get_messages_from_sender(email_address)
#     #     # Then get messages to recipient
#     #     to_messages = self.get_messages_to_recipient(email_address)
#     #
#     #     # Combine and deduplicate based on message ID
#     #     all_messages = from_messages + to_messages
#     #     seen_ids = set()
#     #     unique_messages = []
#     #
#     #     for msg in all_messages:
#     #         if msg.id not in seen_ids:
#     #             seen_ids.add(msg.id)
#     #             unique_messages.append(msg)
#     #
#     #     # Sort by sentDateTime descending
#     #     unique_messages.sort(key=lambda msg: msg.sentDateTime, reverse=True)
#     #     return unique_messages
#     #
#     # def get_conversations_with(self, target_email):
#     #     """Get all conversations with a specific email address, grouped by conversationId"""
#     #     messages = self.get_conversation_with(target_email)
#     #
#     #     # Group messages by conversationId
#     #     conversations = {}
#     #     for message in messages:
#     #         conv_id = message.conversationId
#     #         if conv_id not in conversations:
#     #             conversations[conv_id] = []
#     #         conversations[conv_id].append(message)
#     #
#     #     # Sort messages within each conversation by sentDateTime
#     #     for conv_id in conversations:
#     #         conversations[conv_id].sort(key=lambda msg: msg.sentDateTime)
#     #
#     #     log.info(f"{self}: Found {len(conversations)} conversations with {target_email}")
#     #     return conversations
#     #
#     # def get_latest_conversation_with(self, target_email):
#     #     """Get the most recent conversation with a specific email address"""
#     #     conversations = self.get_conversations_with(target_email)
#     #
#     #     if not conversations:
#     #         return []
#     #
#     #     # Find the conversation with the most recent message
#     #     latest_conv_id = None
#     #     latest_timestamp = None
#     #
#     #     for conv_id, messages in conversations.items():
#     #         # Get the latest message in this conversation
#     #         latest_msg = max(messages, key=lambda msg: msg.sentDateTime)
#     #         if latest_timestamp is None or latest_msg.sentDateTime > latest_timestamp:
#     #             latest_timestamp = latest_msg.sentDateTime
#     #             latest_conv_id = conv_id
#     #
#     #     return conversations[latest_conv_id]
#     #
#     # def get_unread_messages(self):
#     #     """Get all unread messages"""
#     #     filter_query = "isRead eq false"
#     #     return self._get_messages(filter_query=filter_query)
#     #
#     # def get_messages_with_attachments(self):
#     #     """Get messages that have attachments"""
#     #     filter_query = "hasAttachments eq true"
#     #     return self._get_messages(filter_query=filter_query)
#     #
#     # def get_messages_by_subject(self, subject_keyword):
#     #     """Get messages containing keyword in subject"""
#     #     filter_query = f"contains(subject, '{subject_keyword}')"
#     #     return self._get_messages(filter_query=filter_query)
#     #
#     # def get_messages_by_importance(self, importance_level="high"):
#     #     """Get messages by importance level (low, normal, high)"""
#     #     filter_query = f"importance eq '{importance_level}'"
#     #     return self._get_messages(filter_query=filter_query)
#     #
#     # def get_recent_messages(self, days=7):
#     #     """Get messages from the last N days"""
#     #     from datetime import datetime, timedelta
#     #     cutoff_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
#     #     filter_query = f"receivedDateTime ge {cutoff_date}"
#     #     return self._get_messages(
#     #         filter_query=filter_query,
#     #         order_by="receivedDateTime desc"
#     #     )
#     #
#     # def search_messages(self, search_term):
#     #     """Search messages by content (requires search endpoint)"""
#     #     # Note: This uses the search endpoint which has different syntax
#     #     search_params = {
#     #         "$search": f'"{search_term}"'
#     #     }
#     #
#     #     log.debug(f"Searching messages with term: {search_term}")
#     #
#     #     info = self.request("get", "me/messages", params=search_params)
#     #
#     #     if not info or 'value' not in info:
#     #         log.warning(f"{self}: No search results found")
#     #         return []
#     #
#     #     current_user_email = self.me.userPrincipalName
#     #     email_objects = []
#     #
#     #     for message_data in info['value']:
#     #         try:
#     #             email = Email(**message_data)
#     #             email_objects.append(email)
#     #         except Exception as e:
#     #             log.error(f"{self}: Error creating Email object from search: {e}")
#     #             continue
#     #
#     #     log.info(f"{self}: Found {len(email_objects)} messages matching search term")
#     #     return email_objects
#     #
#     # def send_email(self, to_recipients, subject, body, cc_recipients=None, bcc_recipients=None, attachments=None):
#     #     """Send an email using Microsoft Graph"""
#     #
#     #     def format_recipients(recipients):
#     #         """Convert email addresses to Graph API format"""
#     #         if isinstance(recipients, str):
#     #             recipients = [recipients]
#     #         return [{"emailAddress": {"address": email}} for email in recipients]
#     #
#     #     email_data = {
#     #         "message": {
#     #             "subject": subject,
#     #             "body": {
#     #                 "contentType": "HTML",  # or "Text"
#     #                 "content": body
#     #             },
#     #             "toRecipients": format_recipients(to_recipients)
#     #         }
#     #     }
#     #
#     #     # Add optional recipients
#     #     if cc_recipients:
#     #         email_data["message"]["ccRecipients"] = format_recipients(cc_recipients)
#     #
#     #     if bcc_recipients:
#     #         email_data["message"]["bccRecipients"] = format_recipients(bcc_recipients)
#     #
#     #     # Add attachments if provided
#     #     if attachments:
#     #         email_data["message"]["attachments"] = attachments
#     #
#     #     log.debug(f"Sending email to: {to_recipients}")
#     #
#     #     try:
#     #         response = self.request("POST", "me/sendMail", json_body=email_data)
#     #         log.info(f"Email sent successfully to: {to_recipients}")
#     #         return response
#     #     except Exception as e:
#     #         log.error(f"Failed to send email: {e}")
#     #         raise
#     #
#     #
#     # def request(self, method, resource, params: dict = None, headers=None, json_body=None):
#     #     url = f"{self.base_url}/{resource}"
#     #
#     #     request_headers = self.headers.copy()
#     #     if headers:
#     #         request_headers.update(headers)
#     #
#     #     log.info(f"{self}: Sending {method.upper()} request to: {url}")
#     #
#     #     try:
#     #         with httpx.Client() as client:
#     #             response = client.request(
#     #                 method=method.upper(),
#     #                 url=url,
#     #                 headers=request_headers,
#     #                 params=params,
#     #                 json=json_body
#     #             )
#     #
#     #             if not response.is_success:
#     #                 log.error(f"{self}: Error {response.status_code}: {response.text}")
#     #                 raise ConnectionRefusedError(f"Error {response.status_code}: {response.text}")
#     #
#     #             return response.json()
#     #
#     #     except Exception as e:
#     #         log.exception(f"{self}: Request failed: {e}")
#     #         raise
