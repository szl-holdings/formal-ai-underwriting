#!/usr/bin/env python3
"""CI packaging check: the built wheel must ship the `certification` package and nothing from tests/.

Usage: python .github/scripts/check_wheel.py [DIST_DIR]

Exits non-zero when DIST_DIR does not hold exactly one formal_ai_underwriting wheel, when that wheel is
missing an executable package file, or when it contains files from tests/. (Until 2026-11-06 the wheel was
built with `packages = []` and shipped no code at all.)

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REQUIRED = (
    "certification/__init__.py",
    "certification/bounds.py",
    "payments/__init__.py",
    "payments/paycheck.py",
)


def check(dist_dir: Path) -> list[str]:
    wheels = sorted(dist_dir.glob("formal_ai_underwriting-*.whl"))
    if len(wheels) != 1:
        return [f"expected exactly one formal_ai_underwriting wheel in {dist_dir}, found {[w.name for w in wheels]}"]
    with zipfile.ZipFile(wheels[0]) as whl:
        names = set(whl.namelist())
    problems = [f"{wheels[0].name} is missing {name}" for name in REQUIRED if name not in names]
    problems += [f"{wheels[0].name} ships test file {name}" for name in sorted(names) if name.startswith("tests/")]
    return problems


def main(argv: list[str]) -> int:
    dist_dir = Path(argv[1]) if len(argv) > 1 else Path("dist")
    problems = check(dist_dir)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1
    print(f"wheel OK: ships {', '.join(REQUIRED)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
