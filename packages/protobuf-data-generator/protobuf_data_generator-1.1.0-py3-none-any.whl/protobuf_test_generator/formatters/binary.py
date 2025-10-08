class BinaryFormatter:
    def format(self, data):
        """Encode the given data to binary format."""
        return bytes(data)

    def save_to_file(self, data, file_path):
        """Save the binary data to a file."""
        with open(file_path, "wb") as f:
            f.write(self.format(data))
