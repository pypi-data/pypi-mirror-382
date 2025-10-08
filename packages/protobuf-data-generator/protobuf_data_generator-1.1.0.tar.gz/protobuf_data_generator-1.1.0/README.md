# Protobuf Data Generator

[![PyPI](https://img.shields.io/pypi/v/protobuf-data-generator)](https://pypi.org/project/protobuf-data-generator/)
[![Python Versions](https://img.shields.io/pypi/pyversions/protobuf-data-generator)](https://pypi.org/project/protobuf-data-generator/)
[![Build Status](https://github.com/OfekiAlm/protobuf-data-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/OfekiAlm/protobuf-data-generator/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/OfekiAlm/protobuf-data-generator)](LICENSE)

## Overview

The **Protobuf Data Generator** creates realistic valid and invalid payloads for Protocol Buffer messages. It reads constraint annotations directly from your `.proto` files (for example, Protovalidate or Nanopb rules) and deterministically assembles data that either satisfies or intentionally violates those rules. The library is ideal for fuzzing, regression testing, and golden-data generation across embedded and backend protobuf workloads.

## Features

- **Deterministic valid payloads** generated from constraint metadata.
- **Targeted invalid samples** that break explicit rules (e.g., min/max, length, uniqueness).
- **Constraint backends** for Protovalidate and Nanopb, with a lightweight parser that understands enums and repeated fields.
- **Formatter outputs** for C arrays, raw bytes, JSON, and hexadecimal encodings.
- **Showcase fixtures** (`tests/fixtures/showcase.proto`) illustrating the full feature set end-to-end.

## Installation

```bash
pip install protobuf-data-generator
```

> **Supported Python versions:** 3.8 through 3.13. Older Python releases (3.7 and below) are no longer tested.

For local development:

```bash
git clone https://github.com/OfekiAlm/protobuf-data-generator.git
cd protobuf-data-generator
pip install -r requirements-dev.txt
```

## Usage

### Python API

```python
from protobuf_test_generator import DataGenerator

generator = DataGenerator(
		"tests/fixtures/showcase.proto",
		include_paths=["tests/fixtures"],
		constraints_type="protovalidate",  # or "nanopb"
)

valid_payload = generator.generate_valid("Showcase", seed=42)
invalid_payload = generator.generate_invalid(
		"Showcase",
		violate_field="email",
		violate_rule="min_len",
		seed=42,
)

binary_blob = generator.encode_to_binary("Showcase", valid_payload)
c_array = generator.format_output(binary_blob, "c_array", "showcase_payload")
```

### Showcase workflow

- `tests/fixtures/showcase.proto` – comprehensive proto covering numeric, string, enum, repeated, and nested-field constraints.
- `tests/test_showcase.py` – integration test demonstrating parsing, generation, validation, and formatting steps.
- The helper `validate.proto` shipped alongside the fixtures is a minimal stub replicating the option names used in the official [protovalidate](https://github.com/bufbuild/protovalidate) descriptors. It exists solely to exercise constraint parsing in tests.

### Command line interface

```bash
python -m protobuf_test_generator \
	--proto_file tests/fixtures/showcase.proto \
	--message Showcase \
	--format json
```

Optional flags:

- `-I / --include path` – repeatable include directories for proto imports.
- `--invalid --field FIELD --rule RULE` – produce a payload that violates a specific rule.
- `--seed N` – lock generation to deterministic output.

## Development

```bash
black --check src tests
flake8 src tests
mypy src
pytest
```

See the [CHANGELOG](CHANGELOG.md) for release history.

## Contributing

Issues and pull requests are welcome! Please discuss substantial changes in an issue before opening a PR.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE).