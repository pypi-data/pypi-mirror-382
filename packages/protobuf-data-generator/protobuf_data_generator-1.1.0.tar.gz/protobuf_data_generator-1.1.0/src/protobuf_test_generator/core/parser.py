"""Utilities for parsing a small subset of .proto definitions used in tests."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class ConstraintRule:
    category: str
    rule_type: str
    value: Any


@dataclass
class FieldInfo:
    name: str
    type: str
    repeated: bool = False
    constraints: List[ConstraintRule] = field(default_factory=list)
    enum_values: Optional[List[str]] = None

    def get_constraint_value(self, rule_type: str) -> Optional[Any]:
        for rule in self.constraints:
            if rule.rule_type == rule_type:
                return rule.value
        return None


@dataclass
class MessageDefinition:
    name: str
    fields: Dict[str, FieldInfo] = field(default_factory=dict)


class ProtoParser:
    """A light-weight parser for extracting messages and constraints from proto files."""

    _MESSAGE_PATTERN = re.compile(
        r"message\s+(?P<name>\w+)\s*\{(?P<body>.*?)\}", re.DOTALL
    )
    _FIELD_PATTERN = re.compile(
        r"^(?P<label>repeated\s+)?(?P<type>\w+)\s+"
        r"(?P<name>\w+)\s*=\s*\d+"
        r"(?:\s*\[(?P<options>.*)\])?\s*$",
        re.DOTALL,
    )
    _CONSTRAINT_PATTERN = re.compile(
        r"\(validate\.rules\)\.(?P<category>\w+)\.(?P<rule>\w+)\s*=\s*(?P<value>.+)",
        re.IGNORECASE,
    )
    _ENUM_PATTERN = re.compile(r"enum\s+(?P<name>\w+)\s*\{(?P<body>.*?)\}", re.DOTALL)

    def __init__(self) -> None:
        self._messages: Dict[str, MessageDefinition] = {}

    def parse(
        self, proto_source: str, *, include_paths: Optional[Iterable[str]] = None
    ) -> Dict[str, MessageDefinition]:
        """Parse a proto definition and return message metadata.

        Args:
            proto_source: Either a path to a .proto file or the textual content of the proto.
            include_paths: Unused placeholder for compatibility with the public API.

        Returns:
            A mapping from message name to :class:`MessageDefinition`.
        """

        include_paths = list(include_paths or [])
        content = self._load_content(proto_source, include_paths)
        self._messages = {}
        self._enums: Dict[str, List[str]] = {}

        if content.count("{") != content.count("}"):
            raise ValueError("Unbalanced braces in proto definition")

        for enum_match in self._ENUM_PATTERN.finditer(content):
            enum_name = enum_match.group("name")
            enum_body = enum_match.group("body")
            self._enums[enum_name] = self._parse_enum(enum_body)

        for match in self._MESSAGE_PATTERN.finditer(content):
            message_name = match.group("name")
            body = match.group("body")
            definition = MessageDefinition(name=message_name)

            for field_statement in self._split_fields(body):
                field_info = self._parse_field(field_statement)
                if field_info:
                    definition.fields[field_info.name] = field_info

            self._messages[message_name] = definition

        return self._messages

    def _load_content(self, proto_source: str, include_paths: List[str]) -> str:
        if os.path.isfile(proto_source):
            with open(proto_source, "r", encoding="utf-8") as handle:
                return handle.read()

        for include_path in include_paths:
            candidate = os.path.join(include_path, proto_source)
            if os.path.isfile(candidate):
                with open(candidate, "r", encoding="utf-8") as handle:
                    return handle.read()

        # Treat proto_source as raw proto content
        return proto_source

    def _split_fields(self, body: str) -> List[str]:
        fields: List[str] = []
        for raw_field in body.split(";"):
            cleaned = raw_field.strip()
            if cleaned:
                fields.append(cleaned)
        return fields

    def _parse_field(self, field_statement: str) -> Optional[FieldInfo]:
        normalized = " ".join(field_statement.split())
        match = self._FIELD_PATTERN.match(normalized)
        if not match:
            return None

        repeated = bool(match.group("label"))
        field_type = match.group("type")
        name = match.group("name")
        options = match.group("options") or ""

        constraints = self._parse_constraints(options)
        enum_values = self._enums.get(field_type)
        return FieldInfo(
            name=name,
            type=field_type,
            repeated=repeated,
            constraints=constraints,
            enum_values=enum_values,
        )

    def _parse_constraints(self, options: str) -> List[ConstraintRule]:
        if not options:
            return []

        cleaned_options = options.replace("\n", " ")
        parts = [
            part.strip().rstrip("]")
            for part in cleaned_options.split(",")
            if part.strip()
        ]

        constraints: List[ConstraintRule] = []
        for part in parts:
            match = self._CONSTRAINT_PATTERN.match(part)
            if not match:
                continue

            category = match.group("category")
            rule = match.group("rule")
            raw_value = match.group("value").strip().strip("]")
            value: Any = self._convert_value(raw_value)
            constraints.append(
                ConstraintRule(category=category, rule_type=rule, value=value)
            )

        return constraints

    def _convert_value(self, value: str) -> Any:
        trimmed = value.strip()
        if trimmed.lower() == "true":
            return True
        if trimmed.lower() == "false":
            return False
        if trimmed.startswith('"') and trimmed.endswith('"'):
            return trimmed[1:-1]
        if trimmed.startswith("'") and trimmed.endswith("'"):
            return trimmed[1:-1]
        # Attempt integer conversion
        try:
            return int(trimmed)
        except ValueError:
            return trimmed

    @property
    def messages(self) -> Dict[str, MessageDefinition]:
        return self._messages

    def _parse_enum(self, body: str) -> List[str]:
        members: List[str] = []
        for raw_line in body.split(";"):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split()
            if parts:
                members.append(parts[0])
        return members
