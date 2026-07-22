#!/usr/bin/env python3
"""Fail when public profile text contains common private-data indicators."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {"", ".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".toml"}

PATTERNS = {
    "private IPv4 address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "carrier-grade NAT address": re.compile(
        r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"
    ),
    "local hostname": re.compile(r"(?i)\b[a-z0-9][a-z0-9.-]*\.local\b"),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "MAC-like value": re.compile(r"(?i)\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b"),
    "private key block": re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----"),
    "absolute user path": re.compile(r"(?:/Users/|/home/)[A-Za-z0-9._-]+/"),
    "likely access token": re.compile(r"\b(?:gh[pousr]_|github_pat_|sk-|xox[baprs]-)[A-Za-z0-9_-]{8,}\b"),
    "private source repository link": re.compile(
        r"https://github\.com/GumbiiDigital/(?:dgx-cluster|dgx-spark-playbooks|"
        r"dgx-routeros-agent|dgx-routeros-agent-rsl-flywheel|"
        r"dgx-spark-guarded-power-recovery|glm-5-2-on-dgx-spark|spark-nvfp4-lab)(?:[/?#]|$)",
        re.I,
    ),
}


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.resolve() == SELF:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def main() -> int:
    findings: list[str] = []
    for path in text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: {label}")

    if findings:
        print("Publication-safety check failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    files = text_files()
    print(f"Publication-safety check passed ({len(files)} text files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
