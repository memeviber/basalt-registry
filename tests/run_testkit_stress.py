"""Compile and benchmark the testkit high-volume assertion fixture."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "testkit_stress.basalt"
OUT = ROOT / ".tmp" / "testkit-stress"
STRICT_FLAGS = [
    "-std=c11",
    "-Wall",
    "-Wextra",
    "-Wpedantic",
    "-Wconversion",
    "-Wshadow",
    "-Werror",
]
EXPECTED_LINES = [
    "test_10000_int_assertions PASSED",
    "test_5000_range_assertions PASSED",
    "test_5000_bool_assertions PASSED",
    "test_5000_char_assertions PASSED",
    "test_5000_float_assertions PASSED",
    "test_5000_string_assertions PASSED",
    "assertions:35000",
    "total:6",
    "failed:0",
    "RESULT: PASS",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default=os.environ.get("BASALT_COMPILER"), required=False)
    parser.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    if not args.compiler:
        parser.error("--compiler or BASALT_COMPILER is required")
    if args.runs < 1 or args.runs > 100:
        parser.error("--runs must be between 1 and 100")

    compiler = Path(args.compiler).resolve()
    if not compiler.is_file():
        parser.error(f"Bootstrap compiler does not exist: {compiler}")

    OUT.mkdir(parents=True, exist_ok=True)
    generated_c = OUT / "testkit_stress.c"
    binary = OUT / "testkit_stress.bin"
    report_path = OUT / "benchmark.json"

    subprocess.run([str(compiler), "--no-line", str(FIXTURE), str(generated_c)], check=True)
    subprocess.run([args.cc, *STRICT_FLAGS, str(generated_c), "-o", str(binary)], check=True)

    durations_ms: list[float] = []
    output = ""
    for _ in range(args.runs):
        started = time.perf_counter_ns()
        completed = subprocess.run([str(binary)], check=False, capture_output=True, text=True)
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
        durations_ms.append(elapsed_ms)
        output = completed.stdout
        if completed.returncode != 0:
            raise SystemExit(f"testkit stress failed with exit {completed.returncode}: {completed.stderr}")
        missing = [line for line in EXPECTED_LINES if line not in output]
        if missing:
            raise SystemExit(f"testkit stress output missing lines: {missing}")

    result = {
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "assertions": 35000,
        "iterations": args.runs,
        "compiler": str(compiler),
        "cc": args.cc,
        "strict_flags": STRICT_FLAGS,
        "runtime_ms": {
            "min": min(durations_ms),
            "mean": sum(durations_ms) / len(durations_ms),
            "max": max(durations_ms),
        },
        "output": output,
        "status": "PASS",
    }
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"testkit stress: PASS ({result['assertions']} assertions, "
        f"{args.runs} runs, min={result['runtime_ms']['min']:.3f}ms, "
        f"mean={result['runtime_ms']['mean']:.3f}ms, max={result['runtime_ms']['max']:.3f}ms)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
