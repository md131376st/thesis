import hashlib
import json
import logging
import os

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
            log_debug(f"[ERROR] Failed to retrieve package {prefix} with status code {res.status_code}")
            return None

    except Exception as e:
        log_debug(f"[ERROR] An error on  {prefix}: {e}")
        return None


def log_debug(message):
    logger = logging.getLogger('AI_CODEBASE_EXPERT')
    logger.debug(message)
    return


def filter_empty_values(data):
    return {k: v for k, v in data.items() if v != ''}


def open_ai_description_generator(system_prompt, content, sender):
    try:
        # Corrected syntax for getting environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            log_debug("OPENAI_API_KEY is not set in environment variables.")
            return None  # Return None if API key is not found

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": f"{content}"},
            ],
            "temperature": 0
        }
        log_debug(f"[OPEN AI CALL] for: {sender}")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raises an exception for 4XX/5XX responses

        # Parsing the response assuming the structure is as expected
        return response.json()["choices"][0]['message']['content']

    except requests.exceptions.RequestException as e:
        # Handle network-related errors here
        log_debug(f"[ERROR] [OPEN AI] An error occurred while making the request: {e}")
    except KeyError as e:
        # Handle errors related to accessing parts of the response
        log_debug(f"[ERROR] [OPEN AI] An error occurred while parsing the response: {e}")
    except Exception as e:
        # Handle other possible exceptions
        log_debug(f" [ERROR] [OPEN AI] An unexpected error occurred: {e}")

        # Return None if the function cannot complete as expected due to any error
    return None


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
