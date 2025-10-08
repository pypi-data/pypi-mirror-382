class HexFormatter:
    @staticmethod
    def format(data: bytes) -> str:
        """Convert binary data to a hexadecimal string."""
        return data.hex()

    @staticmethod
    def format_with_prefix(data: bytes, prefix: str = "0x") -> str:
        """Convert binary data to a hexadecimal string with a prefix."""
        hex_string = data.hex()
        return f"{prefix}{hex_string}"
