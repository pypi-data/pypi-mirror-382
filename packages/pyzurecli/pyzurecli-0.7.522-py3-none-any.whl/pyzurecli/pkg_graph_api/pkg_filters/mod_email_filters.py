DEFAULT_FILTERS = "sender,subject,toRecipients,receivedDateTime,conversationId"

def email_filters(fil):
    if not (filters := fil):
        return DEFAULT_FILTERS
    elif isinstance(filters, list):
        return ",".join(filters)
    elif not isinstance(filters, list):
        raise TypeError(f"Email filters must be list of strs, got {filters.__class__} instead")