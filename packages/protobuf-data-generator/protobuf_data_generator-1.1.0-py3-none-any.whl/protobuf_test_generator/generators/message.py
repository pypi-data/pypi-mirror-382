from protobuf_test_generator.core.generator import DataGenerator


class MessageGenerator:
    def __init__(self, proto_file, message_name, include_paths=None):
        self.proto_file = proto_file
        self.message_name = message_name
        self.include_paths = include_paths or []
        self.data_generator = DataGenerator(proto_file, include_paths=include_paths)

    def generate_valid(self, seed=None):
        return self.data_generator.generate_valid(self.message_name, seed=seed)

    def generate_invalid(self, violate_field=None, violate_rule=None):
        return self.data_generator.generate_invalid(
            self.message_name, violate_field=violate_field, violate_rule=violate_rule
        )

    def generate_nested_message(self, nested_message_name, seed=None):
        valid_data = self.generate_valid(seed=seed)
        nested_data = self.data_generator.generate_valid(nested_message_name, seed=seed)
        valid_data[nested_message_name] = nested_data
        return valid_data

    def encode_to_binary(self, data):
        return self.data_generator.encode_to_binary(self.message_name, data)

    def format_output(self, data, output_format):
        return self.data_generator.format_output(data, output_format)
