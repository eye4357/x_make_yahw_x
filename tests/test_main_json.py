from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

import pytest
from x_make_common_x.json_contracts import validate_payload

from x_make_yahw_x.json_contracts import ERROR_SCHEMA, OUTPUT_SCHEMA
from x_make_yahw_x.x_cls_make_yahw_x import XClsMakeYahwX, main_json

yahw_module = importlib.import_module("x_make_yahw_x.x_cls_make_yahw_x")


def test_main_json_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_context: dict[str, object] = {}

    class FakeRunner(XClsMakeYahwX):
        def __init__(self, ctx: object | None = None) -> None:
            super().__init__(ctx)
            captured_context["ctx"] = ctx

        def run(self) -> str:  # pragma: no cover - simple override
            return "Hello integration!"

    monkeypatch.setattr(yahw_module, "XClsMakeYahwX", FakeRunner)

    payload = {
        "command": "x_make_yahw_x",
        "parameters": {
            "context": {
                "invoked_by": "json-test",
                "attempt": 3,
            }
        },
    }

    result = main_json(payload)
    validate_payload(result, OUTPUT_SCHEMA)

    assert result["message"] == "Hello integration!"
    metadata = cast("Mapping[str, object]", result.get("metadata", {}))
    assert metadata
    assert metadata.get("context_entries") == 2
    assert metadata.get("context_keys") == ["attempt", "invoked_by"]
    ctx_obj = captured_context["ctx"]
    assert isinstance(ctx_obj, SimpleNamespace)
    assert ctx_obj.invoked_by == "json-test"
    assert ctx_obj.attempt == 3


def test_main_json_handles_runner_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingRunner(XClsMakeYahwX):
        def run(self) -> str:
            raise RuntimeError("boom")

    monkeypatch.setattr(yahw_module, "XClsMakeYahwX", FailingRunner)

    payload = {"command": "x_make_yahw_x"}
    result = main_json(payload)

    validate_payload(result, ERROR_SCHEMA)
    assert result["status"] == "failure"
    details = cast("Mapping[str, object] | None", result.get("details"))
    assert details is not None and "boom" in str(details.get("error"))


def test_main_json_rejects_invalid_payload() -> None:
    result = main_json({})
    validate_payload(result, ERROR_SCHEMA)
    assert result["status"] == "failure"
