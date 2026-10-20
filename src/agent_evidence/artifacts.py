"""Verify locally held artifact integrity, not the authenticity of execution."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .core import InvalidTrace


def verify_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Check the SHA256 and byte length of explicitly listed files.

    A passing manifest proves that supplied bytes match supplied digests.
    It does NOT establish who produced those bytes or whether tests executed.
    """
    if not isinstance(manifest, dict) or not isinstance(manifest.get("artifacts"), list):
        raise InvalidTrace("Manifest must contain an artifacts array.")
    base = Path(root).resolve(strict=True)
    if not base.is_dir():
        raise InvalidTrace("Manifest root must be a directory.")
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for item in manifest["artifacts"]:
        if not isinstance(item, dict):
            raise InvalidTrace("Each artifact must be an object.")
        name, digest, size = item.get("path"), item.get("sha256"), item.get("size")
        if not isinstance(name, str) or not name or "\x00" in name:
            raise InvalidTrace("Artifact path must be a nonempty string.")
        relative = Path(name)
        if relative.is_absolute() or relative.as_posix() != name or any(part in ("", ".", "..") for part in name.split("/")):
            raise InvalidTrace(f"Unsafe artifact path: {name!r}")
        if name in seen:
            raise InvalidTrace(f"Duplicate artifact path: {name!r}")
        seen.add(name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise InvalidTrace("sha256 must be 64 lowercase hexadecimal characters.")
        if type(size) is not int or size < 0:
            raise InvalidTrace("size must be a nonnegative integer.")
        path = base / relative
        actual_sha = None
        actual_size = None
        issue = None
        try:
            # Check every component for symlinks before following any file.
            cursor = base
            for component in relative.parts:
                cursor = cursor / component
                if cursor.is_symlink():
                    raise InvalidTrace(f"Symlink is not allowed: {name!r}")
            if not path.is_file():
                issue = "missing_or_not_regular_file"
            else:
                h = hashlib.sha256()
                actual_size = 0
                with path.open("rb") as handle:
                    while chunk := handle.read(1024 * 1024):
                        h.update(chunk)
                        actual_size += len(chunk)
                actual_sha = h.hexdigest()
                if actual_size != size:
                    issue = "size_mismatch"
                elif actual_sha != digest:
                    issue = "sha256_mismatch"
        except OSError as exc:
            issue = f"read_error:{type(exc).__name__}"
        checked.append({
            "path": name,
            "matches_manifest": issue is None,
            "issue": issue,
            "actual_sha256": actual_sha,
            "actual_size": actual_size,
        })
    return {
        "all_artifacts_match": bool(checked) and all(i["matches_manifest"] for i in checked),
        "artifact_count": len(checked),
        "results": checked,
        "evidence_level": "content_integrity_only",
    }
