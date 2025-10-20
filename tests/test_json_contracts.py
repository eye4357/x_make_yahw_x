from __future__ import annotations

import json
from pathlib import Path

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
    with (FIXTURE_DIR / "input.json").open("r", encoding="utf-8") as handle:
        input_payload = json.load(handle)
    with (FIXTURE_DIR / "output.json").open("r", encoding="utf-8") as handle:
        output_payload = json.load(handle)
    with (FIXTURE_DIR / "error.json").open("r", encoding="utf-8") as handle:
        error_payload = json.load(handle)

    validate_payload(input_payload, INPUT_SCHEMA)
    validate_payload(output_payload, OUTPUT_SCHEMA)
    validate_payload(error_payload, ERROR_SCHEMA)
