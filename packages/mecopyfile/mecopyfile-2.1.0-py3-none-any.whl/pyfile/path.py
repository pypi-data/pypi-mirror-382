from pathlib import Path as ComplexPath
import os


class Path:

    _literal: str
    _complex: ComplexPath

    def __init__(self, path: str):
        self._literal = self.format_path(path)
        self._complex = ComplexPath(self._literal)

    def format_path(self, path: str | ComplexPath) -> str:
        path = os.path.realpath(path)  # Reassign absolute path to path
        path = path.replace("\\", "/")
        while "//" in path:
            path.replace("//", "/")
        return path

    def exists(self) -> bool:
        return os.path.exists(self._literal)

    def get_literal(self) -> str:
        return self._literal

    def get_complex(self) -> ComplexPath:
        return self._complex
