from types import SimpleNamespace

import requests
from requests.adapters import HTTPAdapter

from digisearch.services import http_client


class FakeResponse:
    def __init__(self, payload=None, status=200, bad_json=False):
        self.payload = payload
        self.status = status
        self.bad_json = bad_json

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status} error")

    def json(self):
        if self.bad_json:
            raise ValueError("not json")
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        if self.error:
            raise self.error
        return self.response


def use_fake_session(monkeypatch, session):
    sleeps = []
    monkeypatch.setattr(http_client, "get_session", lambda: session)
    monkeypatch.setattr(http_client, "time", SimpleNamespace(sleep=sleeps.append))
    return sleeps


def test_get_json_returns_parsed_body(monkeypatch):
    session = FakeSession(FakeResponse({"ok": True}))
    use_fake_session(monkeypatch, session)

    assert http_client.get_json("https://x.test/a") == {"ok": True}


def test_get_json_sleeps_between_requests_and_sets_timeout(monkeypatch):
    session = FakeSession(FakeResponse({}))
    sleeps = use_fake_session(monkeypatch, session)

    http_client.get_json("https://x.test/a")

    assert sleeps == [http_client.DELAY]
    assert session.calls[0]["timeout"] == http_client.TIMEOUT


def test_get_json_passes_query_params(monkeypatch):
    session = FakeSession(FakeResponse({}))
    use_fake_session(monkeypatch, session)

    http_client.get_json("https://x.test/a", page=3)
    http_client.get_json("https://x.test/b")

    assert session.calls[0]["params"] == {"page": 3}
    assert session.calls[1]["params"] is None      # no params -> None, not {}


def test_get_json_returns_none_on_http_error(monkeypatch):
    use_fake_session(monkeypatch, FakeSession(FakeResponse(status=500)))
    assert http_client.get_json("https://x.test/a") is None


def test_get_json_returns_none_on_network_errors(monkeypatch):
    for error in (requests.ConnectionError("down"), requests.Timeout("slow")):
        use_fake_session(monkeypatch, FakeSession(error=error))
        assert http_client.get_json("https://x.test/a") is None


def test_get_json_returns_none_on_invalid_json(monkeypatch):
    use_fake_session(monkeypatch, FakeSession(FakeResponse(bad_json=True)))
    assert http_client.get_json("https://x.test/a") is None


def test_get_session_is_a_singleton_with_retry_policy(monkeypatch):
    monkeypatch.setattr(http_client, "_session", None)

    first = http_client.get_session()
    assert http_client.get_session() is first

    adapter = first.get_adapter("https://api.digikala.com")
    assert isinstance(adapter, HTTPAdapter)
    retry = adapter.max_retries
    assert retry.total == 4
    assert retry.backoff_factor == 1
    assert 429 in retry.status_forcelist and 503 in retry.status_forcelist
    assert retry.allowed_methods is not None
    assert "GET" in retry.allowed_methods
    assert retry.respect_retry_after_header is True