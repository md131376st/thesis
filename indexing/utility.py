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


def readfile(path):
    pass


def Get_json_filename(filename):
    return f"{filename.split('/')[1].rsplit('.')[0]}.json"


def Get_html_filename(filename):
    return f"{settings.PROCESSFIELS}/{str(filename.name).split('.')[0]}.html"


def filter_empty_values(data):
    return {k: v for k, v in data.items() if v != ''}
