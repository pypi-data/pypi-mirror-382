"""Nanopb-specific constraint helpers."""

from __future__ import annotations

from protobuf_test_generator.constraints.base import ConstraintBase


class NanopbConstraints(ConstraintBase):
    """Constraints handler for nanopb-generated protos.

    For the purposes of the tests this behaves identically to :class:`ConstraintBase`.
    """

    def __init__(self, proto_source: str, include_paths=None):
        super().__init__(proto_source, include_paths=include_paths)


__all__ = ["NanopbConstraints"]
