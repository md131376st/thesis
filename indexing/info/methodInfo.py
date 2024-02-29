import json
import os

import requests

from indexing.info.baseInfo import BaseInfo
from indexing.prompt import Create_Tech_functional
from indexing.utility import log_debug, filter_empty_values, open_ai_description_generator


def add_string_to_file(file_path, string_to_add):
    with open(file_path, 'a') as file:  # 'a' mode opens the file for appending
        file.write(string_to_add + '\n')


class MethodInfo(BaseInfo):
    def __init__(self, returnType, methodName, className, packageName, body, modifier, signature, parametersNames,
                 parametersTypes, annotations, exceptions, signatureDependencies, bodyDependencies,
                 signatureDependenciesWithPackage, bodyDependenciesWithPackage, imports, stringRepresentation,
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
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data, isDescription=True):
        if isDescription:
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
                description=data["description"],
            )
        else:
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
            "description": self.description
        }
        return filter_empty_values(data)

    def set_description(self):
        self.description = self.generate_description()
        if self.description is None:
            add_string_to_file("retry_methodName.txt", f"{self.methodName}")

    def get_description(self):
        return self.description

    def get_methodName(self):
        return self.methodName

    def generate_description(self) -> str | None:
        return open_ai_description_generator(system_prompt=Create_Tech_functional,
                                             content=self.body,
                                             sender=self.methodName
                                             )
