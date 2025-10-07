from email_inspector.free_providers import is_free_email, get_provider

def test_gmail():
    assert is_free_email("alice@gmail.com")
    assert get_provider("alice@gmail.com") == "gmail"

def test_corp():
    assert not is_free_email("ceo@acme.example")
    assert get_provider("ceo@acme.example") is None
