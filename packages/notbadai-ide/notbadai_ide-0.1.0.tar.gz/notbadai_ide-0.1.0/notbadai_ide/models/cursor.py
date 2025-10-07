from typing import Optional


class Cursor:
    def __init__(self, row: int, column: int, symbol: Optional[str] = None):
        self.row = row
        self.column = column
        self.symbol = symbol
