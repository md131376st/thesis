from celery import shared_task

from indexing.classInfo import ClassInfo
from simplePipline.utils.utilities import log_debug


class ClassCollector:
    def __init__(self, path, collection_name):
        self.path = path
        class_name = str(collection_name).split(".")[-1]
        self.class_info = ClassInfo(class_name, path)
        self.class_info.set_qualified_class_name(collection_name, exact=True)

    def get_class_info(self):
        detail = self.class_info.get_methods_for_class()
        log_debug(detail)
        if detail is not None:
            self.class_info.update_class_details(detail)
            return self.class_info.method_info()
            # self.class_info.generate_class_embedding()
        # else:
        #     log_debug("empty class")
