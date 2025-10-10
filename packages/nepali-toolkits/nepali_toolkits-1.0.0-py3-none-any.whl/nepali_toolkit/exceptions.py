from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

class ErrorCode(str, Enum):
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    OUT_OF_RANGE   = "OUT_OF_RANGE"
    VALIDATION     = "VALIDATION"
    PARSE          = "PARSE"
    INTERNAL       = "INTERNAL"

class NepalToolkitError(Exception):
    code: ErrorCode = ErrorCode.INTERNAL
    def __init__(self, message: str, *, code: ErrorCode | None = None, context: dict | None = None):
        super().__init__(message); self.code = code or self.code; self.context = context or {}

class DataNotFoundError(NepalToolkitError): code = ErrorCode.DATA_NOT_FOUND
class OutOfRangeError   (NepalToolkitError): code = ErrorCode.OUT_OF_RANGE
class ValidationError   (NepalToolkitError): code = ErrorCode.VALIDATION
class ParseError        (NepalToolkitError): code = ErrorCode.PARSE

@dataclass(frozen=True)
class Result:
    ok: bool
    value: object | None = None
    error: NepalToolkitError | None = None

def ok(v: object) -> Result:  return Result(True, value=v)
def err(e: NepalToolkitError) -> Result: return Result(False, error=e)
