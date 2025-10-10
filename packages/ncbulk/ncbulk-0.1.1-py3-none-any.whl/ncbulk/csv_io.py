"""CSV helpers for report and input parsing."""

from __future__ import annotations

import csv
from typing import Iterable


REPORT_HEADER = ["Username", "Email", "Displayname", "Groups", "Password", "Status"]


def create_report_csv(path: str, *, delimiter: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(REPORT_HEADER)


def append_report_row(
    path: str,
    *,
    delimiter: str,
    username: str,
    email: str,
    displayname: str,
    groups: Iterable[str],
    password: str | None,
    status: str,
) -> None:
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(
            [
                username,
                email,
                displayname,
                ",".join(groups),
                password or "",
                status,
            ]
        )


def dict_rows(path: str, *, delimiter: str) -> Iterable[dict]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield {k.lower(): v for k, v in row.items() if k is not None}
