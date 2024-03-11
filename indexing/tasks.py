import json

import requests
from celery import shared_task, group, chain

from fileService import settings
from indexing.info.methodInfo import MethodInfo
from indexing.info.packageInfo import PackageInfo
from indexing.utility import log_debug


@shared_task()
def collect_package_class_info(**kwargs):
    """
    Starter for a package to be collected.
    """
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
    packageInfo.set_description("PackageInfo_set_description", packageInfo.package_name)
    log_debug(f"\n [UPDATE_PACKAGE_INFO] save package descriptions in mongodb :\n \n")
    packageInfo.store_in_mongo_db()
    # log_debug(f"\n[UPDATE_PACKAGE_INFO] generate package embedding in base class {packageInfo.package_name}  :\n\n")
    # packageInfo.generate_codebase_embeddings()
    # log_debug(f"\n [UPDATE_PACKAGE_INFO] finish package embedding in base class {packageInfo.package_name} :\n\n")
    return packageInfo.to_dict()


@shared_task()
def collect_method_info(**kwargs):
    """
    Starter for sending the task to collect information about a method.
    """
    # Assumendo che `method_name` e altre variabili necessarie siano passate correttamente.
    method_name = kwargs.get('method_name')
    qualified_class_name = kwargs.get('qualified_class_name')
    source_code_path = kwargs.get('source_code_path')
    class_metadata = kwargs.get('class_metadata')
    try:
        #  call to parser for get method info
        res = requests.request(
            "GET",
            f"{settings.PARSER_URL}methodsInfo/{qualified_class_name}/{method_name}",
            headers={
                "sourceCodePath": source_code_path
            }
        )
        log_debug(f"[METHOD PREPROCESS] send parser request: {method_name}")
        if res.status_code == 200:
            log_debug(f"[METHOD PREPROCESS] receive parser request:{method_name}")
            methods = json.loads(res.content)
            method_list = []
            if isinstance(methods, list):
                for method in methods:
                    method_info = generate_method_info(method, method_name, class_metadata)
                    method_list.append(method_info)
            else:
                generate_method_info(methods, method_name, class_metadata)
            return method_list
        else:
            log_debug(f"[ERROR] parserProblem: {method_name} : status code: {res.status_code} ")
            return None  # o potresti voler ritornare qualcosa che indica un fallimento
    except Exception as e:
        log_debug(f"[ERROR] An error retrieving method info for {method_name}: {e}")
        return None


def generate_method_info(method: dict, method_name: str, class_metadata: str) -> dict:
    method_info = MethodInfo.from_dict(method, False)
    log_debug(f"[METHOD PREPROCESS] generate method description {method_name}")
    method_info.set_description("MethodInfo_set_description",
                                method_name)  # generating also the description with openai
    log_debug(f"[METHOD PREPROCESS] generated description is {method_info.description}")
    method_info.store_in_mongo_db()
    log_debug(f"[METHOD PREPROCESS]stored in mongodb {method_name}")
    # method_info.generate_method_embedding(class_metadata)
    # log_debug(f"[METHOD PREPROCESS] generated method embedding")
    return method_info.to_dict()


@shared_task()
def collect_class_info(**kwargs):
    """
    Starter for collecting the info about a single class in a package.
    """
    classinfo_data = kwargs.get('classinfo')
    from indexing.info.classInfo import ClassInfo
    class_info = ClassInfo.from_dict(classinfo_data)
    class_metadata = class_info.get_meta_data()
    log_debug(f"[CLASS_INDEXING] start class name: {class_info.class_name}")
    result = [
        collect_method_info.s(
            method_name=method_name,
            qualified_class_name=class_info.qualified_class_name,
            source_code_path=class_info.sourceCodePath,
            class_metadata=class_metadata
        )()
        for method_name in class_info.method_names
    ]
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
        classInfo.set_description("classInfo_set_description", classInfo.qualified_class_name)
        log_debug(f"[PROCESS_PACKAGE_RESULT]:saving class description  {classInfo.class_name}")
        # save descriptions in mongodb
        classInfo.store_in_mongo_db()
        # generate class level embeddings
        # classInfo.generate_class_embedding()

        results.append(classInfo)
    package_info = PackageInfo.from_dict(packageInfo_data)
    package_info.classes = results
    log_debug(f"[PROCESS_PACKAGE_RESULT] generate package embedding: {package_info.package_name} ")
    results_ = [classInfo.to_dict() for classInfo in results]
    return results_
