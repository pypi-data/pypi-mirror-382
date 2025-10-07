class Config:
    def __init__(self):
        self.host = None
        self.port = None

    def configure(self, host: str, port: int):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port


config = Config()
