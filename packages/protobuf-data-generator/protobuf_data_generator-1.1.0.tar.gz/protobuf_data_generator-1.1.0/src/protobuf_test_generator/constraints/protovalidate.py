"""ProtoValidate constraint implementation."""

from __future__ import annotations

from protobuf_test_generator.constraints.base import ConstraintBase


class ProtoValidateConstraints(ConstraintBase):
    """Constraint helper that reuses the generic base validator."""

    def __init__(
        self, proto_source: str, include_paths=None, default_message: str | None = None
    ):
        super().__init__(proto_source, include_paths=include_paths)
        if default_message and default_message in self._messages:
            self._default_message = default_message


__all__ = ["ProtoValidateConstraints"]
