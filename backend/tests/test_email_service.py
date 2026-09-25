import pytest

from app.services import email_service as email_service_module
from app.services.email_service import (
    EmailNotConfiguredError,
    email_service,
    send_welcome_email_best_effort,
)


class _FakeSettings:
    def __init__(self, smtp_username: str = "", smtp_password: str = "") -> None:
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.frontend_url = "http://localhost:5173"


def test_send_welcome_email_raises_when_not_configured(monkeypatch):
    monkeypatch.setattr(email_service_module, "get_settings", lambda: _FakeSettings())

    with pytest.raises(EmailNotConfiguredError):
        email_service.send_welcome_email("someone@example.com")


def test_send_welcome_email_sends_via_smtp(monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            calls["host"] = host
            calls["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, username, password):
            calls["login"] = (username, password)

        def sendmail(self, from_addr, to_addrs, message):
            calls["from_addr"] = from_addr
            calls["to_addrs"] = to_addrs
            calls["message"] = message

    monkeypatch.setattr(
        email_service_module,
        "get_settings",
        lambda: _FakeSettings("me@gmail.com", "app-password"),
    )
    monkeypatch.setattr(email_service_module.smtplib, "SMTP", FakeSMTP)

    email_service.send_welcome_email("someone@example.com")

    assert calls["host"] == "smtp.gmail.com"
    assert calls["port"] == 587
    assert calls["starttls"] is True
    assert calls["login"] == ("me@gmail.com", "app-password")
    assert calls["from_addr"] == "me@gmail.com"
    assert calls["to_addrs"] == ["someone@example.com"]
    assert "someone@example.com" in calls["message"]


def test_best_effort_swallows_not_configured_error(monkeypatch):
    monkeypatch.setattr(email_service_module, "get_settings", lambda: _FakeSettings())

    send_welcome_email_best_effort("someone@example.com")  # should not raise


def test_best_effort_swallows_generic_failures(monkeypatch):
    def raise_error(to_email):
        raise RuntimeError("smtp server exploded")

    monkeypatch.setattr(email_service, "send_welcome_email", raise_error)

    send_welcome_email_best_effort("someone@example.com")  # should not raise
