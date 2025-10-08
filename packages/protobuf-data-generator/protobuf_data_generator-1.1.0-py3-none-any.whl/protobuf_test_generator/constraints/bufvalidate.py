"""BufValidate constraint helpers."""

from __future__ import annotations

from protobuf_test_generator.constraints.base import ConstraintBase


class BufValidateConstraints(ConstraintBase):
    """Thin wrapper around :class:`ConstraintBase` for BufValidate projects."""

    def __init__(
        self, proto_source: str, include_paths=None, default_message: str | None = None
    ):
        super().__init__(proto_source, include_paths=include_paths)
        if default_message and default_message in self._messages:
            self._default_message = default_message


__all__ = ["BufValidateConstraints"]
