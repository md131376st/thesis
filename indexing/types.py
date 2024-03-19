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


class DescriptionType(Enum):
    CODEBASE = "codebase"
    PACKAGE = "package"
    CLASS = "class"
    METHOD = "method"


class StoreLevelTypes(Enum):
    CODEBASE = "codebase"
    PACKAGE = "package"
    CLASS = "class"
    OBJECT = "method"


class ClassTYPES(Enum):
    CLASS = "CLASS"
    ENUM = "ENUM"
    INTERFACE = "INTERFACE"
    RECORD = "RECORD"


class TypeConverter:
    regex = '(codebase|package|class|method)'

    def to_python(self, value: str):
        return DescriptionType(value)

    def to_url(self, value: DescriptionType):
        return value.value
