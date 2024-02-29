import json
import os

import requests
from celery import chain, group

from indexing.utility import packet_info_call, log_debug, filter_empty_values, open_ai_description_generator

from indexing.info.baseInfo import BaseInfo
from indexing.prompt import Create_Tech_functional_package


class PackageInfo(BaseInfo):
    def __init__(self, package_name):
        super().__init__()
        self.package_name = package_name
        self.classes = []  # List to store ClassInfo instances
        self.description = ""

    def to_dict(self):
        return {
            "package_name": self.package_name,
            "classes": [class_.to_dict() for class_ in self.classes],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        from indexing.info.classInfo import ClassInfo
        instance = cls(data["package_name"])
        instance.classes = [ClassInfo.from_dict(ci_data) for ci_data in data["classes"]]
        instance.description = data["description"]
        return instance

    def collect_classes(self, prefix, sourceCodePath):
        from indexing.info.classInfo import ClassInfo
        log_debug(f"[COLLECT_CLASSES] class prefix: {prefix}")
        data = packet_info_call(prefix=prefix, sourceCodePath=sourceCodePath)
        if data["classNames"] is not None:
            for class_name in data["classNames"]:
                class_info = ClassInfo(class_name, sourceCodePath)
                class_info.set_qualified_class_name(data["packageName"])
                details = class_info.get_class_info()
                if details is not None:
                    class_info.update_class_details(details)
                    self.add_class(class_info)
        else:
            log_debug(f"[ERROR] empty package")

    def class_info(self, packageInfo_data):
        from indexing.tasks import collect_class_info, process_package_results
        groups = [collect_class_info.s(classinfo=classinfo.to_dict()) for classinfo in self.classes]
        workflow = chain(
            group(*groups) |
            process_package_results.s(packageInfo_data=packageInfo_data)

        )
        result = workflow.apply_async()

        return result.id

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def get_meta_data(self):
        data = {
            "package_name": self.package_name,
            "classes": json.dumps([cls.class_name for cls in self.classes]),
        }
        return filter_empty_values(data)

    def add_class(self, class_info):
        self.classes.append(class_info)

    def generate_package_embeddings(self):
        from indexing.info.classInfo import rag_store
        chunks = []
        metadata = []
        if self.classes:
            for class_ in self.classes:
                chunks.append(
                    {
                        "text": class_.get_description()
                    }
                )
                metadata.append(class_.get_meta_data())
            collection_metadata = self.get_meta_data()
            rag_store(chunks, metadata, self.package_name, collection_metadata)
        else:
            log_debug(f"[ERROR] empty package")

    def generate_codebase_embeddings(self):
        from indexing.info.classInfo import rag_store
        if self.description:
            collection_name = "MyCodeBase"
            chunks = [{
                "text": self.description
            }]
            collection_metadata = {}
            rag_store([
                {
                    "text": self.description
                }
            ], [
                self.get_meta_data()
            ], collection_name, collection_metadata)

    def description_package_prompt_data(self):
        description = f"Package name : {self.package_name} \n"
        for classinfo in self.classes:
            description += f"{classinfo.get_description()} \n"
        return description

    def generate_description(self):
        return open_ai_description_generator(system_prompt=Create_Tech_functional_package,
                                             content=self.description_package_prompt_data(),
                                             sender=self.package_name
                                             )

    def __repr__(self):
        return f"{self.package_name}', classes={self.classes})"
