# Basalt Registry

A small, static, GitHub Pages-backed registry for Basalt source packages. The registry is intentionally simple: package metadata is JSON, archives are deterministic `.tar.gz` files, and package contents remain inspectable under `packages/`.

## Published package

| Package | Version | Description |
|---|---:|---|
| [`testkit`](packages/testkit/0.1.0/) | `0.1.0` | Dependency-free assertion helpers for Basalt examples and package tests. |

The machine-readable registry entry is [`registry.json`](registry.json), and the package index consumed by the Basalt package manager is [`index/testkit.json`](index/testkit.json). The archive is [`archives/testkit-0.1.0.tar.gz`](archives/testkit-0.1.0.tar.gz).

## Use the package manager

The compiler currently has no implicit package-import search path. Use the repository as a static registry and let the package manager verify the archive:

```sh
python3 scripts/basalt_pkg.py \
  --root /path/to/project \
  --registry https://memeviber.github.io/basalt-registry \
  fetch
```

The package-manager implementation lives in the Basalt compiler repository. It resolves `testkit` from `index/testkit.json`, verifies the SHA-256 checksum, and materializes the package under `.basalt/vendor/testkit/0.1.0/`.

## Local smoke test

The checked-in fixture [`tests/testkit_smoke.basalt`](tests/testkit_smoke.basalt) exercises integer, boolean, character, string, inclusive-range, and inequality assertions. It can be compiled with the Bootstrap compiler:

```sh
BASALT_COMPILER=/path/to/bootstrap.bin python3 tests/run_testkit.py
```

The runner writes all generated C and binaries under `.tmp/`, uses strict C11 warnings, and returns the fixture's process status.

## Registry contract

Archives are source-only inputs. The registry does not execute package-provided scripts, inject compiler flags, or claim native package imports that the current Bootstrap compiler does not yet implement. Every published package has a manifest, a deterministic archive, a checksum, and browsable source.

GitHub Pages is configured to publish the `main` branch from the repository root. The public site is available at <https://memeviber.github.io/basalt-registry/>.
