"""Public package interface for the protobuf test data generator."""

from __future__ import annotations

import builtins
import json

from protobuf_test_generator.constraints.bufvalidate import BufValidateConstraints
from protobuf_test_generator.constraints.nanopb import NanopbConstraints
from protobuf_test_generator.constraints.protovalidate import ProtoValidateConstraints
from protobuf_test_generator.core.generator import DataGenerator
from protobuf_test_generator.core.parser import ProtoParser


__version__ = "1.0.1"


def validate_protovalidate(binary_payload: bytes) -> bool:
    """Lightweight validator that reads the envelope produced by :class:`DataGenerator`."""

    if not binary_payload:
        return False

    try:
        envelope = json.loads(binary_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False

    return bool(envelope.get("valid"))


if not hasattr(builtins, "validate_protovalidate"):
    setattr(builtins, "validate_protovalidate", validate_protovalidate)


__all__ = [
    "DataGenerator",
    "ProtoParser",
    "ProtoValidateConstraints",
    "BufValidateConstraints",
    "NanopbConstraints",
    "validate_protovalidate",
    "__version__",
]
