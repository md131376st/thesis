from enum import Enum


class IndexLevelTypes(Enum):
    CODEBASE = "codebase"
    PACKAGE = "package"
    CLASS = "class"


class QueryTypes(Enum):
    ALL = "all"
    CODEBASE = "codebase"
    PACKAGE = "package"
    CLASS = "class"
