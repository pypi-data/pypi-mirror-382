from typing import Annotated

from .. import _GraphAPIMethods, debug, _GraphAPIProperties, validate_range

def _process_default_people_filter(filter):
    if not isinstance(filter, list):
        raise TypeError(f"Default people filter is not list, got {filter.__class__}")
    return filter


# noinspection PyShadowingBuiltins
def _process_people_filter(default_filter: list = [], filter_override: list | None = [], filter_append = []):
    if not (isinstance(filter_override, list)) or not (isinstance(filter_append, list)):
        if filter_override is None: pass #Run without filter
        else: raise TypeError(f"Filter override or append is not list, got {filter_override.__class__} and {filter_append.__class__} instead")
    filter = default_filter
    if len(filter_override) > 0: filter = filter_override
    else:
        if len(filter_append) > 0: filter = filter + filter_append
    return filter

async def get_filtered_people(self: _GraphAPIProperties, filter_override: list = None, filter_append: list = None, top: Annotated[int, validate_range(1, 999)] = 999):
    # me = self.me
    # my_email = str(me.userPrincipalName).rsplit("@")[1]
    response = await self.safe_request(
        method="GET",
        path=f"me/people?$select=id,displayName,userPrincipalName,scoredEmailAddresses$top={top}"
    )
    val = response.body.get("value")
    debug(f"{self}: Collected {len(val)} people from API")

    filter = _process_people_filter(
        default_filter=self.people_filters,
        filter_override=filter_override,
        filter_append=filter_append,
    )
    debug(f"{self}: Filtering out '{filter}'")
    filtered_people = []
    excluded = 0
    for person in val:
        exclude = False
        try:
            email = person.get("scoredEmailAddresses")[0].get("address").rsplit("@")[1]
        except Exception:
            excluded = excluded + 1
            continue
        for cur_filter in filter:
            if cur_filter in email:
                excluded = excluded + 1
                exclude = True
                break
        if not exclude: filtered_people.append(person)

    debug(f"Collected {len(filtered_people)} people, excluded {excluded}.")
    return filtered_people