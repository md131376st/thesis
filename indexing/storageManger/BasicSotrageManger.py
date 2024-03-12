from abc import ABC

from indexing.utility import log_debug, add_string_to_file


class BasicStorageManger(ABC):
    def __init__(self):
        pass

    def to_dict(self):
        pass

    @classmethod
    def from_dict(cls, data):
        pass

    def store(self):
        pass
