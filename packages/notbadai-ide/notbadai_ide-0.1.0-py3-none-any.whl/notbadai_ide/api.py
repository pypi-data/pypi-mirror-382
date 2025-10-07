import os
import requests
import threading
from typing import Dict, List, Optional, Union

from .config import config
from .models.file import File
from .models.message import Message
from .models.terminal import Terminal
from .models.cursor import Cursor
from .models.api_key import APIKey
from .models.code_apply import CodeApplyChange


class ExtensionAPI:
    def __init__(self):
        self._local = threading.local()

    def load(self):
        self._local.uuid = os.environ['EXTENSION_UUID']
        host = os.environ['HOST']
        port = int(os.environ['PORT'])

        config.configure(host, port)

        kwargs = self._load_data()

        self._local.request_id = kwargs['request_id']
        self._local.repo_path = kwargs['repo_path']
        self._local.selection = kwargs.get('selection', None)
        self._local.clip_board = kwargs.get('clip_board', None)
        self._local.prompt = kwargs.get('prompt', None)
        self._local.chat_history = [Message(**m) for m in kwargs.get('chat_history', [])]
        self._local.current_terminal = kwargs.get('current_terminal', None)
        self._local.terminals = kwargs.get('terminals', [])
        self._local.api_keys = kwargs.get('api_keys', {})
        self._local.settings = kwargs.get('settings', {})
        self._local.ui_action = kwargs.get('ui_action', None)
        self._local.code_apply_change = kwargs.get('code_apply_change', None)

        opened_files = set(kwargs.get('opened_files'))
        self._local.repo_files = [File(p, self._local.repo_path, None, p in opened_files) for p in kwargs['repo']]

        if kwargs['current_file'] is not None:
            current_file_content = kwargs.get('current_file_content', None)
            self._local.current_file = File(kwargs['current_file'], self._local.repo_path, current_file_content, True)
        else:
            self._local.current_file = None

        context_files = {}
        for entry, values in kwargs.get('context_files', {}).items():
            files = [File(p, self._local.repo_path) for p in values]
            context_files[entry] = files
        self._local.context_files = context_files

        if kwargs['cursor'] is not None:
            self._local.cursor = Cursor(**kwargs['cursor'])
        else:
            self._local.cursor = None

    def cleanup(self):
        if hasattr(self._local, '__dict__'):
            self._local.__dict__.clear()

    def _dump(self, method: str, **kwargs):
        assert 'method' not in kwargs
        kwargs['method'] = method
        kwargs['request_id'] = self._local.request_id

        requests.post(f'http://{config.host}:{config.port}/api/extension/response/{self._local.uuid}', json=kwargs)

    def _load_data(self):
        response = requests.get(f'http://{config.host}:{config.port}/api/extension/data/{self._local.uuid}')
        response.raise_for_status()

        result = response.json()
        return result['data']

    def get_repo_files(self) -> List[File]:
        return self._local.repo_files

    def get_repo_path(self) -> str:
        return self._local.repo_path

    def get_current_file(self) -> Optional[File]:
        return self._local.current_file

    def get_selection(self) -> Optional[str]:
        return self._local.selection

    def get_clip_board(self) -> Optional[str]:
        return self._local.clip_board

    def get_cursor(self) -> Optional[Cursor]:
        return self._local.cursor

    def get_chat_history(self) -> List[Message]:
        return self._local.chat_history

    def get_current_terminal(self) -> Terminal:
        return Terminal(self._local.current_terminal, True)

    def get_terminals(self) -> List[Terminal]:
        res = []
        for terminal in self._local.terminals:
            is_current_terminal = terminal == self._local.current_terminal
            res.append(Terminal(terminal, is_current_terminal))

        return res

    def get_code_apply_change(self) -> CodeApplyChange:
        data = self._local.code_apply_change
        return CodeApplyChange(target_file_path=data['target_file_path'],
                               repo_path=self._local.repo_path,
                               patch_text=data['patch_text']
                               )

    def get_context_files(self) -> dict[str, list[File]]:
        return self._local.context_files

    def get_prompt(self) -> Optional[str]:
        return self._local.prompt

    def get_api_key(self, provider: str) -> Optional[APIKey]:
        if provider in self._local.api_keys:
            return APIKey(**self._local.api_keys[provider])

        return None

    def get_api_keys(self) -> List[APIKey]:
        res = []
        for k, v in self._local.api_keys.items():
            res.append(APIKey(**v))
        return res

    def get_setting(self, setting: str) -> Optional[any]:
        return self._local.settings.get(setting, None)

    def get_ui_action(self) -> Dict[str, str]:
        return self._local.ui_action

    def chat(self, content: str):
        self._dump('chat', content=content)

    def end_chat(self):
        self._dump('end_chat')

    def start_chat(self):
        self._dump('start_chat')

    def autocomplete(self, suggestions: List[Dict[str, str]]):
        self._dump('autocomplete', suggestions=suggestions)

    def update_file(self, patch: List[str], matches: List[List[int]]):
        self._dump('update_file', patch=patch, matches=matches)

    def highlight(self, results: List[Dict[str, Union[int, str]]]):
        self._dump('highlight', results=results)

    def inline_completion(self, text: str, cursor_row: int = None, cursor_column: int = None):
        self._dump('inline_completion', content=text, cursor_row=cursor_row, cursor_column=cursor_column)

    def log(self, message: str):
        self._dump('log', content=message)

    def ui_form(self, title: str, form_content: str):
        self._dump('ui_form', title=title, form_content=form_content)
