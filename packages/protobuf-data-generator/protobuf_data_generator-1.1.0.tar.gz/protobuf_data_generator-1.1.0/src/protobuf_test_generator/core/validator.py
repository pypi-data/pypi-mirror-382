from google.protobuf.message import Message


class Validator:
    def __init__(self, constraints):
        self.constraints = constraints

    def validate(self, message: Message) -> bool:
        for field_name, field_value in message.DESCRIPTOR.fields.items():
            if field_name in self.constraints:
                if not self.constraints[field_name].validate(field_value):
                    return False
        return True

    def validate_all(self, messages: list) -> list:
        results = []
        for message in messages:
            is_valid = self.validate(message)
            results.append((message, is_valid))
        return results
