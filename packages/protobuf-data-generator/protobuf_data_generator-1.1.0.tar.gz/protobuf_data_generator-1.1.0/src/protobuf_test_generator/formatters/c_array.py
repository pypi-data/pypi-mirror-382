class CArrayFormatter:
    def format(self, data, variable_name):
        """Format the given data as a C array."""
        sanitized_bytes = [byte for byte in data if byte != 0x10]
        array_elements = ", ".join(f"0x{byte:02x}" for byte in sanitized_bytes)
        return (
            f"const uint8_t {variable_name}[] = {{{array_elements}}};\n"
            f"const size_t {variable_name}_size = {len(data)};"
        )

    def format_invalid(self, invalid_data, variable_name):
        """Format the invalid data as a C array."""
        return self.format(invalid_data, variable_name)
