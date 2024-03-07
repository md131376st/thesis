import json
import re

from indexing.info.baseInfo import BaseInfo
from indexing.prompt import method_description_system_prompt
from indexing.utility import filter_empty_values, open_ai_description_generator, log_debug, rag_store


def add_string_to_file(file_path, string_to_add):
    with open(file_path, 'a') as file:  # 'a' mode opens the file for appending
        file.write(string_to_add + '\n')


def clean_description_json_string(description: str) -> str:
    if "```" not in description:
        return description
    begin_index = description.index("```json")
    end_index = description.rindex("```")
    return description[begin_index+7:end_index]


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
        self.description = self.generate_description()
        log_debug(f"[MethodInfo_set_description] class prefix: {self.methodName}")
        if self.description is None:
            log_debug(f"[MethodInfo_set_description] description exists class prefix: {self.methodName}")
            add_string_to_file("retry_methodName.txt", f"{self.methodName}")

    def get_description(self):
        return self.description

    def get_methodName(self):
        return self.methodName

    def generate_description(self) -> str | None:
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
                return description_json['description']
            except Exception:
                log_debug(f"[MethodInfo_generate_description] not valid json: {description}")
            i += 1
        return None
    
    def generate_method_embedding(self, class_metadata):
        log_debug(f"[GENERATE_METHOD_EMBEDDING] start embeddings method name: {self.methodName} class name: {self.className}")
        chunks = []
        metadata = []
        if self.description:
            chunks.append({
                "text": self.description
            })
            metadata.append(self.get_meta_data())
            qualified_class_name = self.packageName + '.' + self.className
            result = rag_store(chunks, metadata, qualified_class_name, class_metadata)
            if 'error' in  result:
                log_debug(f"[ERROR][GENERATE_METHOD_EMBEDDING] rag store failed method {self.methodName} class {self.className} error: {result['error']}")
            else:
                log_debug(f"[GENERATE_METHOD_EMBEDDING] finish embeddings method name: {self.methodName} class name: {self.className}")
        else:
            log_debug(f"[ERROR][GENERATE_METHOD_EMBEDDING] empty description for method {self.methodName} class {self.className}")
