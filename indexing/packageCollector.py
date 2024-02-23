from indexing.BaseCollector import BaseCollector
from indexing.packageInfo import PackageInfo
from simplePipline.utils.utilities import log_debug


class PackageCollector(BaseCollector):
    def __init__(self, path, packageName):
        super().__init__()
        self.path = path
        self.package = PackageInfo(packageName)

    def collect(self):
        self.package.collect_classes(prefix=self.package.package_name,
                                              sourceCodePath=self.path)
        if self.package.classes:
            log_debug(f"task result id")
            return self.package.class_info()




