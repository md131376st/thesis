import json

import requests

from fileService import settings
from simplePipline.utils.utilities import log_debug


def packet_info_call( sourceCodePath,prefix):
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