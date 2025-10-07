from .models.file import File
from .models.api_key import APIKey
from .models.terminal import Terminal
from .models.cursor import Cursor
from .models.message import Message

from .api import ExtensionAPI

api = ExtensionAPI()

START_METADATA = '\n<metadata>'
END_METADATA = '</metadata>\n'
START_THINK = '<collapse>'
END_THINK = '</collapse>'
