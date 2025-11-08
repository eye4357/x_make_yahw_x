from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections.abc import Mapping, Sequence
from contextlib import suppress
from pathlib import Path
from types import SimpleNamespace
from typing import IO, Protocol, cast

from x_make_common_x.json_contracts import validate_payload
from x_make_yahw_x.json_contracts import ERROR_SCHEMA, INPUT_SCHEMA, OUTPUT_SCHEMA


class _SchemaValidationError(Exception):
    message: str
    path: tuple[object, ...]
    schema_path: tuple[object, ...]


class _JsonSchemaModule(Protocol):
    ValidationError: type[_SchemaValidationError]


def _load_validation_error() -> type[_SchemaValidationError]:
    module = cast("_JsonSchemaModule", importlib.import_module("jsonschema"))
    return module.ValidationError


ValidationErrorType: type[_SchemaValidationError] = _load_validation_error()


class XClsMakeYahwX:
    def __init__(self, ctx: object | None = None) -> None:
        # store optional orchestrator context for backward-compatible upgrades
        self._ctx = ctx

    def run(self) -> str:
        return "Hello world!"


def main() -> str:
    return XClsMakeYahwX().run()


SCHEMA_VERSION = "x_make_yahw_x.run/1.0"


def _failure_payload(
    message: str, *, details: Mapping[str, object] | None = None
) -> dict[str, object]:
    payload: dict[str, object] = {"status": "failure", "message": message}
    if details:
        payload["details"] = dict(details)
    with suppress(ValidationErrorType):
        validate_payload(payload, ERROR_SCHEMA)
    return payload


def _build_context(
    ctx: object | None, overrides: Mapping[str, object] | None
) -> object | None:
    if not overrides:
        return ctx
    namespace = SimpleNamespace(**{str(key): value for key, value in overrides.items()})
    if ctx is not None:
        namespace.parent_ctx = ctx
    return namespace


def main_json(
    payload: Mapping[str, object], *, ctx: object | None = None
) -> dict[str, object]:
    try:
        validate_payload(payload, INPUT_SCHEMA)
    except ValidationErrorType as exc:
        return _failure_payload(
            "input payload failed validation",
            details={
                "error": exc.message,
                "path": [str(part) for part in exc.path],
                "schema_path": [str(part) for part in exc.schema_path],
            },
        )

    parameters_obj = payload.get("parameters", {})
    parameters = cast("Mapping[str, object]", parameters_obj)
    context_obj = parameters.get("context")
    context_mapping = cast(
        "Mapping[str, object] | None",
        context_obj if isinstance(context_obj, Mapping) else None,
    )

    runtime_ctx = _build_context(ctx, context_mapping)

    try:
        runner = XClsMakeYahwX(ctx=runtime_ctx)
        message = runner.run()
    except Exception as exc:  # noqa: BLE001
        return _failure_payload(
            "yahw execution failed",
            details={"error": str(exc)},
        )

    if not isinstance(message, str) or not message.strip():
        return _failure_payload(
            "yahw returned an empty message",
            details={"result": message},
        )

    metadata: dict[str, object] = {}
    if context_mapping:
        context_keys = tuple(sorted(str(key) for key in context_mapping))
        metadata["context_keys"] = list(context_keys)
        metadata["context_entries"] = len(context_keys)
    if runtime_ctx is not ctx and runtime_ctx is not None and ctx is not None:
        metadata["parent_ctx_attached"] = True

    result_payload: dict[str, object] = {
        "status": "success",
        "schema_version": SCHEMA_VERSION,
        "message": message,
    }
    if metadata:
        result_payload["metadata"] = metadata

    try:
        validate_payload(result_payload, OUTPUT_SCHEMA)
    except ValidationErrorType as exc:
        return _failure_payload(
            "generated output failed schema validation",
            details={
                "error": exc.message,
                "path": [str(part) for part in exc.path],
                "schema_path": [str(part) for part in exc.schema_path],
            },
        )

    return result_payload


def _load_json_payload(file_path: str | None) -> Mapping[str, object]:
    def _load(handle: IO[str]) -> Mapping[str, object]:
        payload_obj: object = json.load(handle)
        if not isinstance(payload_obj, dict):
            message = "JSON payload must be an object"
            raise TypeError(message)
        return cast("dict[str, object]", payload_obj)

    if file_path:
        with Path(file_path).open("r", encoding="utf-8") as handle:
            return _load(handle)
    return _load(sys.stdin)


def _run_json_cli(args: Sequence[str]) -> None:
    parser = argparse.ArgumentParser(description="x_make_yahw_x JSON runner")
    parser.add_argument(
        "--json", action="store_true", help="Read JSON payload from stdin"
    )
    parser.add_argument("--json-file", type=str, help="Path to JSON payload file")
    parsed = parser.parse_args(args)
    json_flag_obj = cast("object", getattr(parsed, "json", False))
    json_flag = bool(json_flag_obj)
    json_file_obj = cast("object", getattr(parsed, "json_file", None))
    json_file = json_file_obj if isinstance(json_file_obj, str) else None

    if not (json_flag or json_file):
        parser.error("JSON input required. Use --json for stdin or --json-file <path>.")

    payload = _load_json_payload(json_file if json_file else None)
    result = main_json(payload)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


x_cls_make_yahw_x = XClsMakeYahwX

__all__ = ["XClsMakeYahwX", "main", "main_json", "x_cls_make_yahw_x"]


if __name__ == "__main__":
    _run_json_cli(sys.argv[1:])
