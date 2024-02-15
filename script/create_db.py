import os

import requests
import json
import logging

from simplePipline.utils.utilities import log_debug

sourceCodePath = "/Users/davarimona/Downloads/core-r-metaconto-v1"


class MethodInfo:
    def __init__(self,
                 returnType,
                 methodName,
                 className,
                 packageName,
                 body,
                 modifier,
                 signature,
                 parametersNames,
                 parametersTypes,
                 annotations,
                 exceptions,
                 signatureDependencies,
                 bodyDependencies,
                 signatureDependenciesWithPackage,
                 bodyDependenciesWithPackage,
                 imports,
                 stringRepresentation):
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

    def __repr__(self):
        return f"methodName='{self.methodName}', returnType='{self.returnType}', className='{self.className}', packageName='{self.packageName}')"


class ClassInfo:
    def __init__(self, class_name):
        self.class_name = class_name
        self.qualified_class_name = None
        self.code = None
        self.implemented_class = None
        self.extended_class = None
        self.fields = []
        self.methods = []
        self.method_infos = []
        self.method_names = []

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

    def method_info(self):
        for method_name in self.method_names:
            self.collect_method_info(method_name)

    def collect_method_info(self, method_name):
        try:
            res = requests.request("GET",
                                   f"http://localhost:8080/parser/methodsInfo/{self.qualified_class_name}/{method_name}",
                                   headers={
                                       "sourceCodePath": sourceCodePath
                                   })
            if res.status_code == 200:
                data = json.loads(res.content)
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

    def process_methods(self):
        pass


class PackageInfo:
    def __init__(self, package_name):
        self.package_name = package_name
        self.classes = []  # List to store ClassInfo instances

    def add_class(self, class_info):
        self.classes.append(class_info)

    def __repr__(self):
        return f"{self.package_name}', classes={self.classes})"


class ClassPackagePair:
    def __init__(self, class_name, package_name):
        self.class_name = class_name
        self.package_name = package_name

    def __str__(self):
        return f'{self.package_name}.{self.class_name}'


class ClassPackageCollector:
    def __init__(self):
        self.packages = []

    def packet_info_call(self, prefix):
        try:
            res = requests.get(
                f"http://localhost:8080/parser/packageInfo/{prefix}",
                headers={
                    "sourceCodePath": sourceCodePath
                }
            )

            if res.status_code == 200:
                data = json.loads(res.content)
                return data
            else:
                log_debug(f"Failed to retrieve package {prefix} with status code {res.status_code}")
                return None

        except Exception as e:
            log_debug(f"An error on  {prefix}: {e}")
            return None

    def collect_package_info(self, prefix):
        data = self.packet_info_call(prefix)
        if data is not None:
            package_info = PackageInfo(data["packageName"])

            for class_name in data["classNames"]:
                class_info = ClassInfo(class_name)
                class_info.set_qualified_class_name(data["packageName"])
                details = self.get_methods_for_class(class_name, package_info.package_name)
                if details is not None:
                    class_info.update_class_details(details)

                    package_info.add_class(class_info)
            if len(package_info.classes) != 0:
                self.packages.append(package_info)
            return data["subPackageNames"]

    def get_collected_data(self):
        return self.packages

    def get_class_names_with_packages(self):
        class_with_packages = []
        for package in self.packages:
            for class_info in package.classes:
                full_name = f"{package.package_name}.{class_info.class_name}"
                class_with_packages.append(full_name)
        return class_with_packages

    def get_methods_for_class(self, class_name, package_name):
        try:
            response = requests.get(
                f"http://localhost:8080/parser/classInfo/{package_name}.{class_name}",
                headers={
                    "sourceCodePath": sourceCodePath
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                log_debug(
                    f"Failed to retrieve method  for {package_name}.{class_name} with status code {response.status_code}")
                return None
        except Exception as e:
            log_debug(f"An error while retrieving method  for {package_name}.{class_name}: {e}")
            return None


if __name__ == '__main__':
    prefixes = ['com.intesasanpaolo.bear.sxdr0.metaconto.connector.storage.transformers',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.ws.anagrafe.didy',
              'com.intesasanpaolo.bear.sxdr0.metaconto.factory', 'com.intesasanpaolo.bear.sxdr0.metaconto.resource',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.kafka.producer',
              'com.intesasanpaolo.bear.sxdr0.metaconto.model.kafka', 'com.intesasanpaolo.bear.sxdr0.metaconto.model',
              'com.intesasanpaolo.bear.sxdr0.metaconto.controller.test',
              'com.intesasanpaolo.bear.sxdr0.metaconto.utils',
              'com.intesasanpaolo.bear.sxdr0.metaconto.model.notificator',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.ws',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.storage',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.internal',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.rest',
              'com.intesasanpaolo.bear.sxdr0.metaconto.model.jpa', 'com.intesasanpaolo.bear.sxdr0.metaconto.exception',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.internal.transformers',
              'com.intesasanpaolo.bear.sxdr0.metaconto.cache',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.kafka.consumer',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.gridfsmongo',
              'com.intesasanpaolo.bear.sxdr0.metaconto.model.predicate',
              'com.intesasanpaolo.bear.sxdr0.metaconto.service',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.ws.transformers',
              'com.intesasanpaolo.bear.sxdr0.metaconto.service.exception',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.jpa', 'com.intesasanpaolo.bear.sxdr0.metaconto.dto',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.gridfsmongo.transformers',
              'com.intesasanpaolo.bear.sxdr0.metaconto.service.kafka',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.kafka.processor',
              'com.intesasanpaolo.bear.sxdr0.metaconto.controller',
              'com.intesasanpaolo.bear.sxdr0.metaconto.connector.rest.transformers',
              'com.intesasanpaolo.bear.sxdr0.metaconto.command', 'com.intesasanpaolo.bear.sxdr0.metaconto.assembler']
    collected_data = []
    for prefix in  prefixes:
        collector = ClassPackageCollector()
        subclasses = collector.collect_package_info(prefix)
        if subclasses:
            for subclass in subclasses:
                collector = ClassPackageCollector()
                subclasses_ = collector.collect_package_info(subclass)
                collected_data += collector.get_collected_data()
