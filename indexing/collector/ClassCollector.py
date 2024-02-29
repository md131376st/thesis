from indexing.collector.BaseCollector import BaseCollector
from indexing.info.classInfo import ClassInfo
from indexing.utility import log_debug


class ClassCollector(BaseCollector):
    def __init__(self, path, collection_name):
        super().__init__()
        self.path = path
        class_name = str(collection_name).split(".")[-1]
        self.class_info = ClassInfo(class_name, path)
        self.class_info.set_qualified_class_name(collection_name, exact=True)

    def collect(self):
        detail = self.class_info.get_class_info()
        log_debug(f"[CLASSCOLLECTOR] parser returnValue: {detail}")
        if detail is not None:
            self.class_info.update_class_details(detail)
            return self.class_info.get_method_info()
