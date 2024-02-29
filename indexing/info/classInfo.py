import json

import requests
from celery import group, chain

from fileService import settings
from indexing.info.baseInfo import BaseInfo
from indexing.info.methodInfo import MethodInfo
from indexing.prompt import Create_Tech_functional_class

from indexing.tasks import collect_method_info, class_embedding_handler
from indexing.utility import log_debug, filter_empty_values, rag_store, open_ai_description_generator


class ClassInfo(BaseInfo):
    def __init__(self, class_name, path):
        super().__init__()
        self.sourceCodePath = path
        self.class_name = class_name
        self.qualified_class_name = None
        self.code = None
        self.implemented_class = None
        self.extended_class = None
        self.fields = []
        self.methods = []
        self.method_infos = []
        self.method_names = []
        self.packageName = None
        self.description = ""

    def to_dict(self):
        return {
            "sourceCodePath": self.sourceCodePath,
            "class_name": self.class_name,
            "qualified_class_name": self.qualified_class_name,
            "code": self.code,
            "implemented_class": self.implemented_class,
            "extended_class": self.extended_class,
            "fields": self.fields,
            "methods": self.methods,
            "method_infos": [method_info.to_dict() for method_info in self.method_infos],
            "method_names": self.method_names,
            "description": self.description,
            "packageName": self.packageName,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(data["class_name"], data["sourceCodePath"])
        instance.qualified_class_name = data["qualified_class_name"]
        instance.code = data["code"]
        instance.implemented_class = data["implemented_class"]
        instance.extended_class = data["extended_class"]
        instance.fields = data["fields"]
        instance.methods = data["methods"]
        instance.method_infos = [MethodInfo.from_dict(mi_data) for mi_data in data["method_infos"]]
        instance.method_names = data["method_names"]
        instance.description = data["description"]
        instance.packageName = data["packageName"]
        return instance

    def get_class_info(self) -> dict | None:
        try:

            response = requests.get(
                f"{settings.PARSER_URL}classInfo/{self.qualified_class_name}",
                headers={
                    "sourceCodePath": self.sourceCodePath
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                log_debug(
                    f"[ERROR] Failed to retrieve classinfo  for {self.qualified_class_name} with status code {response.status_code}")
                return None
        except Exception as e:
            log_debug(f"[ERROR] An error while classinfo   for {self.qualified_class_name}: {e}")
            return None

    def get_meta_data(self):
        data = {
            "class_name": self.class_name,
            "qualified_class_name": self.qualified_class_name,
            "code": self.code,
            "implemented_class": self.implemented_class,
            "extended_class": self.extended_class,
            "fields": json.dumps(self.fields) if isinstance(self.fields, list) else self.fields,
            "methods": json.dumps(self.methods) if isinstance(self.methods, list) else self.methods,
            "description": self.description,
            "packageName": self.packageName
        }
        return filter_empty_values(data)

    def set_qualified_class_name(self, package_name, exact=False):
        if exact:
            self.qualified_class_name = package_name
        else:
            self.qualified_class_name = f"{package_name}.{self.class_name}"

    def fill_class_details(self, code, implemented_class, extended_class, fields, methods, method_names, packageName):
        self.code = code
        self.implemented_class = implemented_class
        self.extended_class = extended_class
        self.fields = fields
        self.methods = methods
        self.method_names = method_names
        self.packageName = packageName

    def __repr__(self):
        return f"ClassInfo {self.qualified_class_name}')"

    def get_package_name(self):
        return '.'.join(self.qualified_class_name.split('.')[:-1])

    def get_simple_class_name(self):
        return self.qualified_class_name.split('.')[-1]

    def update_class_details(self, details):
        self.fill_class_details(details['code'],
                                details['implementedClass'],
                                details['extendedClass'],
                                details['fields'],
                                details['methods'],
                                details['methodsNames'],
                                details['packageName'])

    def get_method_info(self):

        workflow = chain(
            group(
                collect_method_info.s(
                    method_name=method_name,
                    qualified_class_name=self.qualified_class_name,
                    source_code_path=self.sourceCodePath
                ) for method_name in self.method_names),
            class_embedding_handler.s(classinfo=self.to_dict())
        )
        results = workflow.apply_async()
        return results.id

    def generate_class_index(self):
        for method in self.method_infos:
            method.set_description()

    def generate_class_embedding(self):
        log_debug(f"[GENERATE_CLASS_EMBEDDING] start class name: {self.class_name} ")
        chunks = []
        metadata = []
        if self.method_infos:
            for method in self.method_infos:
                if method.get_description():
                    chunks.append(
                        {
                            "text": method.get_description()
                        }
                    )
                    metadata.append(method.get_meta_data())
            collection_metadata = self.get_meta_data()
            rag_store(chunks, metadata, self.qualified_class_name, collection_metadata)
            log_debug(f"[GENERATE_CLASS_EMBEDDING] finish  embeddings class name: {self.class_name} ")

        else:
            log_debug(f"[ERROR] empty class function")

    def get_class_methods_descriptions(self):
        descriptions = ""
        for method in self.method_infos:
            descriptions += (f"Method name: {method.signature} \n"
                             f"{method.get_description()}\n")

        # Return the modified code
        return descriptions

    def description_class_prompt_data(self):
        prompt_data = (f"Class Name: {self.class_name} \n"
                       f"class attributes: {self.class_attributs()}\n"
                       f"methods:\n{self.get_class_methods_descriptions()}")
        return prompt_data

    def generate_description(self):
        return open_ai_description_generator(system_prompt=Create_Tech_functional_class,
                                             content=self.description_class_prompt_data(),
                                             sender=self.class_name
                                             )

    def set_description(self, description):
        self.description = description

    def class_attributs(self):
        fields = ""
        for field in self.fields:
            fields += f"\n{field} "
        return fields

    def get_description(self):
        return self.description
