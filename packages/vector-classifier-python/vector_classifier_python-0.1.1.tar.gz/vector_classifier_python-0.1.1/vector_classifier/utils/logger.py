from __future__ import annotations
import json
import sys
from typing import Literal, Protocol, runtime_checkable

LoggerKind = Literal["silent", "json", "pretty"]

@runtime_checkable
class LoggerProtocol(Protocol):
    def info(self, m: object) -> None: ...
    def warn(self, m: object) -> None: ...
    def error(self, m: object) -> None: ...


class _SilentLogger:
    def info(self, m: object) -> None:
        return None

    def warn(self, m: object) -> None:
        return None

    def error(self, m: object) -> None:
        return None


class _JsonLogger:
    def info(self, m: object) -> None:
        sys.stdout.write(json.dumps({"level": "info", "message": m}) + "\n")

    def warn(self, m: object) -> None:
        sys.stdout.write(json.dumps({"level": "warn", "message": m}) + "\n")

    def error(self, m: object) -> None:
        sys.stderr.write(json.dumps({"level": "error", "message": m}) + "\n")


class _PrettyLogger:
    def info(self, m: object) -> None:
        sys.stdout.write(f"[vector-classifier] INFO: {m}\n")

    def warn(self, m: object) -> None:
        sys.stdout.write(f"[vector-classifier] WARN: {m}\n")

    def error(self, m: object) -> None:
        sys.stderr.write(f"[vector-classifier] ERROR: {m}\n")


def create_logger(kind: LoggerKind | LoggerProtocol | None) -> LoggerProtocol:
    if kind is None or kind == "silent":
        return _SilentLogger()
    if isinstance(kind, LoggerProtocol):
        return kind
    if kind == "json":
        return _JsonLogger()
    return _PrettyLogger()

