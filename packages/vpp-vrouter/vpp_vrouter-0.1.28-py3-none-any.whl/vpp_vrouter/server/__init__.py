"""Server package init.

Exposes __version__ dynamically. Prefers installed distribution metadata
and falls back to parsing the local pyproject.toml when running from a
source checkout (editable / dev mode before installation).
"""

from __future__ import annotations

__all__ = ["__version__"]


def _get_version() -> str:
	# 1. Try importlib.metadata (Python 3.8+). Handles installed package.
	try:
		try:  # Python 3.10: importlib.metadata in stdlib
			from importlib.metadata import version, PackageNotFoundError  # type: ignore
		except ImportError:  # pragma: no cover
			from importlib_metadata import version, PackageNotFoundError  # type: ignore

		try:
			return version("vpp-vrouter")
		except PackageNotFoundError:
			pass
	except Exception:  # pragma: no cover - very defensive
		pass

	# 2. Fallback: parse pyproject.toml in repository root (relative to this file)
	import pathlib
	import re

	root = pathlib.Path(__file__).resolve().parent.parent.parent  # repo root (where pyproject.toml lives)
	pyproject = root / "pyproject.toml"
	if pyproject.is_file():
		try:
			text = pyproject.read_text(encoding="utf-8", errors="ignore")
			# Locate the [tool.poetry] section then extract version = "..."
			m = re.search(r"\[tool\.poetry\][^\[]*?^version\s*=\s*\"([^\"]+)\"", text, re.MULTILINE | re.DOTALL)
			if m:
				return m.group(1)
		except Exception:  # pragma: no cover
			pass

	# 3. Last resort
	return "0.0.0+dev"


__version__ = _get_version()

