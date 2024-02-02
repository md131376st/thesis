import json
import os
import requests
from simplePipline.preproccess.baseclass import Baseclass
import logging


class Convertor(Baseclass):
    def __init__(self, loglevel=logging.INFO):
        super().__init__("Converting Image to Text", loglevel=loglevel)

    def convert(self):
        pass


class ImgTextConvertor(Convertor):
    def __init__(self, image_context, imagelist, loglevel=logging.INFO):
        super().__init__( loglevel=loglevel)
        self.image_context = image_context
        self.images = imagelist
        self.logger.info("generate prompt")
        self._image_to_text_prompt()

    def _image_to_text_prompt(self):
        self.prompt = """
        You are asked generate the description of the components in the provided images.
        I'll provide the surrounding text of the images.
        The mages context is:
        <ALL_DATA>
        Image placeholders are: $image_n$ when n indicates the image number. Usually the image placeholder is followed by the image caption.
        STEPS TO FOLLOW:
        1. Generate a list of all the component with the description of the image starting from the top to the bottom.
        2. In the description include useful information about the image in the context
        3. Do not include a list of all the elements in a component just give one example of each component  
        RULES:
        - In case it is a mobile application don\'t include the app nave bar, status bar or any information about the state of the mobile phone
        - take your time and only give information you are sure
        - answer in italian language
        OUTPUT:
        Answer in JSON FORMAT. Return a list of elements where each element is a dictionary with the following keys:
        - the key "index" with the value of the placeholder of the image in the context
        - the key "description" with the description of the image
        [
        {
           "index": $image_n$,
           "description": $description$
           },
           ...
           ]
           """.replace("<ALL_DATA>", self.image_context)

    def image_description_call(self):

        api_key = os.environ["OPENAI_API_KEY"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{self.prompt}"
                        },

                    ]
                }
            ],
            "max_tokens": 1000,

        }
        for image in self.images:
            payload["messages"][0]["content"].append({

                "type": "image_url",
                "image_url": {
                    "url": image
                }

            })
        self.logger.info("call to gpt-4-vision")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        self.logger.debug(response.json())
        return response.json()["choices"][0]['message']['content']

    def convert(self):
        try:
            description = self.image_description_call()
            self.logger.info("fix gpt json format")
            description = description.strip('```json').replace('```json', '').replace('```', '').strip()
            return json.loads(description)
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON loading error: {e}")
            return []
        pass
