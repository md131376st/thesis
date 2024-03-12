from indexing.collector.BaseCollector import BaseCollector
from indexing.info.ClassInfo import ClassInfo


class ClassCollector(BaseCollector):
    def __init__(self, path, collection_name, codebase_name):
        super().__init__()
        self.path = path
        class_name = str(collection_name).split(".")[-1]

        self.class_info = ClassInfo(class_name, path, codebase_name)
        self.class_info.set_qualified_class_name(collection_name, exact=True)

    def collect(self):
        detail = self.class_info.get_class_info()
        if detail is not None:
            self.class_info.update_class_details(detail)
            return self.class_info.get_method_info()
