class BaseFormatter:
    def format(self, data):
        raise NotImplementedError("Subclasses should implement this method.")

    def format_valid(self, data):
        raise NotImplementedError("Subclasses should implement this method.")

    def format_invalid(self, data):
        raise NotImplementedError("Subclasses should implement this method.")
