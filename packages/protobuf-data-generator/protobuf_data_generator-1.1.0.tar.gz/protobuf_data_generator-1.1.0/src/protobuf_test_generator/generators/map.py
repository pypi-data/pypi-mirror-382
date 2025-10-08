from typing import Any, Dict
import random


class MapFieldGenerator:
    def __init__(self, key_type: str, value_type: str):
        self.key_type = key_type
        self.value_type = value_type

    def generate_valid(self, num_entries: int) -> Dict[Any, Any]:
        """Generate a valid map with the specified number of entries."""
        return {
            self._generate_key(): self._generate_value() for _ in range(num_entries)
        }

    def generate_invalid(self, num_entries: int) -> Dict[Any, Any]:
        """Generate an invalid map by violating key or value constraints."""
        invalid_map = {}
        for _ in range(num_entries):
            key = self._generate_invalid_key()
            value = self._generate_invalid_value()
            invalid_map[key] = value
        return invalid_map

    def _generate_key(self) -> Any:
        """Generate a valid key based on the key type."""
        if self.key_type == "string":
            return self._generate_string_key()
        elif self.key_type == "int":
            return self._generate_int_key()
        # Add more key types as needed
        raise ValueError(f"Unsupported key type: {self.key_type}")

    def _generate_value(self) -> Any:
        """Generate a valid value based on the value type."""
        if self.value_type == "string":
            return self._generate_string_value()
        elif self.value_type == "int":
            return self._generate_int_value()
        # Add more value types as needed
        raise ValueError(f"Unsupported value type: {self.value_type}")

    def _generate_invalid_key(self) -> Any:
        """Generate an invalid key."""
        # Logic to generate an invalid key
        return None  # Placeholder for invalid key generation logic

    def _generate_invalid_value(self) -> Any:
        """Generate an invalid value."""
        # Logic to generate an invalid value
        return None  # Placeholder for invalid value generation logic

    def _generate_string_key(self) -> str:
        """Generate a valid string key."""
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5))

    def _generate_int_key(self) -> int:
        """Generate a valid integer key."""
        return random.randint(1, 100)

    def _generate_string_value(self) -> str:
        """Generate a valid string value."""
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))

    def _generate_int_value(self) -> int:
        """Generate a valid integer value."""
        return random.randint(1, 100)
