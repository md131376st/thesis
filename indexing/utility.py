import hashlib
import json
import logging

import requests

from fileService import settings


def packet_info_call(sourceCodePath, prefix):
    try:
        res = requests.get(
            f"{settings.PARSER_URL}packageInfo/{prefix}",
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


def format_collection_name(qualified_class_name):
    # Crea l'oggetto hash SHA-256
    sha256_hash = hashlib.sha256()
    # Aggiorna l'hash con i byte della stringa input
    sha256_hash.update(qualified_class_name.encode("utf-8"))
    # Ottiene la rappresentazione esadecimale completa dell'hash
    hashed_string_full = sha256_hash.hexdigest()
    # Tronca la stringa hash agli ultimi 60 caratteri
    hashed_string_truncated = hashed_string_full[:63]
    return hashed_string_truncated


def log_debug(message):
    logger = logging.getLogger('my_app')
    logger.debug(message)
    return


def filter_empty_values(data):
    return {k: v for k, v in data.items() if v != ''}


def rag_store(chunks,
              metadata,
              collection_name,
              collection_metadata) -> dict:
    try:
        response = requests.request("POST",
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
            log_debug(f"error: {response}")
            return {"error": response}
        else:
            return response.json()
    except Exception as e:
        log_debug(f"error retrieving embedding for {collection_name}: {e} ")
        return {"error": "e"}


def rag_retrival(question,
                 n_results,
                 collection_name) -> dict:
    try:
        request_data = {
            "collection_name": collection_name,
            "question": question,
            "n_results": n_results,
            "embedding_type": settings.EMBEDDING_TYPE
        }
        log_debug(request_data)
        response = requests.request("POST",
                                    f"{settings.RAG_URL}/retrieve",
                                    headers={"Content-Type": "application/json"},
                                    data=json.dumps(request_data))
        if response.status_code != 200:
            log_debug(f"error: {response}")
            return {"error": response.json()}
        else:
            return response.json()
    except Exception as e:
        log_debug(f"error retrieving embedding for {collection_name}: {e} ")
        return {"error": "e"}
