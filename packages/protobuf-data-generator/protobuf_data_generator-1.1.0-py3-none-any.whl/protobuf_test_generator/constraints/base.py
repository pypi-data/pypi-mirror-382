"""Shared helpers for constraint extraction and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from protobuf_test_generator.core.parser import (
    ConstraintRule,
    FieldInfo,
    MessageDefinition,
    ProtoParser,
)


@dataclass
class ConstraintBase:
    proto_source: str
    include_paths: Optional[Iterable[str]] = None

    def __post_init__(self) -> None:
        parser = ProtoParser()
        self._messages: Dict[str, MessageDefinition] = parser.parse(
            self.proto_source,
            include_paths=self.include_paths,
        )
        self._default_message = next(iter(self._messages), None)

    def get_message(self, message_name: Optional[str] = None) -> MessageDefinition:
        target = message_name or self._default_message
        if target is None:
            raise ValueError("No messages found in proto definition")
        if target not in self._messages:
            raise ValueError(f"Message '{target}' not found in proto definition")
        return self._messages[target]

    def get_field(
        self, field_name: str, message_name: Optional[str] = None
    ) -> FieldInfo:
        message = self.get_message(message_name)
        if field_name not in message.fields:
            raise ValueError(
                f"Field '{field_name}' not present in message '{message.name}'"
            )
        return message.fields[field_name]

    def validate(
        self, field_name: str, value, message_name: Optional[str] = None
    ) -> bool:
        field = self.get_field(field_name, message_name)
        return self._validate_field(field, value)

    def get_all_fields(
        self, message_name: Optional[str] = None
    ) -> Dict[str, FieldInfo]:
        message = self.get_message(message_name)
        return message.fields

    def validate_message(
        self, message_name: Optional[str], data: Dict[str, Any]
    ) -> bool:
        message = self.get_message(message_name)
        for field in message.fields.values():
            if field.name in data:
                if not self._validate_field(field, data[field.name]):
                    return False
        return True

    # ------------------------------------------------------------------
    # Internal helpers

    def _validate_field(self, field: FieldInfo, value) -> bool:
        for rule in field.constraints:
            if not self._passes_rule(field, value, rule):
                return False
        return True

    def _passes_rule(self, field: FieldInfo, value, rule: ConstraintRule) -> bool:
        if field.type in {"int32", "int64", "uint32", "uint64"}:
            if rule.rule_type == "gte":
                return value >= int(rule.value)
            if rule.rule_type == "lte":
                return value <= int(rule.value)
        if field.type == "string" or rule.category == "string":
            if rule.rule_type == "min_len":
                return len(value) >= int(rule.value)
            if rule.rule_type == "max_len":
                return len(value) <= int(rule.value)
            if rule.rule_type == "contains":
                return str(rule.value) in value
        if rule.category == "repeated" or field.repeated:
            if rule.rule_type == "min_items":
                return len(value) >= int(rule.value)
            if rule.rule_type == "max_items":
                return len(value) <= int(rule.value)
            if rule.rule_type == "unique":
                return len(set(value)) == len(value)
        return True


__all__ = ["ConstraintBase"]
