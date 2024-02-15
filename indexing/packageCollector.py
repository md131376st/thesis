import json

import requests

from indexing.classInfo import ClassInfo
from indexing.packageInfo import PackageInfo
from simplePipline.utils.utilities import log_debug


class ClassPackageCollector:
    def __init__(self, path):
        self.packages = []
        self.sourceCodePath = path

    def packet_info_call(self, prefix):
        try:
            res = requests.get(
                f"http://localhost:8080/parser/packageInfo/{prefix}",
                headers={
                    "sourceCodePath": self.sourceCodePath
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
                class_info = ClassInfo(class_name, self.sourceCodePath)
                class_info.set_qualified_class_name(data["packageName"])
                details = self.get_methods_for_class(class_name, package_info.package_name)
                if details is not None:
                    class_info.update_class_details(details)
                    # class_info.process_methods()
                    package_info.add_class(class_info)
            if len(package_info.classes) != 0:
                self.packages.append(package_info)
            for sub_package_name in data["subPackageNames"]:
                print(sub_package_name)
                self.collect_package_info(sub_package_name)

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
                    "sourceCodePath": self.sourceCodePath
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                log_debug(
                    f"Failed to retrieve classinfo  for {package_name}.{class_name} with status code {response.status_code}")
                return None
        except Exception as e:
            log_debug(f"An error while classinfo   for {package_name}.{class_name}: {e}")
            return None
