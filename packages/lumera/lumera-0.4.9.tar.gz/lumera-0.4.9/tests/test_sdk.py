import json

import pytest
import requests

import lumera.sdk as sdk
from lumera.sdk import (
    FileRef,
    LumeraAPIError,
    RecordNotUniqueError,
    create_collection,
    create_record,
    get_collection,
    get_record_by_external_id,
    list_collections,
    resolve_path,
    to_filerefs,
    update_record,
)


class DummyResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        json_data: dict | None = None,
        text: str | None = None,
        headers: dict[str, str] | None = None,
        url: str | None = None,
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data
        self._text = (
            text if text is not None else (json.dumps(json_data) if json_data is not None else "")
        )
        self.headers = headers or {
            "Content-Type": "application/json" if json_data is not None else "text/plain"
        }
        self.url = url or "https://app.lumerahq.com/api/pb/test"

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> dict:
        if self._json_data is None:
            raise ValueError("no json payload")
        return self._json_data

    @property
    def text(self) -> str:
        return self._text

    def raise_for_status(self) -> None:
        if not self.ok:
            raise requests.HTTPError(response=self)


def test_resolve_path_with_string() -> None:
    p = "/lumera-files/example/data.csv"
    assert resolve_path(p) == p


def test_resolve_path_with_fileref_path() -> None:
    fr: FileRef = {"path": "/lumera-files/sessions/abc/file.txt"}
    assert resolve_path(fr) == "/lumera-files/sessions/abc/file.txt"


def test_resolve_path_with_fileref_run_path() -> None:
    fr: FileRef = {"run_path": "/lumera-files/agent_runs/run1/out.json"}
    assert resolve_path(fr) == "/lumera-files/agent_runs/run1/out.json"


def test_to_filerefs_from_strings() -> None:
    values = [
        "/lumera-files/scopeX/123/a.txt",
        "/lumera-files/scopeX/123/b.txt",
    ]
    out = to_filerefs(values, scope="scopeX", id="123")
    assert len(out) == 2
    assert out[0]["name"] == "a.txt"
    assert out[0]["path"].endswith("/a.txt")
    assert out[0]["object_name"] == "scopeX/123/a.txt"


def test_to_filerefs_from_dicts_merge_defaults() -> None:
    values: list[FileRef] = [
        {"path": "/lumera-files/scopeY/999/c.txt"},
        {"run_path": "/lumera-files/agent_runs/run2/d.txt", "name": "d.txt"},
    ]
    out = to_filerefs(values, scope="scopeY", id="999")
    assert len(out) == 2
    # path-backed
    assert out[0]["name"] == "c.txt"
    assert out[0]["object_name"] == "scopeY/999/c.txt"
    # run_path-backed
    assert out[1]["name"] == "d.txt"
    assert out[1]["path"].endswith("/d.txt")
    assert out[1]["object_name"] == "scopeY/999/d.txt"


def test_list_collections_uses_token_and_returns_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    recorded: dict[str, object] = {}

    def fake_request(_method: str, _url: str, **kwargs: object) -> DummyResponse:
        recorded["method"] = _method
        recorded["url"] = _url
        recorded["headers"] = kwargs.get("headers")
        return DummyResponse(json_data={"items": [{"id": "col"}]})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    resp = list_collections()
    assert resp["items"][0]["id"] == "col"
    assert recorded["method"] == "GET"
    assert str(recorded["url"]).endswith("/pb/collections")
    headers = recorded["headers"]
    assert isinstance(headers, dict)
    assert headers["Authorization"] == "token tok"


def test_create_collection_posts_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    captured: dict[str, object] = {}

    def fake_request(_method: str, _url: str, **kwargs: object) -> DummyResponse:
        captured["json"] = kwargs.get("json")
        return DummyResponse(status_code=201, json_data={"id": "new"})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    resp = create_collection(
        "example", schema=[{"name": "field", "type": "text"}], indexes=["CREATE INDEX"]
    )

    assert resp["id"] == "new"
    payload = captured["json"]
    assert isinstance(payload, dict)
    assert payload["name"] == "example"
    assert payload["schema"][0]["name"] == "field"
    assert payload["indexes"] == ["CREATE INDEX"]


def test_create_record_sends_json_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    captured: dict[str, object] = {}

    def fake_request(_method: str, _url: str, **kwargs: object) -> DummyResponse:
        captured["json"] = kwargs.get("json")
        return DummyResponse(status_code=201, json_data={"id": "rec"})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    resp = create_record("example", {"name": "value"})
    assert resp["id"] == "rec"
    payload = captured["json"]
    assert isinstance(payload, dict)
    assert payload == {"name": "value"}


def test_update_record_with_files_uses_json_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    captured: dict[str, object] = {}

    def fake_request(_method: str, _url: str, **kwargs: object) -> DummyResponse:
        captured["data"] = kwargs.get("data")
        captured["files"] = kwargs.get("files")
        return DummyResponse(json_data={"id": "rec"})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    file_obj = object()
    resp = update_record("example", "rec", {"name": "value"}, files={"file": file_obj})
    assert resp["id"] == "rec"
    data = captured["data"]
    assert isinstance(data, dict)
    assert json.loads(data["@jsonPayload"]) == {"name": "value"}
    files = captured["files"]
    assert isinstance(files, dict)
    assert files["file"] is file_obj


def test_get_collection_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    def fake_request(_method: str, _url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(status_code=404, json_data={"error": "not found"}, url=_url)

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    with pytest.raises(LumeraAPIError) as exc:
        get_collection("missing")

    assert exc.value.status_code == 404
    assert "missing" in exc.value.url


def test_create_record_unique_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    def fake_request(_method: str, _url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(
            status_code=400,
            json_data={"external_id": "Value must be unique"},
            url="https://app.lumerahq.com/api/pb/collections/example/records",
        )

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    with pytest.raises(RecordNotUniqueError):
        create_record("example", {"external_id": "dup"})


def test_get_record_by_external_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    captured: dict[str, object] = {}

    def fake_request(method: str, url: str, **kwargs: object) -> DummyResponse:
        captured["method"] = method
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return DummyResponse(json_data={"items": [{"id": "rec"}]})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    record = get_record_by_external_id("example", "ext value")
    assert record["id"] == "rec"
    assert captured["method"] == "GET"
    assert str(captured["url"]).endswith("/pb/collections/example/records")
    params = captured["params"]
    assert isinstance(params, dict)
    assert json.loads(params["filter"]) == {"external_id": "ext value"}


def test_get_record_by_external_id_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(sdk.TOKEN_ENV, "tok")

    def fake_request(_method: str, _url: str, **_kwargs: object) -> DummyResponse:
        return DummyResponse(json_data={"items": []})

    monkeypatch.setattr(sdk.requests, "request", fake_request)

    with pytest.raises(LumeraAPIError) as exc:
        get_record_by_external_id("example", "missing")

    assert exc.value.status_code == 404
