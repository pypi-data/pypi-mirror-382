from random import choice, randint
import string


class StringGenerator:
    def __init__(self):
        pass

    def generate_valid(self, min_len=1, max_len=10, charset=string.ascii_letters):
        length = randint(min_len, max_len)
        return "".join(choice(charset) for _ in range(length))

    def generate_invalid(self, min_len=1, max_len=10):
        # Generate a string that is guaranteed to be invalid
        # For example, a string that is too short or too long
        if min_len > 1:
            return ""  # Invalid because it's too short
        else:
            return "x" * (max_len + 1)  # Invalid because it's too long

    def generate_ascii(self, min_len=1, max_len=10):
        return self.generate_valid(
            min_len,
            max_len,
            charset=string.ascii_letters + string.digits + string.punctuation,
        )

    def generate_non_ascii(self, min_len=1, max_len=10):
        # Generate a string with non-ASCII characters
        length = randint(min_len, max_len)
        return "".join(
            chr(randint(128, 255)) for _ in range(length)
        )  # Non-ASCII characters
