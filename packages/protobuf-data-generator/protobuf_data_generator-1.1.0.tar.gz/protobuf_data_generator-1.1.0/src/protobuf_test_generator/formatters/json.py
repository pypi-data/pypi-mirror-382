from json import dumps


class JSONFormatter:
    @staticmethod
    def format(data):
        return dumps(data, separators=(", ", ": "))
