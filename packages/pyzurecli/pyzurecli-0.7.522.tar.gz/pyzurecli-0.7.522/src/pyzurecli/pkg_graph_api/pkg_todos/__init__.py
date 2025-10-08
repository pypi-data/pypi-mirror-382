from typing import Literal, Dict, Optional
from urllib.parse import quote
from .. import _GraphAPIMethods

class DueDateTime(dict):
    def __init__(self, dateTime: str, timeZone: str):
        super().__init__()
        self["dateTime"] = dateTime
        self["timeZone"] = timeZone


class ToDo:
    def __init__(self, graph: _GraphAPIMethods):
        self.graph = graph

    async def get_lists(self, filter: str = None):
        path = "/me/todo/lists"
        if filter:
            path += f"?$filter={quote(filter)}"

        response = await self.graph.safe_request(
            method="GET",
            path=path
        )
        return response

    async def get_lists_filtered(self, displayName: str = None, startsWith: str = None, contains: str = None):
        if displayName:
            filter_query = f"displayName eq '{displayName}'"
        elif startsWith:
            filter_query = f"startswith(displayName, '{startsWith}')"
        elif contains:
            filter_query = f"contains(displayName, '{contains}')"
        else:
            return await self.get_lists()

        return await self.get_lists(filter=filter_query)

    async def post_list(self, displayName: str):
        data = {
            "displayName": displayName
        }
        response = await self.graph.safe_request(
            method="POST",
            path="/me/todo/lists",
            json=data
        )
        return response

    async def delete_list(self, id: str):
        response = await self.graph.safe_request(
            method="DELETE",
            path=f"/me/todo/lists/{id}"
        )
        return response

    async def post_task(self, taskListId: str, title: str, body: str = None, importance: Literal["low", "normal", "high"] = None, status: Literal["notStarted", "inProgress", "completed", "waitingOnOthers", "deferred"] = None, dueDateTime: DueDateTime = None, isReminderOn: bool = False):
        data = {}
        if title: data["title"] = title
        if body: data["body"] = {"content": body, "contentType": "text"}
        if importance: data["importance"] = importance
        if status: data["status"] = status
        if dueDateTime: data["dueDateTime"] = dueDateTime
        if isReminderOn: data["isReminderOn"] = isReminderOn
        response = await self.graph.safe_request(
            method="POST",
            path=f"/me/todo/lists/{taskListId}/tasks",
            json=data
        )
        return response

    async def patch_task(self, taskListId: str, taskId: str, title: str = None, body: str = None, importance: Literal["low", "normal", "high"] = None, status: Literal["notStarted", "inProgress", "completed", "waitingOnOthers", "deferred"] = None, dueDateTime: DueDateTime = None, isReminderOn: bool = None):
        data = {}
        if title: data["title"] = title
        if body: data["body"] = {"content": body, "contentType": "text"}
        if importance: data["importance"] = importance
        if status: data["status"] = status
        if dueDateTime: data["dueDateTime"] = dueDateTime
        if isReminderOn is not None: data["isReminderOn"] = isReminderOn
        response = await self.graph.safe_request(
            method="PATCH",
            path=f"/me/todo/lists/{taskListId}/tasks/{taskId}",
            json=data
        )
        return response

    async def delete_task(self, taskListId: str, taskId: str):
        response = await self.graph.safe_request(
            method="DELETE",
            path=f"/me/todo/lists/{taskListId}/tasks/{taskId}"
        )
        return response

    async def get_tasks(self, taskListId: str, filter: str = None):
        path = f"/me/todo/lists/{taskListId}/tasks"
        if filter:
            path += f"?$filter={quote(filter)}"

        response = await self.graph.safe_request(
            method="GET",
            path=path
        )
        return response

    async def get_tasks_filtered(self,
       taskListId: str,
       title: str = None,
       titleStartsWith: str = None,
       titleContains: str = None,
       status: Literal["notStarted", "inProgress", "completed", "waitingOnOthers", "deferred"] = None,
       importance: Literal["low", "normal", "high"] = None):
        filters = []

        if title:
            filters.append(f"title eq '{title}'")
        elif titleStartsWith:
            filters.append(f"startswith(title, '{titleStartsWith}')")
        elif titleContains:
            filters.append(f"contains(title, '{titleContains}')")

        if status:
            filters.append(f"status eq '{status}'")
        if importance:
            filters.append(f"importance eq '{importance}'")

        if not filters:
            return await self.get_tasks(taskListId)

        filter_query = " and ".join(filters)
        return await self.get_tasks(taskListId, filter=filter_query)