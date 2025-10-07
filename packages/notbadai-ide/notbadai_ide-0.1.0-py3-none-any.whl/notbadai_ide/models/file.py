from pathlib import Path


class File:
    def __init__(self, path: str, repo_path: str, content: str = None, is_open: bool = False):
        self.path: str = path
        self.is_open = is_open
        self._fs_path = Path(f'{repo_path}/{path}')
        self._content = content

    def suffix(self) -> str:
        return self._fs_path.suffix

    def exists(self) -> bool:
        return self._fs_path.is_file()

    def get_content(self) -> str:
        if self._content is not None:
            return self._content

        with open(self._fs_path, 'r') as f:
            self._content = f.read()
        return self._content
