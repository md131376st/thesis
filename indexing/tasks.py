import requests
from celery import shared_task
import json

from indexing.methodInfo import MethodInfo
from simplePipline.utils.utilities import log_debug


@shared_task()
def collect_method_info(method_name, qualified_class_name, source_code_path):
    log_debug(f"{method_name}, {qualified_class_name}, {source_code_path}")
    try:
        res = requests.request("GET",
                               f"http://localhost:8080/parser/methodsInfo/{qualified_class_name}/{method_name}",
                               headers={
                                   "sourceCodePath": source_code_path
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
                log_debug("MethodInfo {}".format(method))
                method.set_description()
                return method.to_dict()
        else:
            log_debug(f"parserProblem: {method_name} : status code: {res.status_code} ")
            return None  # o potresti voler ritornare qualcosa che indica un fallimento
    except Exception as e:
        log_debug(f"An error retrieving method info for {method_name}: {e}")
        return None
