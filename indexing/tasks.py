import json
import os

import requests
from celery import shared_task, group

from fileService import settings
from indexing.methodInfo import MethodInfo
from script.prompt import Create_Tech_functional_class
from simplePipline.utils.utilities import log_debug


@shared_task()
def collect_method_info(**kwargs):
    # Assumendo che `method_name` e altre variabili necessarie siano passate correttamente.
    method_name = kwargs.get('method_name')
    qualified_class_name = kwargs.get('qualified_class_name')
    source_code_path = kwargs.get('source_code_path')
    try:
        res = requests.request("GET",
                               f"{settings.PARSER_URL}methodsInfo/{qualified_class_name}/{method_name}",
                               headers={
                                   "sourceCodePath": source_code_path
                               })
        log_debug(f"parser request {method_name}")

        if res.status_code == 200:
            methods = json.loads(res.content)
            method_List = []
            if isinstance(methods, list):
                for method in methods:
                    Generate_method_info(method_List, method, method_name)
            else:
                Generate_method_info(method_List, methods, method_name)
            return method_List
        else:
            log_debug(f"parserProblem: {method_name} : status code: {res.status_code} ")
            return None  # o potresti voler ritornare qualcosa che indica un fallimento
    except Exception as e:
        log_debug(f"An error retrieving method info for {method_name}: {e}")
        return None


def Generate_method_info(method_list, method, method_name):
    log_debug(f"parser restive {method_name}")
    method_info = MethodInfo.from_dict(method,False)
    log_debug(f"parser restive {method_name} made dict")
    method_info.set_description()
    method_list.append(method_info.to_dict())


@shared_task()
def class_embedding_handler(all_result, classinfo):
    from indexing.classInfo import ClassInfo
    classinfo_ = ClassInfo.from_dict(classinfo)
    method_info_list=[]
    for result in all_result:
        # the methods can have overriding so the result can be a list
        if result:
            log_debug(f"result :  {result}")
            method_info = MethodInfo.from_dict(result)
            log_debug(f"method info :  {method_info.get_description()}")
            method_info_list.append(method_info)
    classinfo_.method_infos = method_info_list
    classinfo_.generate_class_embedding()

    pass


# @shared_task()
# def generate_description(data):
#     try:
#         # Corrected syntax for getting environment variable
#         api_key = os.environ.get("OPENAI_API_KEY")
#         if not api_key:
#             log_debug("OPENAI_API_KEY is not set in environment variables.")
#             return None  # Return None if API key is not found
#
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {api_key}"
#         }
#         payload = {
#             "model": "gpt-4-turbo-preview",
#             "messages": [
#                 {"role": "system", "content": f"{Create_Tech_functional_class}"},
#                 {"role": "user", "content": f"{data}"},
#             ],
#             "max_tokens": 1024,
#             "temperature": 0
#         }
#
#         response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
#         response.raise_for_status()  # Raises an exception for 4XX/5XX responses
#
#         # Parsing the response assuming the structure is as expected
#         return response.json()["choices"][0]['message']['content']
#
#     except requests.exceptions.RequestException as e:
#         # Handle network-related errors here
#         log_debug(f"An error occurred while making the request: {e}")
#     except KeyError as e:
#         # Handle errors related to accessing parts of the response
#         log_debug(f"An error occurred while parsing the response: {e}")
#     except Exception as e:
#         # Handle other possible exceptions
#         log_debug(f"An unexpected error occurred: {e}")
#
#         # Return None if the function cannot complete as expected due to any error
#     return None


@shared_task()
def collect_class_info(**kwargs):
    classinfo_data = kwargs.get('classinfo')
    from indexing.classInfo import ClassInfo
    classinfo = ClassInfo.from_dict(classinfo_data)

    result = [collect_method_info.s(method_name=method_name,
                                    qualified_class_name=classinfo.qualified_class_name,
                                    source_code_path=classinfo.sourceCodePath,
                                    classinfo_data=classinfo_data)()
              for method_name in classinfo.method_names]

    return {'results': result, 'classinfo_data': classinfo_data}


@shared_task
def process_final_results(all_results):
    from indexing.classInfo import ClassInfo
    for group_result in all_results:
        # generate class embeddings
        method_info_list = []
        classinfo_data = group_result['classinfo_data']
        classInfo = ClassInfo.from_dict(classinfo_data)
        for result in group_result['results']:
            # the methods can have overriding so the result can be a list
            if result:
                # add for each class the method descriptions
                for result_ in result:
                    method_info = MethodInfo.from_dict(result_)
                    method_info_list.append(method_info)
        # generate class Descriptions

        classInfo.method_infos = method_info_list
        log_debug("generate Class description ")
        classInfo.generate_description()
        classInfo.generate_class_embedding()
    return
