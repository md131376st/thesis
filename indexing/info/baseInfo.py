from abc import ABC

from indexing.utility import log_debug, add_string_to_file


class BaseInfo(ABC):
    def __init__(self):
        pass

    def to_dict(self):
        pass

    @classmethod
    def from_dict(cls, data):
        pass

    def get_meta_data(self) -> dict:
        pass

    def generate_description(self) -> dict | None:
        pass

    def set_description(self, function_name, sender):
        gpt_json = self.generate_description()
        if gpt_json:
            self.description = gpt_json.get("description")
            self.technical_questions = gpt_json.get("technical_questions")
            self.functional_questions = gpt_json.get("functional_questions")

            log_debug(f"[{function_name}] class prefix: {sender}")
            if self.description is None:
                log_debug(f"[{function_name}] description exists class prefix: {sender}")
                add_string_to_file("retry_methodName.txt", f"{sender}")
        else:
            log_debug(f"[ERROR] [{function_name}] empty gpt response: {sender}")
