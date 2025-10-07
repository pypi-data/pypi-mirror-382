class APIKey:
    def __init__(self, key: str, provider: str, default: bool):
        self.key: str = key
        self.provider: str = provider
        self.default: bool = default