import json
import os
import re
import requests
from celery import group, app, shared_task

from fileService import settings
from indexing.methodInfo import MethodInfo
from indexing.models import Record
from script.prompt import Create_Tech_functional_class
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
            return {"error": response}
        else:
            return response.json()
    except Exception as e:
        log_debug(f"error retrieving embedding for {collection_name}: {e} ")
        return {"error": "e"}

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

    def get_methods_for_class(self):
        try:
            log_debug(self.qualified_class_name)
            log_debug(self.sourceCodePath)
            response = requests.get(
                f"{settings.PARSER_URL}/classInfo/{self.qualified_class_name}",
                headers={
                    "sourceCodePath": self.sourceCodePath
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                log_debug(
                    f"Failed to retrieve classinfo  for {self.qualified_class_name} with status code {response.status_code}")
                return None
        except Exception as e:
            log_debug(f"An error while classinfo   for {self.qualified_class_name}: {e}")
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
            "description": self.description
        }
        return filter_empty_values(data)

    def set_qualified_class_name(self, package_name, exact=False):
        if exact:
            self.qualified_class_name = package_name
        else:
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
        job = group(self.collect_method_info.s(self, method_name) for method_name in self.method_names)
        results = job.apply_async()
        results.get()

    @shared_task()
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
                    method.set_description()
            else:
                log_debug(f"parserProblem: {method_name} : status code: {res.status_code} ")
        except Exception as e:
            log_debug(f"An error retrieving method info for {method_name}: {e}")

    def generate_class_index(self):
        for method in self.method_infos:
            method.set_description()

    def format_collection_name(self, qualified_class_name):
        # Remove the specific prefix and replace periods with dashes
        temp_name = qualified_class_name.replace("com.intesasanpaolo.bear.sxdr0.metaconto", "").replace(".", "-")

        # Ensure the name starts with a lowercase letter or digit
        if not re.match("^[a-z0-9]", temp_name):
            temp_name = "a" + temp_name  # Prefix with 'a' to ensure it starts correctly

        # Ensure the name ends with a lowercase letter or digit
        if not re.match("[a-z0-9]$", temp_name):
            temp_name += "1"  # Suffix with '1' to ensure it ends correctly

        # Adjust the length to be between 3 and 63 characters
        if len(temp_name) > 63:
            temp_name = temp_name[:63]  # Trim to the max length if necessary
        elif len(temp_name) < 3:
            temp_name += "a1"  # Add characters to meet the min length if necessary

        return temp_name

    def generate_class_embedding(self):
        chunks = []
        metadata = []
        if self.method_infos:
            collection_name = self.format_collection_name(self.qualified_class_name)
            for method in self.method_infos:
                result = Record.objects.filter(
                    collection_name__in=[collection_name],
                    name__in=[method.get_methodName()],
                    type__in=[Record.Type.Method]).values_list('chromaDb_id', flat=True)
                if result.exists():
                    chunks.append(
                        {
                            "text": method.get_description(),
                            "id": result.first()
                        }
                    )
                else:
                    chunks.append(
                        {
                            "text": method.get_description()
                        }
                    )
                metadata.append(method.get_meta_data())
            collection_metadata = self.get_meta_data()
            response = generate_embeddings(chunks, metadata, collection_name, collection_metadata)
            # keep track of indexes
            if "embedding_id_list" in response:
                records = []
                for id, method in zip(response["embedding_id_list"], self.method_infos):
                    records.append(Record(
                        name=method.get_methodName(),
                        chromaDb_id=id,
                        type=Record.Type.Method,
                        collection_name=collection_name))
                Record.objects.bulk_create(records)



        else:
            log_debug(f"empty class function")

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
        try:
            # Corrected syntax for getting environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                log_debug("OPENAI_API_KEY is not set in environment variables.")
                return None  # Return None if API key is not found

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": f"{Create_Tech_functional_class}"},
                    {"role": "user", "content": f"{self.description_class_prompt_data}"},
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

    def set_description(self, description):
        self.description = description

    def class_attributs(self):
        fields = ""
        for field in self.fields:
            fields += f"\n{field} "
        return fields

    def get_description(self):
        return self.description
