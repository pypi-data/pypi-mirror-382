from .file import File


class CodeApplyChange:
    def __init__(self, target_file_path: str, repo_path: str, patch_text: str):
        self.target_file = File(target_file_path, repo_path)
        self.patch_text = patch_text
