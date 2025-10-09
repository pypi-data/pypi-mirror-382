from enum import Enum


class Document(Enum):
    TXT = ".txt"
    DOC = ".doc"
    DOCX = ".docx"
    PDF = ".pdf"
    ODT = ".odt"
    RTF = ".rtf"


class Spreadsheet(Enum):
    XLS = ".xls"
    XLSX = ".xlsx"
    CSV = ".csv"
    ODS = ".ods"
    PPT = ".ppt"
    PPTX = ".pptx"
    ODP = ".odp"


class Image(Enum):
    JPG = ".jpg"
    JPEG = ".jpeg"
    PNG = ".png"
    GIF = ".gif"
    BMP = ".bmp"
    TIFF = ".tiff"
    TIF = ".tif"
    SVG = ".svg"


class Audio(Enum):
    MP3 = ".mp3"
    WAV = ".wav"
    FLAC = ".flac"
    AAC = ".aac"
    OGG = ".ogg"


class Video(Enum):
    MP4 = ".mp4"
    AVI = ".avi"
    MKV = ".mkv"
    MOV = ".mov"
    WMV = ".wmv"


class Code(Enum):
    C = ".c"
    CPP = ".cpp"
    H = ".h"
    CS = ".cs"
    JAVA = ".java"
    PY = ".py"
    JS = ".js"
    HTML = ".html"
    HTM = ".htm"
    CSS = ".css"
    PHP = ".php"
    SQL = ".sql"
    SH = ".sh"


class Archive(Enum):
    ZIP = ".zip"
    RAR = ".rar"
    SEVENZ = ".7z"
    TAR = ".tar"
    GZ = ".gz"


class SystemApp(Enum):
    EXE = ".exe"
    MSI = ".msi"
    APK = ".apk"
    DMG = ".dmg"
    ISO = ".iso"


class Extensions:
    Document = Document
    Spreadsheet = Spreadsheet
    Image = Image
    Audio = Audio
    Video = Video
    Code = Code
    Archive = Archive
    SystemApp = SystemApp

    @staticmethod
    def all(enum_cls: Enum) -> list[str]:
        return [e.value for e in enum_cls]
