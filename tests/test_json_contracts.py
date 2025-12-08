from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from x_make_common_x.json_contracts import validate_payload, validate_schema

from x_make_yahw_x.json_contracts import (
    ERROR_SCHEMA,
    INPUT_SCHEMA,
    OUTPUT_SCHEMA,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "json_contracts"


def test_schemas_are_valid() -> None:
    for schema in (INPUT_SCHEMA, OUTPUT_SCHEMA, ERROR_SCHEMA):
        validate_schema(schema)


def test_sample_payloads_match_schema() -> None:
    input_payload = _load_fixture("input")
    output_payload = _load_fixture("output")
    error_payload = _load_fixture("error")

    validate_payload(input_payload, INPUT_SCHEMA)
    validate_payload(output_payload, OUTPUT_SCHEMA)
    validate_payload(error_payload, ERROR_SCHEMA)


def _load_fixture(name: str) -> dict[str, object]:
    path = FIXTURE_DIR / f"{name}.json"
    with path.open("r", encoding="utf-8") as handle:
        payload_obj: object = json.load(handle)
    if not isinstance(payload_obj, dict):
        message = f"Fixture payload must be an object: {name}"
        raise TypeError(message)
    typed_payload = cast("dict[str, object]", payload_obj)
    return dict(typed_payload)
