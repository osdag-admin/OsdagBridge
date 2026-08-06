"""Smoke test: every module in the package must be importable.

This is a regression guard for a specific failure mode. `osdagbridge.core`
previously executed `from .models import *` against a module that does not
exist, so importing the core package — or anything beneath it — raised
ModuleNotFoundError. The test suite still reported green, because every test
was a placeholder that imported nothing.

A missing *first-party* module is exactly that bug and must fail loudly. A
missing *third-party* optional dependency (PySide6 for the desktop UI,
openseespy for the solver adapter) is a legitimate absence in a minimal
install, so those are skipped rather than failed.
"""

import importlib
import pkgutil

import pytest

import osdagbridge


def _all_module_names() -> list[str]:
    """Every module and subpackage under `osdagbridge`, discovered at runtime.

    Discovery is used rather than a hand-written list so that modules added
    later are covered automatically. `onerror` swallows failures during the
    walk itself; the parametrised test below is what reports them.
    """
    names = {osdagbridge.__name__}
    for info in pkgutil.walk_packages(
        osdagbridge.__path__, prefix=f"{osdagbridge.__name__}.", onerror=lambda _name: None
    ):
        names.add(info.name)
    return sorted(names)


@pytest.mark.parametrize("module_name", _all_module_names())
def test_module_is_importable(module_name: str) -> None:
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        if missing.startswith("osdagbridge"):
            raise  # a first-party module is missing — the bug this test guards against
        pytest.skip(f"optional third-party dependency not installed: {missing}")
