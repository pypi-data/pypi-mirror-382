#!/usr/bin/env python3

"""
Utility to manage Python client version bumps.

Updates both pyproject.toml and src/spaps_client/__init__.py so the version
stays consistent. Designed to be GitHub Actions friendly by emitting outputs
that can be consumed via $GITHUB_OUTPUT.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Tuple
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)
INIT_PATTERN = re.compile(r'__version__\s*=\s*"([^"]+)"')


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Manage python client version.")
  parser.add_argument("--pyproject", required=True, help="Path to pyproject.toml")
  parser.add_argument("--init", required=True, help="Path to __init__.py containing __version__")
  parser.add_argument("--package", default="spaps", help="PyPI package name (default: spaps)")
  parser.add_argument("--bump", choices=["major", "minor", "patch", "none"], default="patch",
                      help="Version bump type (default: patch)")
  parser.add_argument("--set", dest="set_version", help="Explicit version override")
  parser.add_argument("--dry-run", action="store_true", help="Do not write any files")
  parser.add_argument("--fail-if-not-greater", action="store_true",
                      help="Exit with non-zero status if the computed version is not greater than the published version.")
  parser.add_argument("--github-output", dest="github_output",
                      help="Path to GitHub output file for setting workflow outputs")
  return parser.parse_args()


def read_version(path: Path, pattern: re.Pattern) -> Tuple[str, str]:
  text = path.read_text(encoding="utf-8")
  match = pattern.search(text)
  if not match:
    raise ValueError(f"Could not locate version string in {path}")
  return match.group(1).strip(), text


def bump_version(version: str, bump: str) -> str:
  major, minor, patch = _parse_semver(version)
  if bump == "major":
    major += 1
    minor = 0
    patch = 0
  elif bump == "minor":
    minor += 1
    patch = 0
  elif bump == "patch":
    patch += 1
  return f"{major}.{minor}.{patch}"


def _parse_semver(version: str) -> Tuple[int, int, int]:
  parts = version.strip().split(".")
  if len(parts) != 3 or not all(part.isdigit() for part in parts):
    raise ValueError(f"Unsupported version format '{version}'. Expected MAJOR.MINOR.PATCH.")
  return tuple(int(part) for part in parts)  # type: ignore[return-value]


def fetch_published_version(package: str) -> str:
  url = f"https://pypi.org/pypi/{package}/json"
  try:
    with urlopen(url, timeout=10) as response:
      data = json.load(response)
      return data["info"]["version"]
  except (HTTPError, URLError, TimeoutError, KeyError, json.JSONDecodeError):
    return "0.0.0"


def ensure_greater(new_version: str, published_version: str) -> None:
  try:
    new_tuple = _parse_semver(new_version)
    published_tuple = _parse_semver(published_version)
  except ValueError as exc:
    raise SystemExit(f"Invalid semantic version found: {exc}") from exc

  if new_tuple <= published_tuple:
    raise SystemExit(
      f"New version {new_version} must be greater than published {published_version}"
    )


def write_pyproject(path: Path, text: str, new_version: str) -> None:
  updated = VERSION_PATTERN.sub(f'version = "{new_version}"', text, count=1)
  path.write_text(updated, encoding="utf-8")


def write_init(path: Path, text: str, new_version: str) -> None:
  updated = INIT_PATTERN.sub(f'__version__ = "{new_version}"', text, count=1)
  path.write_text(updated, encoding="utf-8")


def emit_outputs(args: argparse.Namespace, outputs: dict) -> None:
  if args.github_output:
    with open(args.github_output, "a", encoding="utf-8") as fh:
      for key, value in outputs.items():
        fh.write(f"{key}={value}\n")


def main() -> int:
  args = parse_args()
  pyproject_path = Path(args.pyproject)
  init_path = Path(args.init)

  current_version, pyproject_text = read_version(pyproject_path, VERSION_PATTERN)
  _, init_text = read_version(init_path, INIT_PATTERN)

  if args.set_version:
    new_version = args.set_version.strip()
  elif args.bump != "none":
    new_version = bump_version(current_version, args.bump)
  else:
    new_version = current_version

  published_version = fetch_published_version(args.package)

  if args.fail_if_not_greater:
    ensure_greater(new_version, published_version)

  outputs = {
    "current_version": current_version,
    "new_version": new_version,
    "version_changed": str(new_version != current_version).lower(),
    "published_version": published_version,
    "pyproject_path": str(pyproject_path),
    "init_path": str(init_path)
  }

  if not args.dry_run and new_version != current_version:
    write_pyproject(pyproject_path, pyproject_text, new_version)
    write_init(init_path, init_text, new_version)

  emit_outputs(args, outputs)

  print(json.dumps(outputs, indent=2))
  return 0


if __name__ == "__main__":
  try:
    sys.exit(main())
  except Exception as exc:  # pragma: no cover - for CLI
    print(f"[manage_version] error: {exc}", file=sys.stderr)
    sys.exit(1)
