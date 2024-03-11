from abc import ABC


class BaseInfo(ABC):
    def __init__(self):
        pass

    def to_dict(self):
        pass

    @classmethod
    def from_dict(cls, data):
        pass

    def get_meta_data(self) -> dict:
        pass

    def generate_description(self):
        pass
