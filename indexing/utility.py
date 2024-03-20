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


def clean_description_json_string(description: str) -> str:
    if "```" not in description:
        return description
    begin_index = description.index("```json")
    end_index = description.rindex("```")
    return description[begin_index + 7:end_index]


def add_string_to_file(file_path, string_to_add):
    with open(file_path, 'a') as file:  # 'a' mode opens the file for appending
        file.write(string_to_add + '\n')
