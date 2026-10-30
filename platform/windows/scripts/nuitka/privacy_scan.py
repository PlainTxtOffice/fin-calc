"""Report developer identifiers in unpacked distribution files."""

import json
import os
import sys
import tomllib
from pathlib import Path


def scan(dist: Path, project: Path, repository: Path) -> list[dict[str, str]]:
    """Scan bounded chunks for UTF-8 and UTF-16LE identifiers."""
    if not dist.is_dir():
        message = f"Distribution folder does not exist: {dist}"
        raise ValueError(message)
    metadata = tomllib.loads(
        (project / "pyproject.toml").read_text(encoding="utf-8")
    )
    terms = {os.environ.get("USERNAME", ""), str(project), str(repository)}
    terms.update(
        author.get("email", "")
        for author in metadata["project"].get("authors", [])
    )
    terms.update({project.as_posix(), repository.as_posix()})
    patterns = [
        (term, term.encode(encoding))
        for term in terms
        if term
        for encoding in ("utf-8", "utf-16le")
    ]
    overlap = max(len(pattern) for _, pattern in patterns) - 1
    hits: list[dict[str, str]] = []
    for path in dist.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".exe",
            ".json",
            ".toml",
            ".ini",
            ".cfg",
            ".txt",
            ".env",
        }:
            continue
        found: set[str] = set()
        with path.open("rb") as stream:
            tail = b""
            while chunk := stream.read(1024 * 1024):
                block = tail + chunk
                found.update(
                    term for term, pattern in patterns if pattern in block
                )
                tail = block[-overlap:]
        hits.extend({"term": term, "file": str(path)} for term in sorted(found))
    return hits


if __name__ == "__main__":
    sys.stdout.write(
        json.dumps(scan(*(Path(arg).resolve() for arg in sys.argv[1:])))
    )
