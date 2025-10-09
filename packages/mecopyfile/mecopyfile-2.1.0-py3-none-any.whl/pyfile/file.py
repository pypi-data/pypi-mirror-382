from .systorage import Systorage
import os


class File(Systorage):

    def __init__(self, path: str):
        super().__init__(path)
        if os.path.exists(path) and not os.path.isfile(path):
            raise Exception(f'"{path}" is not a file')
        # Logic to bind to parent

    def create(self) -> bool:
        self._path.get_complex().touch(exist_ok=True)
        return self.exists()

    def delete(self, delete_content: bool = False) -> bool:
        content_deleted: bool = False
        if delete_content:
            content_deleted = self.delete_content()
        if delete_content and not content_deleted:
            raise Exception("Content hasn't been deleted, file deletion aborted.")
        os.remove(self._path.get_literal())
        return self.exists() == False

    def get_size(self) -> int:
        return os.path.getsize(self._path.get_literal())

    def append(self, content: str):
        with open(self._path.get_literal(), "a") as f:
            f.write(content)

    def write(self, content: str):
        with open(self._path.get_literal(), "w") as f:
            f.write(content)

    def read_to_end(self) -> str:
        file_content: str
        with open(self._path.get_literal(), "r") as f:
            f.seek(0)
            file_content = f.read()
        return file_content

    def delete_content(self):
        self.write("")
        return self.get_size() == 0

    def get_extension(self):
        path = self.get_path()
        return path[path.rfind(".") : len(path)]

    def _update_metadata(self, path):
        pass
