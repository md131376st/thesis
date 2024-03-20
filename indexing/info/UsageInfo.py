import json

from indexing.info.BaseInfo import BaseInfo


class UsageInfo(BaseInfo):

    def __init__(self):
        super().__init__()
        self.code = None
        self.is_field_usage = None
        self.methods = None
        self.qualified_class_name = None

    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.qualified_class_name = data['qualifiedClassName']
        instance.methods = data['methods']
        instance.is_field_usage = data['isFieldUsage']
        instance.code = data['code']
        return instance

    def to_dict(self):
        return {
            'qualifiedClassName': self.qualified_class_name,
            'methods': self.methods,
            'isFieldUsage': self.is_field_usage,
            'code': self.code
        }

    def get_meta_data(self):
        return {
            'qualifiedClassName': self.qualified_class_name,
            'methods': json.dumps(self.methods),
            'isFieldUsage': self.is_field_usage
        }

    def generate_description(self):
        pass
