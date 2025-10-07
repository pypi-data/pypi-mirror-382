class QueryException(Exception):
    def __init__(self, message: str, type: str = "BSECURE error"):
        self.type = type
        self.message = message
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.type}: {self.message}"

    def __str__(self):
        return repr(self)


class ClientException(Exception):
    pass
