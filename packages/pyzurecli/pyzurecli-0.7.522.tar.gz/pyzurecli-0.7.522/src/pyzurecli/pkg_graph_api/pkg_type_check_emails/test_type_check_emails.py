import pytest

from . import type_check_emails
from .mock_type_check_emails import mock_email_correct, mock_email_incorrect, mock_email_half_correct

def test_type_check_emails_correct(mock_email_correct):
    foo = type_check_emails(mock_email_correct)
    try:
        assert (isinstance(foo, list))
    except AssertionError as e:
        raise AssertionError(f"Got {foo.__class__} instead")

def test_type_check_emails_half_correct(mock_email_half_correct):
    foo = type_check_emails(mock_email_half_correct)
    try:
        assert (isinstance(foo, list))
    except AssertionError as e:
        raise AssertionError(f"Got {foo.__class__} instead")

def test_type_check_emails_incorrect(mock_email_incorrect):
    with pytest.raises(TypeError):
        foo = type_check_emails(mock_email_incorrect)
