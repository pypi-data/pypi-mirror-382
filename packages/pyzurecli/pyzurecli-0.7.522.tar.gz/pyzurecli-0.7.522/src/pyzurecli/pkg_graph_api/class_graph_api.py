from functools import cached_property
from typing import Literal, Annotated

from toomanyconfigs.simple_api import SimpleAPI

from . import _DEBUG, validate_range
from ..models import Me, Organization

class _GraphAPIInit(SimpleAPI):
    def __init__(self, token: str, version: str = "v1.0", email_filters: list | None = None,
                 people_filters: list | None = None, _debug: bool = _DEBUG):
        self._debug = _debug
        self._token: str = token
        self._version = version.strip("/")
        self._email_filters: list = email_filters
        self._people_filters: list = people_filters
        SimpleAPI.__init__(
            self,
            base_url=f"https://graph.microsoft.com/{self._version}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                # "Prefer": "return=representation"
            }
        )

    def __repr__(self):
        return f"[GraphAPI.{self._token[:8]}]"

    async def safe_request(self, method: Literal["GET", "POST", "PATCH", "DELETE"], path: str, **kwargs):
        from .pkg_safe_request import safe_request
        return await safe_request(self, method, path, **kwargs)

    def sync_safe_request(self, method: Literal["GET", "POST", "PATCH", "DELETE"], path: str, **kwargs):
        from .pkg_safe_request import sync_safe_request
        return sync_safe_request(self, method, path, **kwargs)


class _GraphAPIProperties(_GraphAPIInit):
    def __init__(self, token: str, version: str = "v1.0", email_filters: list | None = None,
                 people_filters: list | None = None, _debug: bool = _DEBUG):
        super().__init__(token, version, email_filters, people_filters, _debug)

    @cached_property
    def email_filters(self):
        from .pkg_filters import email_filters
        return email_filters(self._email_filters)

    @cached_property
    def people_filters(self) -> list["str"]:
        from .pkg_filters import _process_default_people_filter
        return _process_default_people_filter(self._people_filters)

    @property
    def me(self):
        response = self.sync_safe_request(method="GET", path="me")
        return Me(**response.body)

    @property
    def organization(self):
        response = self.sync_safe_request(method="GET", path="organization")
        val = response.body.get("value")[0]
        return Organization(**val)

    @property
    def people(self):
        from .pkg_filters import get_filtered_people
        return get_filtered_people(self)


class _GraphAPIMethods(_GraphAPIProperties):
    def __init__(self, token: str, version: str = "v1.0", email_filters: list | None = None,
                 people_filters: list | None = None, _debug: bool = _DEBUG):
        super().__init__(token, version, email_filters, people_filters, _debug)

    async def list_received_messages_from_person(self, person: str, top: Annotated[int, validate_range(1, 999)] = 999):
        from .pkg_messages import list_received_messages_from_person
        return await list_received_messages_from_person(self, person, top)

    async def list_sent_messages_to_person(self, person: str, top: Annotated[int, validate_range(1, 999)] = 999):
        from .pkg_messages import list_sent_messages_to_person
        return await list_sent_messages_to_person(self, person, top)

    async def list_messages_with_person(self, person: str, top: Annotated[int, validate_range(1, 999)] = 999) -> dict:
        from .pkg_messages import list_messages_with_person
        return await list_messages_with_person(self, person, top)

    async def list_filtered_people(self, filter_append: list | None = None, filter_override: list | None = None, top: Annotated[int, validate_range(1, 999)] = 999):
        from .pkg_filters import get_filtered_people
        get_filtered_people(self, filter_override, filter_append, top)

    async def list_conversations_with_person(self, person: str, top: Annotated[int, validate_range(1, 999)] = 999):
        from .pkg_messages import list_conversations_with_person
        return await list_conversations_with_person(self, person, top)

    async def get_conversation(self, conversation_id: str, get_message_content: bool = True, top: Annotated[int, validate_range(1, 999)] = 999):
        from .pkg_messages import get_conversation
        return await get_conversation(self, conversation_id, get_message_content, top)

    @cached_property
    def todo(self):
        from .pkg_todos import ToDo
        return ToDo(self)

class GraphAPI(_GraphAPIMethods):
    def __init__(self, token: str, version: str = "v1.0", email_filters: list | None = None,
                 people_filters: list | None = None, _debug: bool = _DEBUG):
        super().__init__(token, version, email_filters, people_filters, _debug)
