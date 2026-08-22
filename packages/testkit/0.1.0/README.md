# testkit 0.1.0

`testkit` is a tiny dependency-free assertion library for Basalt examples and package-manager fixtures. The helpers deliberately return `1` for success and `0` for failure, so a test can aggregate failures and return a conventional process status without hidden I/O or global state.

## Import

Until native package imports are enabled in the compiler, include the package entry explicitly from a workspace or a vendored path:

```basalt
include "packages/testkit/0.1.0/src/testkit.basalt"
```

The registry package manager records this boundary explicitly; it does not rewrite source files or inject an implicit include path.

## API

| Function | Contract |
|---|---|
| `testkit::check_int(actual, expected)` | Returns `1` when two `int` values are equal. |
| `testkit::check_bool(actual, expected)` | Returns `1` when two `bool` values are equal. |
| `testkit::check_char(actual, expected)` | Returns `1` when two `char` values are equal. |
| `testkit::check_string(actual, expected)` | Performs a byte-oriented NUL-terminated string equality check and returns `1` on equality. |
| `testkit::check_between(value, minimum, maximum)` | Returns `1` when `value` is within the inclusive integer range. |
| `testkit::check_not_int(actual, unexpected)` | Returns `1` when the integer values differ. |

## Minimal test

```basalt
include "packages/testkit/0.1.0/src/testkit.basalt"

func main(): int {
  let failures: int = 0;
  if testkit::check_int(2 + 2, 4) == 0 then failures += 1;
  if testkit::check_string("ok", "ok") == 0 then failures += 1;
  return failures;
}
```

No allocation, external C header, or runtime service is required by the library itself.
