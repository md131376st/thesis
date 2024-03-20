import json

import requests

from fileService import settings
from indexing.utility import log_debug


class RagHandler:
    @staticmethod
    def rag_retrival(question,
                     n_results,
                     collection_name, keyword=None):
        try:
            request_data = {
                'collection_name': collection_name,
                'question': question,
                'n_results': n_results,
                'embedding_type': settings.EMBEDDING_TYPE
            }
            if keyword:
                request_data['keyword'] = keyword
            response = requests.request("POST",
                                        f"{settings.RAG_URL}/retrieve",
                                        headers={"Content-Type": "application/json"},
                                        data=json.dumps(request_data))
            if response.status_code != 200:
                log_debug(f"[ERROR]: {response.json()}")
                return None
            else:
                return response.json()
        except Exception as e:
            log_debug(f"[ERROR] error retrieving embedding for {collection_name}: {e} ")
            return None

    @staticmethod
    def rag_delete(collection_name, id):
        try:
            log_debug(f"[ERROR]: {collection_name}")
            response = requests.request(method="DELETE",
                                        url=f"{settings.RAG_URL}/document/{id}/",
                                        params={"collection_name": collection_name},
                                        headers={"Content-Type": "application/json"},
                                        )
            if response.status_code != 200:
                log_debug(f"[ERROR]: {response.json()}")
                return None
            else:
                return 200

        except Exception as e:
            log_debug(f"[ERROR] error retrieving embedding for {collection_name}: {e} ")
            return None

    @staticmethod
    def rag_store(chunks,
                  metadata,
                  collection_name,
                  collection_metadata) -> dict:
        try:
            log_debug(f"[RAG STORE]\n{chunks}\n{metadata}\n")
            response = requests.request(
                "POST",
                f"{settings.RAG_URL}/store",
                headers={"Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "collection_name": f"{collection_name}",
                        "is_async": True,
                        "chunks": chunks,
                        "metadata": metadata,
                        "collection_metadata": collection_metadata,
                        "embedding_type": settings.EMBEDDING_TYPE
                    }
                ))
            if response.status_code != 202:
                log_debug(f"[ERROR RESPONSE CODE]: {response}")
                return {"error": response}
            else:
                return response.json()
        except Exception as e:
            log_debug(f"[ERROR] retrieving embedding for {collection_name}: {e} ")
            return {"error": "e"}


def rag_store(chunks,
              metadata,
              collection_name,
              collection_metadata) -> dict:
    try:
        log_debug(f"[RAG STORE]\n{chunks}\n{metadata}\n")
        response = requests.request(
            "POST",
            f"{settings.RAG_URL}/store",
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "collection_name": f"{collection_name}",
                    "is_async": True,
                    "chunks": chunks,
                    "metadata": metadata,
                    "collection_metadata": collection_metadata,
                    "embedding_type": settings.EMBEDDING_TYPE
                }
            ))
        if response.status_code != 202:
            log_debug(f"[ERROR RESPONSE CODE]: {response}")
            return {"error": response}
        else:
            return response.json()
    except Exception as e:
        log_debug(f"[ERROR] retrieving embedding for {collection_name}: {e} ")
        return {"error": "e"}
