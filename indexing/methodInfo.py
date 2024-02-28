import json
import os

import requests

from indexing.baseInfo import BaseInfo
from script.prompt import Create_Tech_functional
from simplePipline.utils.utilities import filter_empty_values, log_debug
from dotenv import load_dotenv


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
        return f"methodName='{self.methodName}', returnType='{self.returnType}', className='{self.className}', packageName='{self.packageName}')"

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
        try:
            # Corrected syntax for getting environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                log_debug("OPENAI_API_KEY is not set in environment variables.")
                return None  # Return None if API key is not found
            log_debug(f"OPENAI_API_CALL: {self.methodName}")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": f"{Create_Tech_functional}"},
                    {"role": "user", "content": f"{self.body}"},
                ],
                "max_tokens": 1024,
                "temperature": 0
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # Raises an exception for 4XX/5XX responses

            # Parsing the response assuming the structure is as expected
            return response.json()["choices"][0]['message']['content']

        except requests.exceptions.RequestException as e:
            # Handle network-related errors here
            log_debug(f"An error occurred while making the request: {e}")
        except KeyError as e:
            # Handle errors related to accessing parts of the response
            log_debug(f"An error occurred while parsing the response: {e}")
        except Exception as e:
            # Handle other possible exceptions
            log_debug(f"An unexpected error occurred: {e}")

        # Return None if the function cannot complete as expected due to any error
        return None
