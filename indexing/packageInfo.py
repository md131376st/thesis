import json

from simplePipline.utils.utilities import filter_empty_values


class PackageInfo:
    def __init__(self, package_name):
        self.package_name = package_name
        self.classes = []  # List to store ClassInfo instances
        self.description = ""

    def get_meta_data(self):
        data = {
            "package_name": self.package_name,
            "classes": json.dumps([cls.class_name for cls in self.classes]),
            "description": self.description
        }
        return filter_empty_values(data)

    def add_class(self, class_info):
        self.classes.append(class_info)

    def __repr__(self):
        return f"{self.package_name}', classes={self.classes})"
