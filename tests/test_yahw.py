"""Tests for the XClsMakeYahwX helper."""

from __future__ import annotations

# ruff: noqa: S101
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from x_make_yahw_x import x_cls_make_yahw_x as yahw_module
from x_make_yahw_x.x_cls_make_yahw_x import XClsMakeYahwX, main

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


def test_run_returns_greeting() -> None:
    greeter = XClsMakeYahwX()

    result = greeter.run()

    assert result == "Hello world!"


def test_main_invokes_runner(monkeypatch: MonkeyPatch) -> None:
    captured: dict[str, bool] = {}

    class FakeRunner:
        def __init__(self) -> None:
            captured["created"] = True

        def run(self) -> str:
            captured["called"] = True
            return "hi"

    monkeypatch.setattr(yahw_module, "XClsMakeYahwX", FakeRunner)

    assert main() == "hi"
    assert captured == {"created": True, "called": True}


def test_module_entrypoint_requires_json(
    capsys: CaptureFixture[str], monkeypatch: MonkeyPatch
) -> None:
    # Simulate running the module directly without JSON arguments
    module_file = getattr(yahw_module, "__file__", None)
    assert isinstance(module_file, str)
    module_path = Path(module_file).resolve()
    spec = importlib.util.spec_from_file_location(
        "__main__",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setattr(sys, "argv", [str(module_path)])

    with pytest.raises(SystemExit) as excinfo:
        spec.loader.exec_module(module)

    assert excinfo.value.code == 2
    output = capsys.readouterr()
    assert "JSON input required" in output.err
