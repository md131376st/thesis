import json

import requests
from celery import group
from mongoengine import ValidationError, NotUniqueError, OperationError

from fileService import settings
from indexing.info.baseInfo import BaseInfo
from indexing.info.methodInfo import MethodInfo
from indexing.info.usageInfo import UsageInfo
from indexing.models import ClassRecord
from indexing.prompt import class_description_system_prompt

from indexing.tasks import collect_method_info
from indexing.utility import log_debug, filter_empty_values, rag_store, open_ai_description_generator, \
    clean_description_json_string


class ClassInfo(BaseInfo):
    def __init__(self, class_name, path, codebase_name):
        super().__init__()
        self.sourceCodePath = path
        self.class_name = class_name
        self.codebase_name = codebase_name
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
        self.usages = []
        self.annotations = []
        self.technical_questions = []
        self.functional_questions = []

    def to_dict(self):
        return {
            "sourceCodePath": self.sourceCodePath,
            "class_name": self.class_name,
            "codebase_name": self.codebase_name,
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
            "usages": [usage.to_dict() for usage in self.usages],
            "annotations": self.annotations
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(data["class_name"], data["sourceCodePath"], data["codebase_name"])
        instance.qualified_class_name = data["qualified_class_name"]
        instance.codebase_name = data["codebase_name"]
        instance.code = data["code"]
        instance.implemented_class = data["implemented_class"]
        instance.extended_class = data["extended_class"]
        instance.fields = data["fields"]
        instance.methods = data["methods"]
        instance.method_infos = [MethodInfo.from_dict(mi_data) for mi_data in data["method_infos"]]
        instance.method_names = data["method_names"]
        instance.description = data["description"]
        instance.packageName = data["packageName"]
        instance.usages = [UsageInfo.from_dict(x) for x in data["usages"]]
        instance.annotations = data["annotations"]
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
            "codebase_name": self.codebase_name,
            "code": self.code,
            "implemented_class": self.implemented_class,
            "extended_class": self.extended_class,
            "fields": json.dumps(self.fields) if isinstance(self.fields, list) else self.fields,
            "methods": json.dumps(self.methods) if isinstance(self.methods, list) else self.methods,
            "description": self.description,
            "packageName": self.packageName,
            "usages": json.dumps([x.get_meta_data() for x in self.usages]),
            "annotations": json.dumps(self.annotations) if isinstance(self.annotations, list) else self.annotations
        }
        return filter_empty_values(data)

    def set_qualified_class_name(self, package_name, exact=False):
        if exact:
            self.qualified_class_name = package_name
        else:
            self.qualified_class_name = f"{package_name}.{self.class_name}"

    def fill_class_details(self, code, implemented_class, extended_class, fields, methods, method_names, package_name,
                           usages, annotations):
        self.code = code
        self.implemented_class = implemented_class
        self.extended_class = extended_class
        self.fields = fields
        self.methods = methods
        self.method_names = method_names
        self.packageName = package_name
        self.annotations = annotations
        self.usages = [UsageInfo.from_dict(usage_data) for usage_data in usages]

    def __repr__(self):
        return f"ClassInfo {self.qualified_class_name}')"

    def get_package_name(self):
        return '.'.join(self.qualified_class_name.split('.')[:-1])

    def get_simple_class_name(self):
        return self.qualified_class_name.split('.')[-1]

    def update_class_details(self, details):
        self.fill_class_details(
            details['code'],
            details['implementedClass'],
            details['extendedClass'],
            details['fields'],
            details['methods'],
            details['methodsNames'],
            details['packageName'],
            details['usages'],
            details['annotations']
        )

    def get_method_info(self):
        workflow = group(
            collect_method_info.s(
                method_name=method_name,
                qualified_class_name=self.qualified_class_name,
                source_code_path=self.sourceCodePath,
                class_metadata=self.get_meta_data()
            ) for method_name in self.method_names
        )
        results = workflow.apply_async()
        return results.id

    def generate_class_index(self):
        for method in self.method_infos:
            method.set_description("MethodInfo_set_description", method.methodName)

    def generate_class_embedding(self):
        log_debug(f"[GENERATE_CLASS_EMBEDDING] start class name: {self.class_name} ")
        chunks = [
            {
                "text": self.description
            }
        ]
        collection_metadata = {
            "code_base_name": self.codebase_name,
            "packageName": self.packageName
        }

        result = rag_store(
            chunks=chunks,
            metadata=[self.get_meta_data()],
            collection_name=self.packageName,
            collection_metadata=collection_metadata
        )
        if "error" in result:
            log_debug(f"[error] [GENERATE_CLASS_EMBEDDING]  ")
        log_debug(f"[GENERATE_CLASS_EMBEDDING] finish  embeddings class name: {self.class_name} ")

    def get_class_methods_descriptions(self):
        descriptions = ""
        for method in self.method_infos:
            descriptions += (f"Method name: {method.signature} \n"
                             f"{method.get_description()}\n")

        # Return the modified code
        return descriptions

    def get_class_usages(self) -> str:
        usages = []
        for usage in self.usages:
            methods_str = "\n\t".join(usage.methods)
            usages.append(f"{usage.qualified_class_name}:\n{methods_str}")
        result = "\n\n".join(usages) if len(usages) > 0 else "None"
        log_debug(f"CLASS USAGE: {result}")
        return result

    def description_class_prompt_data(self):
        prompt_data = f"""
CLASS: {self.class_name}\n
CLASS ATTRIBUTES:\n{self.class_attributes()}\n
ANNOTATIONS:\n{"\n".join(self.annotations)}\n
METHODS DESCRIPTIONS:\n{self.get_class_methods_descriptions()}\n
USAGES:\n
{self.get_class_usages()}
"""
        return prompt_data

    def generate_description(self) -> dict | None:
        max_retry = 3
        i = 0
        while i < max_retry:
            description = open_ai_description_generator(
                system_prompt=class_description_system_prompt,
                content=self.description_class_prompt_data(),
                sender=self.class_name
            )

            log_debug(f"[ClassInfo_generate_description] description: {type(description)}")
            try:
                description = clean_description_json_string(description)
                log_debug(f"[ClassInfo_generate_description] CLEANED DESCRIPTION {description}")
                description_json = json.loads(description)
                return description_json
            except json.JSONDecodeError:
                log_debug(f"[ClassInfo_generate_description] not valid json: {description}")
            i += 1
        return None

    def class_attributes(self):
        fields = ""
        for field in self.fields:
            fields += f"\n{field} "
        return fields

    def get_description(self):
        return self.description

    def store_in_mongo_db(self):
        try:
            log_debug(f"[STORE_IN_DB_Class] start storing {self.class_name}")
            record = ClassRecord(
                qualified_class_name=self.qualified_class_name,
                package_name=self.packageName,
                codebase_name=self.codebase_name,

                description=self.description,
                technical_questions=self.technical_questions,
                functional_questions=self.functional_questions,
                metadata=self.get_meta_data()
            )
            record.save()
            log_debug(f"[STORE_IN_DB_Class] finish storing {self.qualified_class_name}")
        except ValidationError as e:
            # Handle validation errors, e.g., missing fields or incorrect data types
            log_debug(f"[ERROR][STORE_IN_DB_Class]Validation error while saving record: {e}")
            # Optionally, log the error or take other actions like sending a notification
        except NotUniqueError as e:
            # Handle errors related to unique constraints being violated
            log_debug(f"[ERROR][STORE_IN_DB_Class]Unique constraint violated while saving record: {e}")
            # Optionally, log the error or take other actions
        except OperationError as e:
            # Handle general operation errors, e.g., issues with the connection to MongoDB
            log_debug(f"[ERROR][STORE_IN_DB_Class]Operation error while saving record: {e}")
            # Optionally, log the error or take other actions
        except Exception as e:
            # Handle any other exceptions that were not caught by the specific handlers above
            log_debug(f"[ERROR][STORE_IN_DB_Class]An unexpected error occurred while saving record: {e}")
            # Optionally, log the error or take other actions
