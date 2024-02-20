from enum import Enum


class ChunkType(Enum):
    TEXT = "txt"
    CODE = "code"
    LAMA_INDEX = "llm_index"
