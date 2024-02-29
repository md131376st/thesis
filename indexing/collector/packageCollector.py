from indexing.collector.BaseCollector import BaseCollector
from indexing.info.packageInfo import PackageInfo
from indexing.utility import log_debug


class PackageCollector(BaseCollector):
    def __init__(self, path, packageName):
        super().__init__()
        self.path = path
        self.package = PackageInfo(packageName)

    def collect(self):
        self.package.collect_classes(prefix=self.package.package_name,
                                     sourceCodePath=self.path)
        if self.package.classes:
            return self.package.class_info(self.package.to_dict())
