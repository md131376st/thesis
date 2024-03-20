from celery import group

from indexing.collector.BaseCollector import BaseCollector
from indexing.info.PackageInfo import PackageInfo
from indexing.tasks import collect_package_class_info
from indexing.utility import packet_info_call, log_debug
from indexing.ragHandler import RagHandler


class CodeBaseCollector(BaseCollector):
    def __init__(self, path, codebase_name, packagePrefix=None):
        super().__init__()
        self.packages = []
        self.sourceCodePath = path
        self.packagePrefix = packagePrefix
        self.codebase_name = codebase_name

    def collect(self):
        self.collect_package_info(self.codebase_name)
        if self.packages:
            log_debug("Start Indexing")
            package_tasks = [
                collect_package_class_info.s(packageInfo=package.to_dict(), sourceCodePath=self.sourceCodePath)
                for package in self.packages]

            workflow = group(package_tasks)
            result = workflow.apply_async()
            return result.id
        pass

    def set_packages(self, packages):
        self.packages = packages

    def collect_package_info(self, codebase_name):
        data = packet_info_call(prefix=self.packagePrefix, sourceCodePath=self.sourceCodePath)
        # if data is not None:
        #     package_info = PackageInfo(data["packageName"])
        #
        #     for class_name in data["classNames"]:
        #         class_info = ClassInfo(class_name, self.sourceCodePath)
        #         class_info.set_qualified_class_name(data["packageName"])
        #         details = self.get_methods_for_class(class_name, package_info.package_name)
        #         if details is not None:
        #             class_info.update_class_details(details)
        #             package_info.add_class(class_info)
        #     if len(package_info.classes) != 0:
        #         self.packages.append(package_info)
        for sub_package_name in data["subPackageNames"]:
            self.packages.append(PackageInfo(sub_package_name, code_base_name=codebase_name))
            # print(sub_package_name)
            # self.collect_package_info(sub_package_name)

    def get_collected_data(self):
        return self.packages

    def get_class_names_with_packages(self):
        class_with_packages = []
        for package in self.packages:
            for class_info in package.classes:
                full_name = f"{package.package_name}.{class_info.class_name}"
                class_with_packages.append(full_name)
        return class_with_packages

    def generate_codebase_embeddings(self):
        chunks = []
        metadata = []

        for package in self.packages:
            chunks.append(
                {
                    "text": package.get_description()
                }
            )
            metadata.append(package.get_meta_data())
        else:
            log_debug(f"[ERROR] empty class function")
        collection_name = "MyCodeBase"
        collection_metadata = {}
        RagHandler.rag_store(chunks, metadata, collection_name, collection_metadata)

    def get_meta_data(self):
        metadata = {
            "package_number": len(self.packages)
        }
        return metadata
