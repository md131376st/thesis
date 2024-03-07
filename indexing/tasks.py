import json

import requests
from celery import shared_task, group, chain

from fileService import settings
from indexing.info.methodInfo import MethodInfo
from indexing.info.packageInfo import PackageInfo
from indexing.utility import log_debug


@shared_task()
def collect_package_class_info(**kwargs):
    packageInfo_data = kwargs.get('packageInfo')
    sourceCodePath = kwargs.get('sourceCodePath')
    packageInfo = PackageInfo.from_dict(packageInfo_data)
    log_debug(f"[COLLECT_PACKAGE_CLASS_INFO] package name : {packageInfo.package_name}")
    packageInfo.collect_classes(prefix=packageInfo.package_name, sourceCodePath=sourceCodePath)
    groups = [collect_class_info.s(classinfo=classinfo.to_dict()) for classinfo in packageInfo.classes]
    workflow = chain(
        group(*groups) |
        process_package_results.s(packageInfo_data=packageInfo_data) |
        update_package_info.s(packageInfo_data=packageInfo_data)
    )
    return workflow()


@shared_task()
def update_package_info(results, packageInfo_data):
    log_debug(f"\n [UPDATE_PACKAGE_INFO] start")
    # updates the package data after result and returns it
    packageInfo = PackageInfo.from_dict(packageInfo_data)
    from indexing.info.classInfo import ClassInfo
    log_debug(f"\n [UPDATE_PACKAGE_INFO] set package class list :\n\n")
    packageInfo.classes = [ClassInfo.from_dict(groupResult) for groupResult in results]
    log_debug(f"\n [UPDATE_PACKAGE_INFO] generate package class list :\n \n")
    description = packageInfo.generate_description()
    if description:
        packageInfo.set_description(description)
        log_debug(f"\n[UPDATE_PACKAGE_INFO] generate package embedding in base class {packageInfo.package_name}  :\n\n")
        packageInfo.generate_codebase_embeddings()
        log_debug(f"\n [UPDATE_PACKAGE_INFO] finish package embedding in base class {packageInfo.package_name} :\n\n")
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
        log_debug(f"[METHOD PREPROCESS] send parser request: {method_name}")

        if res.status_code == 200:
            log_debug(f"[METHOD PREPROCESS] receive parser request:{method_name}")
            methods = json.loads(res.content)
            method_list = []
            if isinstance(methods, list):
                log_debug(f"PIPPPOOOOO: {method_name}")
                for method in methods:
                    generate_method_info(method_list, method, method_name)
            else:
                generate_method_info(method_list, methods, method_name)
            return method_list
        else:
            log_debug(f"[ERROR] parserProblem: {method_name} : status code: {res.status_code} ")
            return None  # o potresti voler ritornare qualcosa che indica un fallimento
    except Exception as e:
        log_debug(f"[ERROR] An error retrieving method info for {method_name}: {e}")
        return None


def generate_method_info(method_list, method, method_name):
    method_info = MethodInfo.from_dict(method, False)
    log_debug(f"[METHOD PREPROCESS] generate method description {method_name}")
    method_info.set_description()
    log_debug(f"[METHOD PREPROCESS] generated description is {method_info.description}")
    method_list.append(method_info.to_dict())


@shared_task()
def collect_class_info(**kwargs):
    classinfo_data = kwargs.get('classinfo')
    from indexing.info.classInfo import ClassInfo
    classinfo = ClassInfo.from_dict(classinfo_data)
    log_debug(f"[CLASS_INDEXING] start class name: {classinfo.class_name}")
    result = [collect_method_info.s(method_name=method_name,
                                    qualified_class_name=classinfo.qualified_class_name,
                                    source_code_path=classinfo.sourceCodePath,
                                    classinfo_data=classinfo_data)()
              for method_name in classinfo.method_names]

    return {'results': result, 'classinfo_data': classinfo_data}


@shared_task
def process_package_results(all_results, packageInfo_data):
    log_debug("[PROCESS_PACKAGE_RESULT] started")
    from indexing.info.classInfo import ClassInfo
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
        log_debug(f"[PROCESS_PACKAGE_RESULT]:generate Class description {classInfo.class_name}")
        description = classInfo.generate_description()
        if description:
            classInfo.set_description(description)
            # generate class level embeddings
            classInfo.generate_class_embedding()
        results.append(classInfo)
    package_info = PackageInfo.from_dict(packageInfo_data)
    package_info.classes = results
    log_debug(f"[PROCESS_PACKAGE_RESULT] generate package embedding: {package_info.package_name} ")
    package_info.generate_package_embeddings()
    results_ = [classInfo.to_dict() for classInfo in results]
    return results_


@shared_task()
def class_embedding_handler(all_result, classinfo):
    from indexing.info.classInfo import ClassInfo
    log_debug(f"[CLASS_EMMBEDING_HANDLER] number of chunks send : {len(all_result)}")
    # log_debug(f"class_embedding_handler: {all_result}\n ***********\n")
    classinfo_ = ClassInfo.from_dict(classinfo)
    log_debug(f"[CLASS_EMMBEDING_HANDLER] class name: {classinfo_.class_name}")
    method_info_list = []
    for methods_list in all_result:
        if not isinstance(methods_list, list):
            methods_list = [methods_list]
        # the methods can have overriding so the result can be a list
        for method in methods_list:
            if isinstance(method, dict):
                method_info = MethodInfo.from_dict(method)
                method_info_list.append(method_info)
            else:
                log_debug(f"[ERROR][CLASS_EMMBEDING_HANDLER] result reutuned form tasks are wronge: {method}")

    classinfo_.method_infos = method_info_list
    classinfo_.generate_class_embedding()
