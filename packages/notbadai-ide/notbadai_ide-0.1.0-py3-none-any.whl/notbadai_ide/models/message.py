from typing import Dict


class Message:
    def __init__(self, **kwargs):
        self.role: str = kwargs["role"]
        self.content: str = kwargs["content"]

    def to_dict(self) -> Dict[str, str]:
        return {'role': self.role, 'content': self.content}
