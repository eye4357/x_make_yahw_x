from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, NoReturn, cast

from x_make_common_x.json_contracts import validate_payload
from x_make_yahw_x.json_contracts import ERROR_SCHEMA, OUTPUT_SCHEMA
from x_make_yahw_x.x_cls_make_yahw_x import XClsMakeYahwX, main_json

yahw_module = importlib.import_module("x_make_yahw_x.x_cls_make_yahw_x")

if TYPE_CHECKING:
    from types import SimpleNamespace

    from _pytest.monkeypatch import MonkeyPatch

EXPECTED_CONTEXT_ENTRIES = 2
EXPECTED_ATTEMPT_VALUE = 3
EXPECTED_CONTEXT_KEYS = ["attempt", "invoked_by"]


def _raise_failure(message: str) -> NoReturn:
    failure_message = message
    raise AssertionError(failure_message)


def expect(*, condition: bool, message: str) -> None:
    if not condition:
        _raise_failure(message)


def _ensure_dict(value: object, *, message: str) -> dict[str, object]:
    if not isinstance(value, dict):
        _raise_failure(message)
    typed: dict[str, object] = {}
    for key, val in value.items():
        if not isinstance(key, str):
            _raise_failure(message)
        typed[key] = val
    return typed


def _ensure_str_list(value: object, *, message: str) -> list[str]:
    if not isinstance(value, list):
        _raise_failure(message)
    str_values: list[str] = []
    for entry in value:
        if not isinstance(entry, str):
            _raise_failure(message)
        str_values.append(entry)
    return str_values


def test_main_json_success(monkeypatch: MonkeyPatch) -> None:
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
    metadata = _ensure_dict(
        result.get("metadata"),
        message="Metadata should be populated",
    )
    context_entries = metadata.get("context_entries")
    if not isinstance(context_entries, int):
        _raise_failure("Context entry count mismatch")
    expect(
        condition=context_entries == EXPECTED_CONTEXT_ENTRIES,
        message="Context entry count mismatch",
    )
    context_keys = _ensure_str_list(
        metadata.get("context_keys"),
        message="Context keys mismatch",
    )
    expect(
        condition=context_keys == EXPECTED_CONTEXT_KEYS,
        message="Context keys mismatch",
    )
    ctx_obj = captured_context["ctx"]
    if type(ctx_obj).__name__ != "SimpleNamespace":
        _raise_failure("Expected SimpleNamespace context")
    namespace_ctx = cast("SimpleNamespace", ctx_obj)
    ctx_data = _ensure_dict(
        cast("dict[str, object]", vars(namespace_ctx)),
        message="Expected namespace data",
    )
    invoked_by = ctx_data.get("invoked_by")
    if not isinstance(invoked_by, str):
        _raise_failure("Incorrect invoked_by value")
    expect(
        condition=invoked_by == "json-test",
        message="Incorrect invoked_by value",
    )
    attempt = ctx_data.get("attempt")
    if not isinstance(attempt, int):
        _raise_failure("Incorrect attempt value")
    expect(
        condition=attempt == EXPECTED_ATTEMPT_VALUE,
        message="Incorrect attempt value",
    )


def test_main_json_handles_runner_error(monkeypatch: MonkeyPatch) -> None:
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
    details = _ensure_dict(
        result.get("details"), message="Failure payload must include details"
    )
    error_text = str(details.get("error"))
    expect(condition="boom" in error_text, message="Expected error message in details")


def test_main_json_rejects_invalid_payload() -> None:
    result = main_json({})
    validate_payload(result, ERROR_SCHEMA)
    expect(
        condition=result.get("status") == "failure",
        message="Invalid payload should fail",
    )
