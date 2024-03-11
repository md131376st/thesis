import json
from celery import chain, group

from indexing.models import PackageRecord
from indexing.utility import packet_info_call, log_debug, filter_empty_values, open_ai_description_generator, \
    clean_description_json_string

from indexing.info.baseInfo import BaseInfo
from indexing.prompt import package_description_system_prompt
from mongoengine import ValidationError, NotUniqueError, OperationError


class PackageInfo(BaseInfo):
    def __init__(self, package_name, code_base_name=""):
        super().__init__()
        self.package_name = package_name
        self.classes = []  # List to store ClassInfo instances
        self.description = ""
        self.code_base_name = code_base_name
        self.technical_questions = []
        self.functional_questions = []

    def to_dict(self):
        return {
            "package_name": self.package_name,
            "classes": [class_.to_dict() for class_ in self.classes],
            "description": self.description,
            "code_base_name": self.code_base_name
        }

    @classmethod
    def from_dict(cls, data):
        from indexing.info.classInfo import ClassInfo
        instance = cls(data["package_name"], data["code_base_name"])
        instance.classes = [ClassInfo.from_dict(ci_data) for ci_data in data["classes"]]
        instance.description = data["description"]
        return instance

    def collect_classes(self, prefix, sourceCodePath):
        from indexing.info.classInfo import ClassInfo
        log_debug(f"[COLLECT_CLASSES] class prefix: {prefix}")
        data = packet_info_call(prefix=prefix, sourceCodePath=sourceCodePath)
        if "classNames" in data and data["classNames"] is not None:
            for class_name in data["classNames"]:
                class_info = ClassInfo(class_name, sourceCodePath, self.code_base_name)
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

    def get_description(self):
        return self.description

    def get_meta_data(self):
        data = {
            "package_name": self.package_name,
            "classes": json.dumps([cls.class_name for cls in self.classes]),
            "code_base_name": self.code_base_name
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

    def generate_description(self) -> dict | None:
        max_retry = 3
        i = 0
        while i < max_retry:
            description = open_ai_description_generator(
                system_prompt=package_description_system_prompt,
                content=self.description_package_prompt_data(),
                sender=self.package_name
            )
            log_debug(f"[PackageInfo_generate_description] description: {type(description)}")
            try:
                description = clean_description_json_string(description)
                log_debug(f"[PackageInfo_generate_description] CLEANED DESCRIPTION {description}")
                description_json = json.loads(description)
                return description_json
            except json.JSONDecodeError:
                log_debug(f"[PackageInfo_generate_description] not valid json: {description}")
            i += 1
        return None

    def store_in_mongo_db(self):
        try:
            log_debug(f"[STORE_IN_DB_Package] start storing {self.package_name}")
            record = PackageRecord(
                name=self.package_name,
                description=self.description,
                technical_questions=self.technical_questions,
                functional_questions=self.functional_questions,
                metadata=self.get_meta_data()
            )
            record.save()
            log_debug(f"[STORE_IN_DB_Package] finish storing {self.package_name}")
        except ValidationError as e:
            # Handle validation errors, e.g., missing fields or incorrect data types
            log_debug(f"[ERROR][STORE_IN_DB_Package]Validation error while saving record: {e}")
            # Optionally, log the error or take other actions like sending a notification
        except NotUniqueError as e:
            # Handle errors related to unique constraints being violated
            log_debug(f"[ERROR][STORE_IN_DB_Package]Unique constraint violated while saving record: {e}")
            # Optionally, log the error or take other actions
        except OperationError as e:
            # Handle general operation errors, e.g., issues with the connection to MongoDB
            log_debug(f"[ERROR][STORE_IN_DB_Package]Operation error while saving record: {e}")
            # Optionally, log the error or take other actions
        except Exception as e:
            # Handle any other exceptions that were not caught by the specific handlers above
            log_debug(f"[ERROR][STORE_IN_DB_Package]An unexpected error occurred while saving record: {e}")
            # Optionally, log the error or take other actions

    def __repr__(self):
        return f"{self.package_name}', classes={self.classes})"
