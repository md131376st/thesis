from enum import Enum


class ChunkType(Enum):
    TEXT = "txt"
    CODE = "code"
    LAMA_INDEX = "llm_index"


class IndexLevelTypes(Enum):
    CODEBASE = "codebase"
    PACKAGE = "package"
    CLASS = "class"
