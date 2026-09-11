#!/usr/bin/env python3
"""Check the vendored device library is a faithful, importable copy.

HACS installs a custom integration by copying files, so the
``lg-heatpump-modbus`` device library is vendored into the integration rather
than installed from PyPI. A vendored tree rots silently: this script fails the
build if the copy has been hand-edited or has drifted from the library.

Run it from the repository root::

    python3 scripts/check_vendored.py

When the library checkout is not next to this repository, only the local checks
run. Point ``LIBRARY_SOURCE`` at its ``src/lg_heatpump_modbus`` directory to
compare the trees as well.
"""

from __future__ import annotations

import filecmp
import importlib.util
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VENDORED = ROOT / "custom_components" / "lg_heatpump" / "lg_heatpump_modbus"
DEFAULT_SOURCE = ROOT.parent / "lg-heatpump-modbus" / "src" / "lg_heatpump_modbus"

IGNORED = {"__pycache__", "VENDORED"}


def fail(message: str) -> None:
    """Print an error and exit non-zero."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_present() -> None:
    """Check the vendored tree exists and carries its provenance marker."""
    if not VENDORED.is_dir():
        fail(f"vendored library missing at {VENDORED.relative_to(ROOT)}")
    if not (VENDORED / "VENDORED").is_file():
        fail("vendored library has no VENDORED marker; re-run scripts/vendor")
    if not (VENDORED / "py.typed").is_file():
        fail("vendored library lost its py.typed marker")
    print(f"ok: {(VENDORED / 'VENDORED').read_text().splitlines()[0]}")


def check_importable() -> None:
    """Check the vendored tree imports and exposes its public API."""
    # Load the copy from its path rather than by adding a directory to
    # sys.path. The integration package holds platform modules named after
    # stdlib modules (select.py), so putting it on sys.path would shadow them.
    spec = importlib.util.spec_from_file_location(
        "lg_heatpump_modbus",
        VENDORED / "__init__.py",
        submodule_search_locations=[str(VENDORED)],
    )
    if spec is None or spec.loader is None:  # pragma: no cover - a broken copy
        fail("vendored library has no importable __init__.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except ImportError as error:  # pragma: no cover - a broken copy
        fail(f"vendored library does not import: {error}")
    for name in ("LgHeatPump", "MODELS", "SETTING_COMPONENTS", "UpdateReport"):
        if not hasattr(module, name):
            fail(f"vendored library does not export {name}")
    print(f"ok: vendored library exports {len(module.__all__)} names")


def _differences(comparison: filecmp.dircmp) -> list[str]:
    """Return every path where the two trees disagree."""
    found = [
        *(f"only in the library: {name}" for name in comparison.left_only),
        *(f"only in the copy: {name}" for name in comparison.right_only),
        *(f"edited in the copy: {name}" for name in comparison.diff_files),
    ]
    for sub in comparison.subdirs.values():
        found.extend(_differences(sub))
    return [line for line in found if not any(part in line for part in IGNORED)]


def check_matches_source() -> None:
    """Compare the copy against the library checkout, when one is available."""
    source = Path(os.environ.get("LIBRARY_SOURCE", DEFAULT_SOURCE))
    if not source.is_dir():
        print(f"skip: no library checkout at {source}; tree comparison skipped")
        return
    comparison = filecmp.dircmp(source, VENDORED, ignore=list(IGNORED))
    if differences := _differences(comparison):
        for line in differences:
            print(f"  {line}", file=sys.stderr)
        fail("vendored library has drifted; re-run scripts/vendor")
    print(f"ok: vendored library matches {source}")


def main() -> int:
    """Run every check."""
    check_present()
    check_importable()
    check_matches_source()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
