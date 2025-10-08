"""Helpers for interacting with proto files used in tests."""

from __future__ import annotations

import os
from typing import Dict

from protobuf_test_generator.core.parser import MessageDefinition, ProtoParser


def load_proto_file(proto_file_path: str) -> str:
    """Return the textual contents of a proto file."""

    if not os.path.isfile(proto_file_path):
        raise FileNotFoundError(f"Proto file not found: {proto_file_path}")
    with open(proto_file_path, "r", encoding="utf-8") as handle:
        return handle.read()


def parse_proto_file(proto_source: str) -> Dict[str, MessageDefinition]:
    """Parse the given proto source (path or content) using the lightweight parser."""

    parser = ProtoParser()
    return parser.parse(proto_source)


def list_proto_messages(proto_file_path: str):
    """List message names defined in a proto file."""

    messages = parse_proto_file(proto_file_path)
    return list(messages.keys())
