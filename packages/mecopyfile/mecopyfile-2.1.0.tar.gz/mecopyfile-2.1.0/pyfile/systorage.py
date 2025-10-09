from abc import ABC, abstractmethod
from .path import Path
import os


class Systorage(ABC):

    _path: Path
    _name: str
    _parent = None

    def __init__(self, path):
        self._path = Path(path)
        self.__name = self._path.get_complex().name

    @abstractmethod
    def _update_metadata(self, path: str):
        self._path = Path(path)
        self.__name = self._path.get_complex().name

    def exists(self) -> bool:
        return self._path.exists()

    @abstractmethod
    def create(self) -> bool:
        pass

    @abstractmethod
    def delete(self) -> bool:
        pass

    @abstractmethod
    def get_size(self) -> int:
        pass

    def rename(self, new_name: str) -> bool:
        if "/" or "\\" in new_name:
            raise Exception("This method is not intended to be used as move method")
        old_path = self._path.get_literal()
        new_path = f"{str(self._path.get_complex().parent())}/{new_name}"
        os.rename(self._path._literal, new_path)
        self._update_metadata(new_path)
        return os.path.exists(old_path) == False and os.path.exists(new_path) == True

    def move(self, new_path: str) -> bool:
        new_path = os.path.realpath(new_path)  # Format to absolute
        # If new path do not exists
        if not os.path.exists(new_path):
            raise Exception(f'"{new_path}" do not exists')
        old_path = self._path.get_literal()
        os.rename(old_path, new_path)
        self._update_metadata(new_path)
        return os.path.exists(old_path) == False and os.path.exists(new_path) == True

    ### Getters

    def get_name(self) -> str:
        return self.__name

    def get_path(self) -> str:
        return self._path.get_literal()

    def get_parent(self):
        from .directory import Directory

        if self._parent is None:
            self._parent = Directory(os.path.dirname(self._path.get_literal()))
        return self._parent

    def get_path_object(self) -> Path:
        return self._path
