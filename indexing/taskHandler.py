from typing import Type, Dict, Any, List

from fileService import settings
from indexing.utility import log_debug, rag_retrival


class TaskHandler:

    @staticmethod
    def package_retrival(question, package_name, n_results) -> dict[str, list[Any | None] | Any] | None:
        print("packaage_retrival", type(n_results))
        package_result = rag_retrival(question=question,
                                      collection_name=package_name,
                                      n_results=n_results)
        if "error" in package_result:
            log_debug(f"[Package Retrival Error] {package_result}")
            return None
        elif "answer" in package_result:
            package_final_result = dict()
            package_final_result["package"] = package_result["answer"]
            class_final_result = []
            for class_ in package_result["answer"]:
                if "metadata" in class_ and "qualified_class_name" in class_["metadata"]:
                    class_result = TaskHandler.class_retrival(question,
                                                              class_["metadata"]["qualified_class_name"],
                                                              n_results)
                    if class_result:
                        class_final_result.append(class_result)
            package_final_result["class"] = class_final_result
            return package_final_result

    @staticmethod
    def class_retrival(question, qualified_class_name, n_results):
        print("class_retrival", type(n_results))
        class_result = rag_retrival(question=question,
                                    collection_name=qualified_class_name,
                                    n_results=n_results)
        if "error" in class_result:
            log_debug(f"[Class Retrival Error] {class_result}")
            return None
        elif "answer" in class_result:
            return class_result["answer"]

    @staticmethod
    def query_handler(question, collection_name, n_results):
        # get question embedding
        log_debug(f"collection_name: {collection_name}")
        # start quering form root
        if collection_name is None:
            log_debug(f"hi")
            collection_name = settings.INDEXROOT
            log_debug(f"collection_name: {collection_name}")
            # print(type(n_results))
            result = rag_retrival(question=question,
                                  collection_name=collection_name,
                                  n_results=n_results)
            if "error" in result:
                return {
                    "status": "error",
                    "message": "the collection doesn't exist"
                }
            elif "answer" in result:
                final_result = []
                for package in result["answer"]:
                    if "metadata" in package and "package_name" in package["metadata"]:
                        package_result = TaskHandler.package_retrival(question=question,
                                                                      package_name=package["metadata"]["package_name"],
                                                                      n_results=n_results)
                        if package_result:
                            final_result.append(package_result)
                return final_result
