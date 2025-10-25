"""Tests for the XClsMakeYahwX helper."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import pytest

from x_make_yahw_x.x_cls_make_yahw_x import XClsMakeYahwX, main

yahw_module = importlib.import_module("x_make_yahw_x.x_cls_make_yahw_x")

EXPECTED_USAGE_ERROR = 2


def _raise_failure(message: str) -> NoReturn:
    failure_message = message
    raise AssertionError(failure_message)


def expect(*, condition: bool, message: str) -> None:
    if not condition:
        _raise_failure(message)


if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_run_returns_greeting() -> None:
    greeter = XClsMakeYahwX()

    result = greeter.run()

    expect(condition=result == "Hello world!", message="Default greeting mismatch")


def test_main_invokes_runner(monkeypatch: MonkeyPatch) -> None:
    captured: dict[str, bool] = {}

    class FakeRunner:
        def __init__(self) -> None:
            captured["created"] = True

        def run(self) -> str:
            captured["called"] = True
            return "hi"

    monkeypatch.setattr(yahw_module, "XClsMakeYahwX", FakeRunner)

    expect(condition=main() == "hi", message="Runner result mismatch")
    expect(
        condition=captured == {"created": True, "called": True},
        message="Runner lifecycle events not captured",
    )


def test_module_entrypoint_requires_json(
    capsys: CaptureFixture[str], monkeypatch: MonkeyPatch
) -> None:
    # Simulate running the module directly without JSON arguments
    module_file = getattr(yahw_module, "__file__", None)
    if not isinstance(module_file, str):
        _raise_failure("Module __file__ must be a string")
    module_path = Path(module_file).resolve()
    spec = importlib.util.spec_from_file_location(
        "__main__",
        module_path,
    )
    if spec is None:
        _raise_failure("Expected importlib spec")
    loader = spec.loader
    if loader is None:
        _raise_failure("Expected importlib loader")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setattr(sys, "argv", [str(module_path)])

    with pytest.raises(SystemExit) as excinfo:
        loader.exec_module(module)

    expect(
        condition=excinfo.value.code == EXPECTED_USAGE_ERROR,
        message="Unexpected exit code",
    )
    output = capsys.readouterr()
    expect(
        condition="JSON input required" in output.err,
        message="Missing usage guidance for JSON input",
    )
