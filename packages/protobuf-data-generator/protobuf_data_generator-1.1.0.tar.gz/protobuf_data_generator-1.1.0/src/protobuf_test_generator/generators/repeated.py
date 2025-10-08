from random import choice, randint
from typing import List, Any


class RepeatedFieldGenerator:
    def __init__(self, field_type_generator, min_items: int = 1, max_items: int = 10):
        self.field_type_generator = field_type_generator
        self.min_items = min_items
        self.max_items = max_items

    def generate_valid(self) -> List[Any]:
        """Generate a list of valid repeated field values."""
        num_items = randint(self.min_items, self.max_items)
        return [self.field_type_generator.generate_valid() for _ in range(num_items)]

    def generate_invalid(self) -> List[Any]:
        """Generate a list of invalid repeated field values."""
        # Example of generating invalid data by exceeding max_items
        num_items = randint(self.max_items + 1, self.max_items + 5)
        return [self.field_type_generator.generate_valid() for _ in range(num_items)]


class NumericFieldGenerator:
    def generate_valid(self) -> int:
        return randint(1, 100)  # Example valid numeric value


class StringFieldGenerator:
    def generate_valid(self) -> str:
        return choice(
            ["valid_string_1", "valid_string_2"]
        )  # Example valid string value


# Example usage:
# numeric_generator = RepeatedFieldGenerator(NumericFieldGenerator())
# valid_numeric_list = numeric_generator.generate_valid()
# invalid_numeric_list = numeric_generator.generate_invalid()

# string_generator = RepeatedFieldGenerator(StringFieldGenerator())
# valid_string_list = string_generator.generate_valid()
# invalid_string_list = string_generator.generate_invalid()
