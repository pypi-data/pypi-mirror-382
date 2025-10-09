from ..file import File
from ..directory import Directory


class SegmentedSearchResult:

    parent: Directory = property(lambda self: self._parent)
    childs: list[File] | list[Directory] = property(lambda self: self._childs)

    def __init__(self, parent: Directory, childs: list[File] | list[Directory]):
        self._parent = parent
        self._childs = childs

    def to_paths(self) -> dict[str, list[str]]:
        return {
            self._parent.get_path(): list(
                map(lambda child: child.get_path(), self._childs)
            ),
        }
