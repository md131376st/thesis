import json

from mongoengine.errors import ValidationError, NotUniqueError, OperationError

from indexing.info.baseInfo import BaseInfo
from indexing.models import MethodRecord
from indexing.prompt import method_description_system_prompt
from indexing.utility import filter_empty_values, open_ai_description_generator, log_debug, rag_store, \
    clean_description_json_string


def add_string_to_file(file_path, string_to_add):
    with open(file_path, 'a') as file:  # 'a' mode opens the file for appending
        file.write(string_to_add + '\n')


class MethodInfo(BaseInfo):

    def __init__(self, returnType, methodName, className, packageName, body, modifier, signature, parametersNames,
                 parametersTypes, annotations, exceptions, signatureDependencies, bodyDependencies,
                 signatureDependenciesWithPackage, bodyDependenciesWithPackage, imports, stringRepresentation,
                 dependencies_stubs,
                 description=""):
        super().__init__()
        self.returnType = returnType
        self.methodName = methodName
        self.className = className
        self.packageName = packageName
        self.body = body
        self.modifier = modifier
        self.signature = signature
        self.parametersNames = parametersNames
        self.parametersTypes = parametersTypes
        self.annotations = annotations
        self.exceptions = exceptions
        self.signatureDependencies = signatureDependencies
        self.bodyDependencies = bodyDependencies
        self.signatureDependenciesWithPackage = signatureDependenciesWithPackage
        self.bodyDependenciesWithPackage = bodyDependenciesWithPackage
        self.imports = imports
        self.stringRepresentation = stringRepresentation
        self.dependencies_stubs = dependencies_stubs
        self.description = description
        self.technical_questions = []
        self.functional_questions = []

    def to_dict(self):
        return {
            "returnType": self.returnType,
            "methodName": self.methodName,
            "className": self.className,
            "packageName": self.packageName,
            "body": self.body,
            "modifier": self.modifier,
            "signature": self.signature,
            "parametersNames": self.parametersNames,  # Assuming these are serializable as is
            "parametersTypes": self.parametersTypes,
            "annotations": self.annotations,
            "exceptions": self.exceptions,
            "signatureDependencies": self.signatureDependencies,
            "bodyDependencies": self.bodyDependencies,
            "signatureDependenciesWithPackage": self.signatureDependenciesWithPackage,
            "bodyDependenciesWithPackage": self.bodyDependenciesWithPackage,
            "imports": self.imports,
            "stringRepresentation": self.stringRepresentation,
            "dependenciesStubs": self.dependencies_stubs,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data, isDescription=True):
        return cls(
            returnType=data["returnType"],
            methodName=data["methodName"],
            className=data["className"],
            packageName=data["packageName"],
            body=data["body"],
            modifier=data["modifier"],
            signature=data["signature"],
            parametersNames=data["parametersNames"],
            parametersTypes=data["parametersTypes"],
            annotations=data["annotations"],
            exceptions=data["exceptions"],
            signatureDependencies=data["signatureDependencies"],
            bodyDependencies=data["bodyDependencies"],
            signatureDependenciesWithPackage=data["signatureDependenciesWithPackage"],
            bodyDependenciesWithPackage=data["bodyDependenciesWithPackage"],
            imports=data["imports"],
            stringRepresentation=data["stringRepresentation"],
            dependencies_stubs=data["dependenciesStubs"],
            description=data["description"] if isDescription else "",
        )

    def __repr__(self):
        return (f"methodName='{self.methodName}',"
                f" returnType='{self.returnType}',"
                f" className='{self.className}',"
                f" packageName='{self.packageName}')")

    def get_meta_data(self):
        data = {
            "returnType": self.returnType,
            "methodName": self.methodName,
            "className": self.className,
            "packageName": self.packageName,
            "body": self.body,
            "modifier": self.modifier,
            "signature": self.signature,
            "parametersNames": json.dumps(self.parametersNames) if isinstance(self.parametersNames,
                                                                              list) else self.parametersNames,
            "parametersTypes": json.dumps(self.parametersTypes) if isinstance(self.parametersTypes,
                                                                              list) else self.parametersTypes,
            "annotations": json.dumps(self.annotations) if isinstance(self.annotations, list) else self.annotations,
            "exceptions": json.dumps(self.exceptions) if isinstance(self.exceptions, list) else self.exceptions,
            "signatureDependencies": json.dumps(self.signatureDependencies) if isinstance(self.signatureDependencies,
                                                                                          list) else self.signatureDependencies,
            "bodyDependencies": json.dumps(self.bodyDependencies) if isinstance(self.bodyDependencies,
                                                                                list) else self.bodyDependencies,
            "signatureDependenciesWithPackage": json.dumps(self.signatureDependenciesWithPackage) if isinstance(
                self.signatureDependenciesWithPackage, list) else self.signatureDependenciesWithPackage,
            "bodyDependenciesWithPackage": json.dumps(self.bodyDependenciesWithPackage) if isinstance(
                self.bodyDependenciesWithPackage, list) else self.bodyDependenciesWithPackage,
            "imports": json.dumps(self.imports) if isinstance(self.imports, list) else self.imports,
            "stringRepresentation": self.stringRepresentation,
            "dependenciesStubs": json.dumps(self.dependencies_stubs) if isinstance(self.dependencies_stubs,
                                                                                   list) else self.dependencies_stubs,
        }
        return filter_empty_values(data)

    def set_description(self):
        gpt_json = self.generate_description()
        self.description = gpt_json.get("description")
        self.technical_questions = gpt_json.get("technical_questions")
        self.functional_questions = gpt_json.get("functional_questions")

        log_debug(f"[MethodInfo_set_description] class prefix: {self.methodName}")
        if self.description is None:
            log_debug(f"[MethodInfo_set_description] description exists class prefix: {self.methodName}")
            add_string_to_file("retry_methodName.txt", f"{self.methodName}")

    def get_description(self):
        return self.description

    def get_methodName(self):
        return self.methodName

    def generate_description(self) -> dict | None:
        user_prompt = f"""
        METHOD BODY:
        {self.body}
        
        DEPENDENCIES STUBS:
        {self.dependencies_stubs}
        """

        max_retry = 3
        i = 0
        while i < max_retry:
            description = open_ai_description_generator(
                system_prompt=method_description_system_prompt,
                content=user_prompt,
                sender=self.methodName
            )
            log_debug(f"[MethodInfo_generate_description] description: {type(description)}")
            try:
                description = clean_description_json_string(description)
                log_debug(f"CLEANED DESCRIPTION {description}")
                description_json = json.loads(description)
                return description_json
            except json.JSONDecodeError:
                log_debug(f"[MethodInfo_generate_description] not valid json: {description}")
            i += 1
        return None

    def store_in_mongo_db(self):
        try:
            log_debug(f"[STORE_IN_DB_Method] start storing {self.methodName}")
            record = MethodRecord(
                name=self.methodName,
                description=self.description,
                qualified_class_name=f"{self.packageName}.{self.className}",
                package_name=self.packageName,
                technical_questions=self.technical_questions,
                functional_questions=self.functional_questions,
                metadata=self.get_meta_data()
            )
            record.save()
            log_debug(f"[STORE_IN_DB_Method] finish storing {self.methodName}")
        except ValidationError as e:
            # Handle validation errors, e.g., missing fields or incorrect data types
            log_debug(f"[ERROR][STORE_IN_DB_Method]Validation error while saving record: {e}")
            # Optionally, log the error or take other actions like sending a notification
        except NotUniqueError as e:
            # Handle errors related to unique constraints being violated
            log_debug(f"[ERROR][STORE_IN_DB_Method]Unique constraint violated while saving record: {e}")
            # Optionally, log the error or take other actions
        except OperationError as e:
            # Handle general operation errors, e.g., issues with the connection to MongoDB
            log_debug(f"[ERROR][STORE_IN_DB_Method]Operation error while saving record: {e}")
            # Optionally, log the error or take other actions
        except Exception as e:
            # Handle any other exceptions that were not caught by the specific handlers above
            log_debug(f"[ERROR][STORE_IN_DB_Method]An unexpected error occurred while saving record: {e}")
            # Optionally, log the error or take other actions

    def generate_method_embedding(self, class_metadata):
        log_debug(
            f"[GENERATE_METHOD_EMBEDDING] start embeddings method name: {self.methodName} class name: {self.className}")
        chunks = []
        metadata = []
        if self.description:
            chunks.append({
                "text": self.description
            })
            metadata.append(self.get_meta_data())
            qualified_class_name = self.packageName + '.' + self.className
            result = rag_store(chunks, metadata, qualified_class_name, class_metadata)
            if 'error' in result:
                log_debug(
                    f"[ERROR][GENERATE_METHOD_EMBEDDING] rag store failed method {self.methodName} class {self.className} error: {result['error']}")
            else:
                log_debug(
                    f"[GENERATE_METHOD_EMBEDDING] finish embeddings method name: {self.methodName} class name: {self.className}")
        else:
            log_debug(
                f"[ERROR][GENERATE_METHOD_EMBEDDING] empty description for method {self.methodName} class {self.className}")
