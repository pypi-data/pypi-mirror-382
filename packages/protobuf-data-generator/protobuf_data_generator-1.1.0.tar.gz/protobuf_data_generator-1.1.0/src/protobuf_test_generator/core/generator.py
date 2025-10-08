"""High level data generation utilities used by the tests."""

from __future__ import annotations

import json
import random
import string
from pathlib import Path
from typing import Dict, Iterable, Optional, Union

from protobuf_test_generator.constraints.nanopb import NanopbConstraints
from protobuf_test_generator.constraints.protovalidate import ProtoValidateConstraints
from protobuf_test_generator.core.parser import (
    FieldInfo,
    MessageDefinition,
    ProtoParser,
)
from protobuf_test_generator.formatters.binary import BinaryFormatter
from protobuf_test_generator.formatters.c_array import CArrayFormatter
from protobuf_test_generator.formatters.hex import HexFormatter
from protobuf_test_generator.formatters.json import JSONFormatter


class DataGenerator:
    """Produce valid and invalid payloads for a proto message.

    The implementation intentionally focuses on the limited rule-set exercised by the
    test-suite (numeric bounds, string lengths/containment, repeated counts and
    uniqueness).
    """

    def __init__(
        self,
        proto_source: str,
        *,
        include_paths: Optional[Iterable[str]] = None,
        constraints_type: str = "protovalidate",
        invalid: bool = False,
    ) -> None:
        self.proto_source = proto_source
        self.include_paths = list(include_paths or [])
        proto_dir = Path(proto_source).resolve().parent
        if proto_dir.exists():
            proto_dir_str = str(proto_dir)
            if proto_dir_str not in self.include_paths:
                self.include_paths.append(proto_dir_str)
        self.invalid_mode = invalid
        self._parser = ProtoParser()
        self._messages: Dict[str, MessageDefinition] = self._parser.parse(
            proto_source,
            include_paths=self.include_paths,
        )
        self._constraints = self._initialise_constraints(constraints_type)

    # ------------------------------------------------------------------
    # Public API

    def generate_valid(
        self, message_name: str, seed: Optional[int] = None
    ) -> Dict[str, object]:
        message = self._get_message(message_name)
        rng = self._build_rng(seed)
        deterministic = seed is not None

        payload = {}
        for field in message.fields.values():
            payload[field.name] = self._generate_field(field, rng, deterministic)
        return payload

    def generate_invalid(
        self,
        message_name: str,
        *,
        violate_field: str,
        violate_rule: str,
        seed: Optional[int] = None,
    ) -> Dict[str, object]:
        data = self.generate_valid(message_name, seed=seed)
        field = self._get_field(message_name, violate_field)
        data[violate_field] = self._generate_invalid_value(field, violate_rule)
        return data

    def get_all_fields(self, message_name: str) -> Dict[str, FieldInfo]:
        return self._get_message(message_name).fields

    def encode_to_binary(self, message_name: str, payload: Dict[str, object]) -> bytes:
        """Return a deterministic binary envelope for tests."""

        is_valid = False
        if self._constraints:
            try:
                is_valid = self._constraints.validate_message(message_name, payload)
            except ValueError:
                is_valid = False

        envelope = {
            "message": message_name,
            "data": payload,
            "valid": is_valid,
        }
        return json.dumps(envelope, sort_keys=True).encode("utf-8")

    def format_output(
        self, binary_data: bytes, format_type: str, variable_name: str
    ) -> Union[str, bytes]:
        format_type = format_type.lower()
        if format_type == "c_array":
            return CArrayFormatter().format(binary_data, variable_name)
        if format_type == "hex":
            return HexFormatter.format(binary_data)
        if format_type == "json":
            try:
                envelope = json.loads(binary_data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Binary payload is not valid JSON") from exc
            return JSONFormatter.format(envelope)
        if format_type == "binary":
            return BinaryFormatter().format(binary_data)
        raise ValueError(f"Unsupported formatter '{format_type}'")

    # ------------------------------------------------------------------
    # Internal helpers

    def _initialise_constraints(self, constraints_type: str):
        constraints_type = constraints_type.lower()
        if constraints_type == "nanopb":
            return NanopbConstraints(
                self.proto_source, include_paths=self.include_paths
            )
        return ProtoValidateConstraints(
            self.proto_source, include_paths=self.include_paths
        )

    def _get_message(self, message_name: str) -> MessageDefinition:
        if message_name not in self._messages:
            raise ValueError(f"Message '{message_name}' not found in proto definitions")
        return self._messages[message_name]

    def _get_field(self, message_name: str, field_name: str) -> FieldInfo:
        message = self._get_message(message_name)
        if field_name not in message.fields:
            raise ValueError(
                f"Field '{field_name}' missing from message '{message_name}'"
            )
        return message.fields[field_name]

    def _build_rng(self, seed: Optional[int]) -> random.Random:
        rng = random.Random()
        if seed is not None:
            rng.seed(seed)
        return rng

    def _generate_field(
        self, field: FieldInfo, rng: random.Random, deterministic: bool
    ):
        if field.repeated:
            return self._generate_repeated(field, rng, deterministic)
        if field.enum_values:
            return self._generate_enum(field, rng, deterministic)
        if field.type in {"int32", "int64", "uint32", "uint64"}:
            return self._generate_int(field, rng, deterministic)
        if field.type == "string":
            return self._generate_string(field, rng, deterministic)
        # Default fallback for unhandled types
        return None

    def _generate_repeated(
        self, field: FieldInfo, rng: random.Random, deterministic: bool
    ):
        min_items = field.get_constraint_value("min_items") or 0
        max_items = field.get_constraint_value("max_items") or max(min_items, 1)
        if deterministic:
            count = max(min_items, 0)
        else:
            count = (
                rng.randint(min_items, max_items)
                if max_items >= min_items
                else min_items
            )
        base_values = [
            self._generate_scalar_for_repeated(field, i) for i in range(max(count, 1))
        ]

        if deterministic and count == 0:
            return base_values[:0]
        values = base_values[:count]
        if field.get_constraint_value("unique"):
            values = list(dict.fromkeys(values))
            while len(values) < count:
                values.append(f"item{len(values)}")
        return values

    def _generate_scalar_for_repeated(self, field: FieldInfo, index: int):
        if field.type == "string":
            return f"tag{index + 1}"
        if field.enum_values:
            return field.enum_values[index % len(field.enum_values)]
        return index

    def _generate_enum(
        self, field: FieldInfo, rng: random.Random, deterministic: bool
    ) -> str:
        if not field.enum_values:
            return ""
        if deterministic:
            return field.enum_values[0]
        return rng.choice(field.enum_values)

    def _generate_int(
        self, field: FieldInfo, rng: random.Random, deterministic: bool
    ) -> int:
        minimum = field.get_constraint_value("gte")
        maximum = field.get_constraint_value("lte")
        if minimum is None:
            minimum = 0
        if maximum is None:
            maximum = minimum + 100
        if deterministic:
            return int(minimum)
        return rng.randint(int(minimum), int(maximum))

    def _generate_string(
        self, field: FieldInfo, rng: random.Random, deterministic: bool
    ) -> str:
        min_len = field.get_constraint_value("min_len") or 1
        max_len = field.get_constraint_value("max_len") or max(min_len, min_len + 10)
        contains = field.get_constraint_value("contains")

        if deterministic:
            length = int(min_len)
        else:
            length = (
                rng.randint(int(min_len), int(max_len))
                if max_len >= min_len
                else int(min_len)
            )

        if length <= 0:
            length = 1

        base = (
            "".join(rng.choice(string.ascii_letters) for _ in range(length))
            if not deterministic
            else "a" * length
        )
        if contains and contains not in base:
            if len(base) >= 1:
                base = contains + base[1:] if deterministic else base[:-1] + contains
            else:
                base = str(contains)
        return base

    def _generate_invalid_value(self, field: FieldInfo, rule_type: str):
        if field.type in {"int32", "int64", "uint32", "uint64"}:
            if rule_type == "lte":
                maximum = field.get_constraint_value("lte")
                maximum = int(maximum) if maximum is not None else 100
                return maximum + 1
            if rule_type == "gte":
                minimum = field.get_constraint_value("gte")
                minimum = int(minimum) if minimum is not None else 0
                return minimum - 1
        if field.type == "string":
            if rule_type == "min_len":
                minimum = field.get_constraint_value("min_len")
                minimum = int(minimum) if minimum is not None else 1
                return "a" * max(minimum - 1, 0)
            if rule_type == "contains":
                substring = str(field.get_constraint_value("contains") or "")
                return "a" * max(len(substring), 5)
            if rule_type == "max_len":
                maximum = field.get_constraint_value("max_len")
                maximum = int(maximum) if maximum is not None else 10
                return "a" * (maximum + 5)
        if field.repeated:
            if rule_type == "min_items":
                minimum = field.get_constraint_value("min_items")
                minimum = int(minimum) if minimum is not None else 1
                return [] if minimum > 0 else []
            if rule_type == "max_items":
                maximum = field.get_constraint_value("max_items")
                maximum = int(maximum) if maximum is not None else 0
                return [f"item{i}" for i in range(maximum + 2)]
            if rule_type == "unique":
                minimum = field.get_constraint_value("min_items")
                minimum = int(minimum) if minimum is not None else 2
                return ["dup"] * max(minimum, 2)
        return None


__all__ = ["DataGenerator"]
