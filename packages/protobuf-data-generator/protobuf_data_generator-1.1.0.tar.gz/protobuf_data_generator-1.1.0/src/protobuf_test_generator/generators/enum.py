from random import choice
from typing import List


class EnumGenerator:
    def __init__(self, enum_values: List[str]):
        self.enum_values = enum_values

    def generate_valid(self) -> str:
        """Generate a valid enum value."""
        return choice(self.enum_values)

    def generate_invalid(self) -> str:
        """Generate an invalid enum value."""
        # Assuming the invalid value is simply a string not in the enum values
        invalid_value = "INVALID_ENUM_VALUE"
        return invalid_value

    def generate_random(self, valid: bool) -> str:
        """Generate either a valid or invalid enum value based on the flag."""
        if valid:
            return self.generate_valid()
        else:
            return self.generate_invalid()
