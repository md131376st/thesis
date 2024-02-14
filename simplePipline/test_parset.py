import os

import requests
import json
import logging

from simplePipline.utils.utilities import log_debug

path = "/Users/davarimona/Downloads/core-r-metaconto-v1/src/main/java/com/intesasanpaolo/bear/sxdr0/metaconto/"


def image_description_call(methodSigneture, sysprompt):
    api_key = os.environ["OPENAI_API_KEY"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"{sysprompt}"},
            {"role": "user", "content": f" the method is this:   {methodSigneture}"},
        ],
        "max_tokens": 1000,

    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()["choices"][0]['message']['content']


def list_directories(path='.'):
    """List all directories in the given path. Default is the current directory."""
    # List all entries in the path
    all_entries = os.listdir(path)

    # Filter out directories
    directories = [entry for entry in all_entries if os.path.isdir(os.path.join(path, entry))]

    return directories


def list_files(directory='.'):
    """List all files in the given directory. Default is the current directory."""
    # Get a list of all entries in the directory
    all_entries = os.listdir(directory)

    # Filter the list to include only files
    files = [entry for entry in all_entries if os.path.isfile(os.path.join(directory, entry))]

    return files


def list_java_files_with_nested_prefix(directory='.', base_prefix='BasePrefix'):
    """List all .java files in the given directory and its subdirectories without the '.java' extension,
    with a prefix added that includes additional identifiers for nested directories separated by dots."""
    files_with_prefix = []

    # Helper function to recursively list files and add prefixes based on directory nesting
    def list_files_recursive(current_directory, current_prefix):
        # Get a list of all entries in the current directory
        all_entries = os.listdir(current_directory)

        for entry in all_entries:
            full_path = os.path.join(current_directory, entry)

            if os.path.isfile(full_path) and entry.endswith('.java'):
                # If entry is a .java file, strip the extension, add the current prefix, and append to the result list
                # Check if current_prefix is not empty to avoid leading dots
                filename_without_extension = entry.removesuffix('.java')
                prefixed_filename = f"{current_prefix}.{filename_without_extension}" if current_prefix else filename_without_extension
                files_with_prefix.append(prefixed_filename)
            elif os.path.isdir(full_path):
                # If entry is a directory, recurse into it with an updated prefix
                # Check if current_prefix is not empty to avoid leading dots
                new_prefix = f"{current_prefix}.{entry}" if current_prefix else entry
                list_files_recursive(full_path, new_prefix)

    # Start the recursive file listing from the base directory with the base prefix
    list_files_recursive(directory, base_prefix)

    return files_with_prefix


def process_data(data):
    metadata = {}

    # Fields to be directly copied
    direct_fields = [
        "returnType", "methodName", "className", "packageName", "body", "modifier", "signature", "stringRepresentation"
    ]

    # Fields that need to be converted to JSON strings
    json_fields = [
        "parametersNames", "parametersTypes", "annotations", "exceptions", "signatureDependencies",
        "bodyDependencies", "signatureDependenciesWithPackage", "bodyDependenciesWithPackage", "imports"
    ]

    # Copy direct fields if they exist and are not empty
    for field in direct_fields:
        value = data.get(field)
        if value:
            metadata[field] = value

    # Convert list fields to JSON strings if they exist
    for field in json_fields:
        value = data.get(field)
        if value:
            metadata[field] = json.dumps(value)

    return metadata


if __name__ == '__main__':
    prefix = "com.intesasanpaolo.bear.sxdr0.metaconto"
    classList = []
    empty_classMethods = []
    problem_classes = []
    responses = []
    directories = list_directories(path)
    for directory in directories:
        classList += list_java_files_with_nested_prefix(directory=f"{path}/{directory}", base_prefix=f"{directory}")

    log_debug("number of classes: " + str(len(classList)))
    num = 0
    # additional classes
    for classname in classList:
        response = requests.request("GET",
                                    f"http://localhost:8080/parser/classInfo/{prefix}.{classname}",
                                    headers={
                                        "sourceCodePath": "/Users/davarimona/Downloads/core-r-metaconto-v1"
                                    })
        data = json.loads(response.content)
        methods = [element for element in data["methods"]]
        methodsNames = [element for element in data["methodsNames"]]
        if len(methods) == 0:
            log_debug(f"empty class: {classname} ")
            empty_classMethods.append(classname)
            continue
        prompt = ("you are a java coding interpreter.\n"
                  " you are provided a method declaration and you have to describe.\n"
                  " the description should be synthetic"
                  " include of params and the return values\n"
                  " take your time to answer \n"
                  "don't make any assumption ")

        for index, element in enumerate(methods):

            description = image_description_call(element, prompt)
            try:
                methods = requests.request("GET",
                                           f"http://localhost:8080/parser/methodsInfo/{classname}/{methodsNames[index]}",
                                           headers={
                                               "sourceCodePath": "/Users/davarimona/Downloads/core-r-metaconto-v1"
                                           })
                if methods.status_code == 200:
                    methodOverRide = json.loads(methods.content)
                    for data in methodOverRide:
                        metadata = process_data(data)
                else:
                    log_debug(f"parserProblem: {classname} : status code: {response.status_code} ")
                    problem_classes.append(classname)
                    break

                value = data.get("body", None)
                response = requests.request("POST",

                                            f"http://localhost:8000/embedding",
                                            headers={"Content-Type": "application/json"},
                                            data=json.dumps({
                                                "collection_name": f"{classname}",
                                                "is_async": True,
                                                "chunks": [
                                                    {
                                                        "text": f"description: {description}, code: {value}  ",
                                                    }
                                                ],
                                                "metadata": [metadata],
                                                "chunks_type": "txt",
                                                "embedding_type": "text-embedding-3-large"
                                            }
                                            )
                                            )
                log_debug(f"{classname}: done")
                responses.append(response)
            except IndexError:
                log_debug(f"parser error indexError classname: {classname} :  ")
                problem_classes.append(classname)
                break
