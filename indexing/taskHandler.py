from typing import Type, Dict, Any, List

from fileService import settings
from indexing.types import QueryTypes
from indexing.utility import log_debug, rag_retrival


class TaskHandler:

    @staticmethod
    def package_retrival(question, package_name, n_results) -> list[
                                                                   dict[str, dict[str, list[Any | None]] | Any]] | None:
        package_result = rag_retrival(question=question,
                                      collection_name=package_name,
                                      n_results=n_results)
        if "error" in package_result:
            log_debug(f"[Package Retrival Error] {package_result}")
            return None
        elif "answer" in package_result:
            class_final_result = []
            for class_ in package_result["answer"]:
                if "metadata" in class_ and "qualified_class_name" in class_["metadata"]:
                    class_result = TaskHandler.class_retrival(question,
                                                              class_["metadata"]["qualified_class_name"],
                                                              n_results)
                    if class_result:
                        class_final_result.append(
                            {
                                "class": class_,
                                "methods": class_result
                            }
                        )

            return class_final_result

    @staticmethod
    def class_retrival(question, qualified_class_name, n_results) -> dict[str, list[Any | None]]:
        class_result = rag_retrival(question=question,
                                    collection_name=qualified_class_name,
                                    n_results=n_results)
        if not class_result:
            log_debug(f"[Class Retrival Error] {class_result}")
            return None
        elif "answer" in class_result:
            return class_result["answer"]

    @staticmethod
    def query_result_handler(result, question, n_results):
        if not result:
            return {
                "status": "error",
                "message": "the collection doesn't exist"
            }
        elif "answer" in result:
            package_result = []
            for package in result["answer"]:
                if "metadata" in package and "package_name" in package["metadata"]:
                    package_info = TaskHandler.package_retrival(question=question,
                                                                package_name=package["metadata"]["package_name"],
                                                                n_results=n_results)
                    if package:
                        package_result.append({
                            "package": package,
                            "classes": package_info
                        })

            return package_result
        pass

    @staticmethod
    def query_handler(question, collection_name, n_results, query_type):
        if (collection_name is None
                or query_type is QueryTypes.ALL.value
        ):
            collection_name = settings.INDEXROOT
            log_debug(f"[QUERY_HANDLER] collection_name: {collection_name}")
            result = rag_retrival(question=question,
                                  collection_name=collection_name,
                                  n_results=n_results)
            return TaskHandler.query_result_handler(result, question, n_results)

        elif query_type is QueryTypes.CODEBASE.value:
            log_debug(f"[QUERY_HANDLER] collection_name: {collection_name}")
            result = rag_retrival(question=question,
                                  collection_name=settings.INDEXROOT,
                                  n_results=n_results, keyword={"code_base_name": collection_name})
            return TaskHandler.query_result_handler(result, question, n_results)

        elif query_type is QueryTypes.PACKAGE.value:
            return TaskHandler.package_retrival(question=question,
                                                package_name=collection_name,
                                                n_results=n_results)
        else:
            return TaskHandler.class_retrival(question=question,
                                              qualified_class_name=collection_name,
                                              n_results=n_results)
