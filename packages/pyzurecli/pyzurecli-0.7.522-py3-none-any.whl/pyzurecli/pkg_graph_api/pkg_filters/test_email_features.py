import pytest
from .mod_email_filters import email_filters, DEFAULT_FILTERS

@pytest.fixture
def bogus_filters():
    return None

def test_email_filters_none(bogus_filters):
    bar = email_filters(bogus_filters)
    assert bar == DEFAULT_FILTERS