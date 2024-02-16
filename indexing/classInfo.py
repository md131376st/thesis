import json

import requests

from indexing.methodInfo import MethodInfo
from simplePipline.utils.utilities import filter_empty_values, log_debug


def generate_embeddings(chunks,
                        metadata,
                        collection_name,
                        collection_metadata):
    try:
        response = requests.request("POST",
                                    f"http://localhost:8000/embedding",
                                    headers={"Content-Type": "application/json"},
                                    data=json.dumps(
                                        {
                                            "collection_name": f"{collection_name}",
                                            "is_async": True,
                                            "chunks": chunks,
                                            "metadata": metadata,
                                            "collection_metadata": collection_metadata,
                                            "chunks_type": "txt",
                                            "embedding_type": "text-embedding-3-large"
                                        }
                                    ))
        if response.status_code != 202:
            log_debug(f"error: {response}")
    except Exception as e:
        log_debug(f"error retrieving embedding for {collection_name}: {e} ")

    pass


class ClassInfo:
    def __init__(self, class_name, path):
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
        self.description = ""

    def get_meta_data(self):
        data = {
            "class_name": self.class_name,
            "qualified_class_name": self.qualified_class_name,
            "code": self.code,
            "implemented_class": self.implemented_class,
            "extended_class": self.extended_class,
            "fields": json.dumps(self.fields) if isinstance(self.fields, list) else self.fields,
            "methods": json.dumps(self.methods) if isinstance(self.methods, list) else self.methods,
            "description": self.description
        }
        return filter_empty_values(data)

    def set_qualified_class_name(self, package_name):
        self.qualified_class_name = f"{package_name}.{self.class_name}"

    def fill_class_details(self, code, implemented_class, extended_class, fields, methods, method_names):
        self.code = code
        self.implemented_class = implemented_class
        self.extended_class = extended_class
        self.fields = fields
        self.methods = methods
        self.method_names = method_names

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
                                details['methodsNames'])
        self.method_info()

    def method_info(self):
        for method_name in self.method_names:
            self.collect_method_info(method_name)

    def collect_method_info(self, method_name):
        try:
            res = requests.request("GET",
                                   f"http://localhost:8080/parser/methodsInfo/{self.qualified_class_name}/{method_name}",
                                   headers={
                                       "sourceCodePath": self.sourceCodePath
                                   })

            if res.status_code == 200:

                info = json.loads(res.content)
                for data in info:
                    method = MethodInfo(
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
                        stringRepresentation=data["stringRepresentation"]
                    )
                    self.method_infos.append(method)

            else:
                log_debug(f"parserProblem: {method_name} : status code: {res.status_code} ")
        except Exception as e:
            log_debug(f"An error retrieving method info for {method_name}: {e}")

    def generate_class_index(self):
        for method in self.method_infos:
            method.set_description()

    def generate_class_embedding(self):
        chunks = []
        metadata = []
        if self.method_infos:
            for method in self.method_infos:
                chunks.append(
                    {
                        "text": method.get_description()
                    }
                )
                metadata.append(method.get_meta_data())
            collection_name = self.class_name
            collection_metadata = self.get_meta_data()
            generate_embeddings(chunks, metadata, collection_name, collection_metadata)
        else:
            log_debug(f"empty class function")
