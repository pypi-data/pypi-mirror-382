import sys
from argparse import ArgumentParser

from protobuf_test_generator.core.generator import DataGenerator


def main():
    parser = ArgumentParser(description="Protobuf Test Data Generator CLI")
    parser.add_argument("proto_file", help="Path to the .proto file")
    parser.add_argument("message", help="Message name to generate data for")
    parser.add_argument("--invalid", action="store_true", help="Generate invalid data")
    parser.add_argument("--field", help="Field to violate (required with --invalid)")
    parser.add_argument("--rule", help="Rule to violate (required with --invalid)")
    parser.add_argument(
        "--format",
        choices=["binary", "c_array", "hex", "json"],
        default="c_array",
        help="Output format (default: c_array)",
    )
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument(
        "-I", "--include", action="append", help="Include path for proto files"
    )

    args = parser.parse_args()

    generator = DataGenerator(args.proto_file, include_paths=args.include)

    if args.invalid and (not args.field or not args.rule):
        parser.error("--field and --rule are required when using --invalid")

    if args.invalid:
        payload = generator.generate_invalid(
            args.message,
            violate_field=args.field,
            violate_rule=args.rule,
            seed=args.seed,
        )
    else:
        payload = generator.generate_valid(args.message, seed=args.seed)

    binary_data = generator.encode_to_binary(args.message, payload)
    output = generator.format_output(binary_data, args.format, args.message)

    if args.output:
        mode = "wb" if args.format == "binary" else "w"
        with open(args.output, mode) as fh:
            fh.write(output)
    else:
        if args.format == "binary":
            sys.stdout.buffer.write(output)
        else:
            print(output)


if __name__ == "__main__":
    main()
