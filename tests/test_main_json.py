from __future__ import annotations

import importlib
from collections.abc import Mapping
from types import SimpleNamespace
from typing import NoReturn, cast

import pytest
from x_make_common_x.json_contracts import validate_payload

from x_make_yahw_x.json_contracts import ERROR_SCHEMA, OUTPUT_SCHEMA
from x_make_yahw_x.x_cls_make_yahw_x import XClsMakeYahwX, main_json

yahw_module = importlib.import_module("x_make_yahw_x.x_cls_make_yahw_x")

EXPECTED_CONTEXT_ENTRIES = 2
EXPECTED_ATTEMPT_VALUE = 3
EXPECTED_CONTEXT_KEYS = ["attempt", "invoked_by"]


def _raise_failure(message: str) -> NoReturn:
    failure_message = message
    raise AssertionError(failure_message)


def expect(*, condition: bool, message: str) -> None:
    if not condition:
        _raise_failure(message)


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

    expect(
        condition=result["message"] == "Hello integration!",
        message="Unexpected success message",
    )
    metadata = cast("Mapping[str, object]", result.get("metadata", {}))
    expect(condition=bool(metadata), message="Metadata should be populated")
    expect(
        condition=metadata.get("context_entries") == EXPECTED_CONTEXT_ENTRIES,
        message="Context entry count mismatch",
    )
    expect(
        condition=metadata.get("context_keys") == EXPECTED_CONTEXT_KEYS,
        message="Context keys mismatch",
    )
    ctx_obj = captured_context["ctx"]
    if not isinstance(ctx_obj, SimpleNamespace):
        _raise_failure("Expected SimpleNamespace context")
    namespace_ctx = cast("SimpleNamespace", ctx_obj)
    expect(
        condition=namespace_ctx.invoked_by == "json-test",
        message="Incorrect invoked_by value",
    )
    expect(
        condition=namespace_ctx.attempt == EXPECTED_ATTEMPT_VALUE,
        message="Incorrect attempt value",
    )


def test_main_json_handles_runner_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingRunner(XClsMakeYahwX):
        def run(self) -> str:
            message = "boom"
            raise RuntimeError(message)

    monkeypatch.setattr(yahw_module, "XClsMakeYahwX", FailingRunner)

    payload = {"command": "x_make_yahw_x"}
    result = main_json(payload)

    validate_payload(result, ERROR_SCHEMA)
    expect(
        condition=result.get("status") == "failure",
        message="Runner failure should surface",
    )
    details = cast("Mapping[str, object] | None", result.get("details"))
    expect(
        condition=details is not None, message="Failure payload must include details"
    )
    error_text = str(details.get("error")) if details is not None else ""
    expect(condition="boom" in error_text, message="Expected error message in details")


def test_main_json_rejects_invalid_payload() -> None:
    result = main_json({})
    validate_payload(result, ERROR_SCHEMA)
    expect(
        condition=result.get("status") == "failure",
        message="Invalid payload should fail",
    )
