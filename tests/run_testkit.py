#!/usr/bin/env python3
"""Compile and run the checked-in testkit smoke fixture with Bootstrap."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "testkit_smoke.basalt"
OUT = ROOT / ".tmp" / "testkit-smoke"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default=os.environ.get("BASALT_COMPILER"), help="path to basaltc Bootstrap binary")
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"), help="C compiler for generated output")
    args = parser.parse_args()
    if not args.compiler:
        parser.error("--compiler or BASALT_COMPILER is required")
    compiler = Path(args.compiler).resolve()
    if not compiler.is_file():
        parser.error(f"Bootstrap compiler does not exist: {compiler}")

    OUT.mkdir(parents=True, exist_ok=True)
    generated_c = OUT / "testkit_smoke.c"
    binary = OUT / "testkit_smoke.bin"
    subprocess.run([str(compiler), "--no-line", str(FIXTURE), str(generated_c)], check=True)
    subprocess.run(
        [
            args.cc,
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Wconversion",
            "-Wshadow",
            "-Werror",
            str(generated_c),
            "-o",
            str(binary),
        ],
        check=True,
    )
    completed = subprocess.run([str(binary)], check=False)
    if completed.returncode == 0:
        print("testkit smoke: PASS")
    else:
        print(f"testkit smoke: FAIL (exit {completed.returncode})")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
