class ProtobufEncoder:
    def __init__(self, message_type):
        self.message_type = message_type

    def encode(self, data):
        """Encodes the given data into protobuf wire format."""
        if not isinstance(data, dict):
            raise ValueError(
                "Data must be a dictionary representing the protobuf message."
            )

        # Assuming we have a method to convert dict to protobuf message
        message = self.message_type(**data)
        return message.SerializeToString()

    def encode_multiple(self, data_list):
        """Encodes a list of data dictionaries into protobuf wire format."""
        return [self.encode(data) for data in data_list]
