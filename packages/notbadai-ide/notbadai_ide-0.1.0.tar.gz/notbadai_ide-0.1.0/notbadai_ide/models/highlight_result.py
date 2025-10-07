class HighlightResult:
    def __init__(self,
                 file_path: str,
                 description: str,
                 *
                 row_from: int,
                 row_to: int = None,
                 column_from: int = None,
                 column_to: int = None,
                 ) -> None:
        self.file_path = file_path
        self.description = description
        self.row_from = row_from
        self.row_to = row_to
        self.column_from = column_from
        self.column_to = column_to

    def to_dict(self):
        return {
            'file_path': self.file_path,
            'description': self.description,
            'row_from': self.row_from,
            'row_to': self.row_to,
            'column_from': self.column_from,
            'column_to': self.column_to
        }
