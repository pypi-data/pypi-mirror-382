def no_results(obj: any):
    if len(obj) == 0: return True
    return False

def is_graph_email_query(obj: dict):
    if "@odata.context" and "value" in obj.keys(): return True
    return False

def type_check_emails(emails: dict | list[dict]) -> list[dict]:
    from .. import debug
    type_checked_dicts: list[dict] = []
    if isinstance(emails, dict) or isinstance(emails, list):
        for item in emails:
            if not isinstance(item, dict): continue
            type_checked_dicts.append(item)
        if isinstance(emails, dict) and (no_results(type_checked_dicts)) and is_graph_email_query(emails):
            if isinstance(emails.get("value"), list): type_checked_dicts = emails.get("value")
    else: raise TypeError(f"Could not compile emails from param object, {emails}")
    if no_results(type_checked_dicts): raise TypeError(f"No sub-objects found in {emails.__class__.__name__}, got {emails} instead.")
    debug(f"Collected {len(type_checked_dicts)} emails from {emails.__class__}")
    return type_checked_dicts