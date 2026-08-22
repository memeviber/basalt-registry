#!/usr/bin/env python3
"""Build deterministic static registry artifacts for basalt-registry."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "testkit"
VERSION = "0.1.0"
PACKAGE_DIR = ROOT / "packages" / NAME / VERSION
ARCHIVE_DIR = ROOT / "archives"
INDEX_DIR = ROOT / "index"
ARCHIVE_PATH = ARCHIVE_DIR / f"{NAME}-{VERSION}.tar.gz"


def package_files() -> list[Path]:
    files = [
        path
        for path in PACKAGE_DIR.rglob("*")
        if path.is_file() and path.name != "index.html"
    ]
    return sorted(files, key=lambda path: path.relative_to(PACKAGE_DIR).as_posix())


def build_archive() -> str:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with ARCHIVE_PATH.open("wb") as archive_file:
        with gzip.GzipFile(fileobj=archive_file, mode="wb", compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as output:
                top = f"{NAME}-{VERSION}"
                directory = tarfile.TarInfo(top)
                directory.type = tarfile.DIRTYPE
                directory.mode = 0o755
                directory.mtime = 0
                output.addfile(directory)
                for path in package_files():
                    relative = path.relative_to(PACKAGE_DIR).as_posix()
                    info = tarfile.TarInfo(f"{top}/{relative}")
                    data = path.read_bytes()
                    info.size = len(data)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    output.addfile(info, fileobj=io.BytesIO(data))
    digest = hashlib.sha256(ARCHIVE_PATH.read_bytes()).hexdigest()
    return digest


def write_metadata(digest: str) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "name": NAME,
        "version": VERSION,
        "description": "A dependency-free assertion library for Basalt examples and package tests.",
        "archive": f"archives/{ARCHIVE_PATH.name}",
        "checksum": f"sha256:{digest}",
        "dependencies": {},
        "entry": "src/testkit.basalt",
        "source": f"packages/{NAME}/{VERSION}/",
    }
    (INDEX_DIR / f"{NAME}.json").write_text(json.dumps([record], indent=2) + "\n", encoding="utf-8")
    registry = {
        "name": "basalt-registry",
        "format": 1,
        "packages": [
            {
                "name": NAME,
                "latest": VERSION,
                "description": record["description"],
                "index": f"index/{NAME}.json",
                "archive": record["archive"],
                "checksum": record["checksum"],
            }
        ],
    }
    (ROOT / "registry.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not PACKAGE_DIR.is_dir():
        raise SystemExit(f"missing package directory: {PACKAGE_DIR}")
    digest = build_archive()
    write_metadata(digest)
    print(f"built {ARCHIVE_PATH.relative_to(ROOT)}")
    print(f"sha256:{digest}")


if __name__ == "__main__":
    main()
