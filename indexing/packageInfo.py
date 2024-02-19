import json
import os

import requests

from indexing.classInfo import generate_embeddings
from simplePipline.utils.utilities import filter_empty_values, log_debug
from script.prompt import Create_Tech_functional_package


class PackageInfo:
    def __init__(self, package_name):
        self.package_name = package_name
        self.classes = []  # List to store ClassInfo instances
        self.description = ""

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def get_meta_data(self):
        data = {
            "package_name": self.package_name,
            "classes": json.dumps([cls.class_name for cls in self.classes]),
        }
        return filter_empty_values(data)

    def add_class(self, class_info):
        self.classes.append(class_info)

    def generate_package_embeddings(self):
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
            collection_name = str(self.package_name).replace(".", "-")[-60:]
            collection_metadata = self.get_meta_data()
            generate_embeddings(chunks, metadata, collection_name, collection_metadata)
        else:
            log_debug(f"empty package")

    def description_package_prompt_data(self):
        description = f"Package name : {self.package_name} \n"
        for classinfo in self.classes:
            description += f"{classinfo.get_description()} \n"
        return description

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
                    {"role": "system", "content": f"{Create_Tech_functional_package}"},
                    {"role": "user", "content": f"{self.description_package_prompt_data}"},
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

    def __repr__(self):
        return f"{self.package_name}', classes={self.classes})"
