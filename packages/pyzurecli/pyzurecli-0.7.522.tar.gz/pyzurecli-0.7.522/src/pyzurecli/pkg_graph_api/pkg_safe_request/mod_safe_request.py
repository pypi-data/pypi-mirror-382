from toomanyconfigs.simple_api import SimpleAPIResponse
from loguru import logger as log
from .. import _GraphAPIInit


def error_handling(response: SimpleAPIResponse):
    code = response.status
    if code not in [200, 201, 204]:
        msg = "Got unexpected status code" if not isinstance(response.body, dict) else response.body.get("error").get("message")
        if code >= 400:
            log.error(f"Got status-code >= 400: {msg}")
            log.error(f"Raw HTTP response: {response}")
            if code == 400:
                raise ConnectionRefusedError(msg)  # Can't process the request because it's malformed or incorrect.
            elif code == 401:
                raise PermissionError(
                    msg)  # Required authentication information is either missing or not valid for the resource.
            elif code == "InvalidAuthenticationToken":
                raise PermissionError(msg)
            elif code == 403:
                raise PermissionError(
                    msg)  # Access is denied to the requested resource. The user does not have enough permission or does not have a required license.
            else:
                raise PermissionError(msg)
    return response


async def safe_request(self, method: str, path: str, force_refresh: bool = True, **kwargs) -> SimpleAPIResponse:
    self: _GraphAPIInit
    try:
        response = await self.async_request(method, path, force_refresh, **kwargs)
        return error_handling(response)
    except Exception:
        raise


def sync_safe_request(self, method: str, path: str, force_refresh: bool = True, **kwargs) -> SimpleAPIResponse:
    self: _GraphAPIInit
    try:
        response = self.request(method, path, force_refresh, **kwargs)
        return error_handling(response)
    except Exception:
        raise
