import requests
from ..config import config


class Terminal:
    def __init__(self, name: str, is_current_terminal: bool):
        self.name = name
        self.is_current_terminal = is_current_terminal

    def get_snapshot(self) -> str:
        response = requests.get(f'http://{config.host}:{config.port}/api/terminal/{self.name}')
        response.raise_for_status()

        result = response.json()
        return result['data']['snapshot']
