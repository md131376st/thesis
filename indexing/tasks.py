import json
import os

import requests
from celery import shared_task, group, chain

from fileService import settings
from indexing import packageInfo
from indexing.methodInfo import MethodInfo
from indexing.packageInfo import PackageInfo
from script.prompt import Create_Tech_functional_class
from simplePipline.utils.utilities import log_debug


@shared_task()
def collect_package_class_info(**kwargs):
    packageInfo_data = kwargs.get('packageInfo')
    sourceCodePath = kwargs.get('sourceCodePath')
    packageInfo = PackageInfo.from_dict(packageInfo_data)
    log_debug(f"start code base indexing  : {packageInfo.package_name}")
    packageInfo.collect_classes(prefix=packageInfo.package_name, sourceCodePath=sourceCodePath)
    groups = [collect_class_info.s(classinfo=classinfo.to_dict()) for classinfo in packageInfo.classes]
    workflow = chain(
        group(*groups) |
        process_package_results.s() |
        update_package_info.s(packageInfo_data=packageInfo_data)
    )
    return workflow.apply_async()


@shared_task()
def update_package_info(results, packageInfo_data):
    log_debug(f"\n package indexing :\n {results} \n")
    log_debug(f"\n packageInfo_data :\n {packageInfo_data} \n")
    # updates the package data after result and returns it
    packageInfo = PackageInfo.from_dict(packageInfo_data)
    from indexing.classInfo import ClassInfo
    packageInfo.classes = [ClassInfo.from_dict(groupResult) for groupResult in results]
    description = packageInfo.generate_description()
    if description:
        packageInfo.set_description(description)
        # save package index level
        packageInfo.generate_package_embeddings()
    # add  root package descriptions
    packageInfo.generate_codebase_embeddings()
    return packageInfo.to_dict()


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
            log_debug(f"parser response {method_name}")
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
    method_info = MethodInfo.from_dict(method, False)
    log_debug(f" generate method description {method_name}")
    method_info.set_description()
    method_list.append(method_info.to_dict())


@shared_task()
def collect_class_info(**kwargs):
    classinfo_data = kwargs.get('classinfo')
    from indexing.classInfo import ClassInfo
    classinfo = ClassInfo.from_dict(classinfo_data)
    log_debug(f"start class indexing  : {classinfo.class_name}")
    result = [collect_method_info.s(method_name=method_name,
                                    qualified_class_name=classinfo.qualified_class_name,
                                    source_code_path=classinfo.sourceCodePath,
                                    classinfo_data=classinfo_data)()
              for method_name in classinfo.method_names]

    return {'results': result, 'classinfo_data': classinfo_data}


@shared_task
def process_package_results(all_results):
    log_debug("process_package_results")
    log_debug(f"\n all_results :  {all_results} \n ***********\n")
    from indexing.classInfo import ClassInfo
    results = []
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
        description = classInfo.generate_description()
        if description:
            classInfo.set_description(description)
            # generate class level embeddings
            classInfo.generate_class_embedding()
        results.append(classInfo.to_dict())


    return results


@shared_task()
def class_embedding_handler(all_result, classinfo):
    from indexing.classInfo import ClassInfo
    log_debug(f"class_embedding_handler: {len(all_result)}\n ***********\n")
    log_debug(f"class_embedding_handler: {all_result}\n ***********\n")
    classinfo_ = ClassInfo.from_dict(classinfo)
    log_debug(f"class_embedding_handler: {classinfo_.class_name}")
    method_info_list = []
    for result in all_result:
        # the methods can have overriding so the result can be a list
        if result[0]:
            method_info = MethodInfo.from_dict(result[0])
            method_info_list.append(method_info)
    classinfo_.method_infos = method_info_list
    classinfo_.generate_class_embedding()

    pass
