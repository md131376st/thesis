import json

import requests
from celery import group
from mongoengine import ValidationError, NotUniqueError, OperationError

from fileService import settings
from indexing.info.BaseInfo import BaseInfo
from indexing.info.MethodInfo import MethodInfo
from indexing.info.UsageInfo import UsageInfo
from indexing.models import ClassRecord
from indexing.prompt import class_description_system_prompt

from indexing.tasks import collect_method_info
from indexing.types import ClassTYPES
from indexing.utility import log_debug, filter_empty_values, rag_store, open_ai_description_generator, \
    clean_description_json_string


class ClassInfo(BaseInfo):
    def __init__(self, class_name, path, codebase_name):
        super().__init__()
        self.sourceCodePath = path
        self.class_name = class_name
        self.codebase_name = codebase_name
        self.qualified_class_name = None
        self.packageName = None
        self.code = None
        self.extended_class = None
        self.type = None
        self.fields = []
        self.methods = []
        self.method_infos = []
        self.method_names = []
        self.imports = []
        self.usages = None
        self.annotations = []
        self.implemented_classes = []
        self.indirect_inheritances = []
        self.description = ""
        self.technical_questions = []
        self.functional_questions = []

    def to_dict(self):
        return {
            "sourceCodePath": self.sourceCodePath,
            "class_name": self.class_name,
            "codebase_name": self.codebase_name,
            "qualified_class_name": self.qualified_class_name,
            "packageName": self.packageName,
            "code": self.code,
            "extended_class": self.extended_class,
            "type": self.type,
            "fields": self.fields,
            "methods": self.methods,
            "method_infos": [method_info.to_dict() for method_info in self.method_infos],
            "method_names": self.method_names,
            "imports": self.imports,
            "usages": [usage.to_dict() for usage in self.usages],
            "annotations": self.annotations,
            "implemented_classes": self.implemented_classes,
            "indirect_inheritances": self.indirect_inheritances,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(data["class_name"], data["sourceCodePath"], data["codebase_name"])
        instance.qualified_class_name = data["qualified_class_name"]
        instance.codebase_name = data["codebase_name"]
        instance.packageName = data["packageName"]
        instance.code = data["code"]
        instance.extended_class = data["extended_class"]
        instance.type = data["type"]
        instance.fields = data["fields"]
        instance.methods = data["methods"]
        instance.method_infos = [MethodInfo.from_dict(mi_data) for mi_data in data["method_infos"]]
        instance.method_names = data["method_names"]
        instance.imports = data["imports"]
        instance.usages = [UsageInfo.from_dict(x) for x in data["usages"]]
        instance.annotations = data["annotations"]
        instance.implemented_classes = data["implemented_classes"]
        instance.indirect_inheritances = data["indirect_inheritances"]
        instance.description = data["description"]
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
            "packageName": self.packageName,
            "code": self.code,
            "extended_class": self.extended_class,
            "type": self.type,
            "fields": json.dumps(self.fields) if isinstance(self.fields, list) else self.fields,
            "methods": json.dumps(self.methods) if isinstance(self.methods, list) else self.methods,
            "imports": json.dumps(self.imports) if isinstance(self.imports, list) else self.imports,
            "usages": json.dumps([x.get_meta_data() for x in self.usages]),
            "annotations": json.dumps(self.annotations) if isinstance(self.annotations, list) else self.annotations,
            "implemented_classes": json.dumps(self.implemented_classes) if isinstance(
                self.implemented_classes,
                list) else self.implemented_classes,
            "indirect_inheritances": json.dumps(self.indirect_inheritances) if isinstance(
                self.implemented_classes,
                list) else self.indirect_inheritances
        }
        return filter_empty_values(data)

    def set_qualified_class_name(self, package_name, exact=False):
        if exact:
            self.qualified_class_name = package_name
        else:
            self.qualified_class_name = f"{package_name}.{self.class_name}"

    def fill_class_details(self,
                           package_name,
                           code,
                           extended_class,
                           type,
                           fields,
                           methods,
                           method_names,
                           imports,
                           usages,
                           annotations,
                           implemented_classes,
                           indirectInheritances
                           ):
        self.packageName = package_name
        self.code = code
        self.extended_class = extended_class
        self.type = type
        self.fields = fields
        self.methods = methods
        self.method_names = method_names
        self.imports = imports
        self.usages = [UsageInfo.from_dict(usage_data) for usage_data in usages]
        self.annotations = annotations
        self.implemented_classes = implemented_classes
        self.indirect_inheritances = indirectInheritances

    def __repr__(self):
        return f"ClassInfo {self.qualified_class_name}')"

    def get_package_name(self):
        return '.'.join(self.qualified_class_name.split('.')[:-1])

    def get_simple_class_name(self):
        return self.qualified_class_name.split('.')[-1]

    def update_class_details(self, details):
        self.fill_class_details(
            details['packageName'],
            details['code'],
            details['extendedClass'],
            details['type'],
            details['fields'],
            details['methods'],
            details['methodsNames'],
            details['imports'],
            details['usages'],
            details['annotations'],
            details['implementedClasses'],
            details['indirectInheritances']
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

    def description_class_type_class_prompt_data(self):
        prompt_data = f"""
CLASS: {self.class_name}\n
CLASS ATTRIBUTES:\n{self.class_attributes()}\n
ANNOTATIONS:\n{"\n".join(self.annotations)}\n
METHODS DESCRIPTIONS:\n{self.get_class_methods_descriptions()}\n
USAGES:\n
{self.get_class_usages()}
EXTENDED CLASS:\n
{self.extended_class}
IMPLEMENTED CLASSES:\n
{"\n".join(self.implemented_classes)}\n
CLASS INDIRECT INHERITANCES:\n
{"\n".join(self.indirect_inheritances)}\n
"""
        return prompt_data

    def description_class_prompt_data(self):
        prompt_data = f"""
CLASS: {self.class_name}\n
CLASS ATTRIBUTES:\n{self.class_attributes()}\n
ANNOTATIONS:\n{"\n".join(self.annotations)}\n
CODE:\n{self.code}
USAGES:\n
{self.get_class_usages()}
EXTENDED CLASS:\n
{self.extended_class}
IMPLEMENTED CLASSES:\n
{"\n".join(self.implemented_classes)}\n
CLASS INDIRECT INHERITANCES:\n
{"\n".join(self.indirect_inheritances)}\n
"""
        return prompt_data

    def generate_description(self) -> dict | None:
        max_retry = 3
        i = 0
        while i < max_retry:
            if self.type == ClassTYPES.CLASS.value:
                description = open_ai_description_generator(
                    system_prompt=class_description_system_prompt,
                    content=self.description_class_type_class_prompt_data(),
                    sender=self.class_name
                )
            else:
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
                log_debug(f"[ERROR][ClassInfo_generate_description] not valid json: {description}")
            except TypeError as e:
                log_debug(f"[ERROR][ClassInfo_generate_description] TypeError: {type(e)}")
            finally:
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
