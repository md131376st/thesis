

from fileService import settings
from indexing.utility import log_debug


class TaskHandler:

    @staticmethod
    def query_handler(question, classname, embedding_type, n_results):
        # get question embedding
        pass
        # start quering form root
        # if classname is None:
        #     result = []
        #     collection = db.get_collection(name=settings.INDEXROOT)
        #     results = collection.query(query_embeddings=embedding,
        #                                n_results=n_results)
        #     for text, metadata in zip(
        #             results["documents"][0],
        #             results["metadatas"][0]):
        #         if "package_name" in metadata:
        #             package_collection_name = get_package_name(metadata["package_name"])
        #             package_collection = db.get_collection(name=package_collection_name)
        #             packageResult = package_collection.query(query_embeddings=embedding,
        #                                                      n_results=n_results)
        #             packageinfo = []
        #             for package_text, package_meta_data in zip(
        #                     packageResult["documents"][0],
        #                     packageResult["metadatas"][0]):
        #                 data = {
        #                     "package": package_text,
        #                     "metadata": package_meta_data
        #                 }
        #
        #                 if "qualified_class_name" in package_meta_data:
        #
        #                     classinfo = []
        #                     class_collection_name = get_class_collection_name(package_meta_data["qualified_class_name"])
        #                     class_collection = db.get_collection(name=class_collection_name)
        #                     classResult = class_collection.query(query_embeddings=embedding,
        #                                                          n_results=n_results)
        #                     for classinfo_text, classinfo_text_meta_data in zip(
        #                             classResult["documents"][0],
        #                             classResult["metadatas"][0]):
        #                         classinfo.append(
        #                             {
        #                                 "text": classinfo_text,
        #                                 "metadata": classinfo_text_meta_data
        #                             }
        #                         )
        #                     data["class"] = classinfo
        #                 packageinfo.append(data)
        #             result.append(packageinfo)
        #
        #     return result
        #
        # # just returning the level base
        # else:
        #     collection = db.get_collection(name=classname)
        #     results = collection.query(query_embeddings=embedding,
        #                                n_results=n_results)
        #     result = []
        #     log_debug(results)
        #     for text, metadata in zip(
        #             results["documents"][0],
        #             results["metadatas"][0]):
        #         result.append(
        #             {
        #                 "text": text,
        #                 "metadata": metadata
        #             }
        #         )
        #     return result
