from ..enums.extensions import Extensions


class SearchOptions:

    recursion: bool = property(lambda self: self._recursion)
    segmentation: bool = property(lambda self: self._segmentation)
    extensions: list[str] = property(lambda self: self._extensions)

    def __init__(
        self,
        recursion: bool = False,
        segmentation: bool = False,
        extensions: list[str | Extensions] = [],
    ):
        self._recursion = recursion
        self._segmentation = segmentation
        self._extensions = self.__parse_extensions(extensions)
        pass

    def __parse_extensions(self, extensions: list[str | Extensions]) -> list[str]:
        return [x.value if type(x) != str else x for x in extensions]
