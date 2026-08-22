# testkit 0.1.0

`testkit` is a tiny, dependency-free assertion and reporting library for Basalt. It is designed for small package fixtures and follows the useful parts of a pytest workflow: tests have readable names, each case emits a `PASSED` or `FAILED` line, the runner aggregates failures, and the process returns a non-zero status when any assertion fails.

The library has no global state, hidden allocation service, C header, or runtime dependency. Assertions return `1` for success and `0` for failure. `testkit::run` converts an assertion result into a named test report and returns `0` or `1`, while `testkit::summary` prints the final count and returns the number of failed tests.

## Import

Basalt supports short, explicit prefixes for source imports. Prefixes are anchored at the project root, meaning the directory from which the compiler is invoked:

```basalt
include "@stdlib/string.basalt"
include "@lib/testkit/0.1.0/src/testkit.basalt"
```

`@stdlib/` resolves to `src/stdlib/` and `@lib/` resolves to `.basalt/vendor/`. The second form is available after the package manager has fetched and verified the library. The version remains explicit, so resolution never silently selects a different release. The older relative include form remains valid for compatibility:

```basalt
include "packages/testkit/0.1.0/src/testkit.basalt"
```

The registry package manager records this boundary explicitly; it does not rewrite source files or inject an implicit include path.

## Assertion API

| Function | Contract |
|---|---|
| `testkit::assert_true(actual)` | Passes when a boolean expression is `true`. |
| `testkit::assert_int(actual, expected)` | Passes when two `int` values are equal. |
| `testkit::assert_bool(actual, expected)` | Passes when two `bool` values are equal. |
| `testkit::assert_char(actual, expected)` | Passes when two `char` values are equal. |
| `testkit::assert_string(actual, expected)` | Performs byte-oriented NUL-terminated string equality. |
| `testkit::assert_between(value, minimum, maximum)` | Passes for an inclusive integer range. |
| `testkit::assert_not_int(actual, unexpected)` | Passes when two `int` values differ. |
| `testkit::assert_f64_close(actual, expected, tolerance)` | Passes when the absolute difference is within `tolerance`. |

The original `check_*` helpers remain as compatibility aliases for existing consumers.

## Reporting API

| Function | Contract |
|---|---|
| `testkit::run(name, passed)` | Prints `<name> PASSED` or `<name> FAILED`; returns `0` or `1`. |
| `testkit::summary(total, failures)` | Prints a compact final summary and returns `failures`. |

## Minimal pytest-like test

```basalt
include "packages/testkit/0.1.0/src/testkit.basalt"

func main(): int {
  let total: int = 0;
  let failures: int = 0;
  total += 1;
  failures += testkit::run("test_addition", testkit::assert_int(2 + 2, 4));
  total += 1;
  failures += testkit::run("test_contract", testkit::assert_true(7 >= 1));
  return testkit::summary(total, failures);
}
```

The repository smoke fixture contains nine named cases, including a floating-point tolerance check and two assertions that verify mismatches are correctly rejected. Run it with the repository runner:

```text
python3 tests/run_testkit.py --compiler /path/to/basaltc
```

A successful run exits with status `0`; any failed case produces a non-zero status suitable for CI.

## High-volume stress fixture

The package also includes `tests/testkit_stress.basalt`, which executes 35,000 assertions across integer equality, inclusive ranges, booleans, characters, floating-point tolerance and byte-oriented strings. It emits six named group results instead of one line per assertion, keeping the test readable while exercising the hot assertion paths:

```text
python3 tests/run_testkit_stress.py --compiler /path/to/basaltc --runs 5
```

The runner compiles with strict C11 warnings, executes the binary repeatedly, checks every expected result line and writes timing data to `.tmp/testkit-stress/benchmark.json`.
