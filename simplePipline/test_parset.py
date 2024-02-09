import os

import requests
import json


def image_description_call(methodSigneture, sysprompt):
    api_key = os.environ["OPENAI_API_KEY"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"{sysprompt}"},
            {"role": "user", "content": f" the method is this:   {methodSigneture}"},
        ],
        "max_tokens": 1000,

    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()["choices"][0]['message']['content']


if __name__ == '__main__':
    classname = "com.intesasanpaolo.bear.sxdr0.metaconto.assembler.GetPdfListAssembler"
    response = requests.request("GET",
                                f"http://localhost:8080/parser/classInfo/{classname}",
                                headers={
                                    "sourceCodePath": "/Users/davarimona/Downloads/core-r-metaconto-v1"
                                })
    data = json.loads(response.content)
    methods = [element for element in data["methods"]]
    prompt = ("you are a java coding interpreter.\n"
              " you are provided a method declaration and you have to describe.\n"
              " the description should be synthetic"
              " include of params and the return values\n"
              " take your time to answer \n"
              "don't make any assumption ")
    responses = []
    for element in methods:
        hi = image_description_call(element, prompt)
        response = requests.request("POST",

                                    f"http://localhost:8001/embedding",
                                    headers={"Content-Type": "application/json"},
                                    data=json.dumps({
                                        "collection_name": f"{classname}",
                                        "is_async": True,
                                        "chunks": [
                                            {
                                                "text": hi,
                                            }
                                        ],
                                        "metadata": [{"methodName": element}],
                                        "chunks_type": "txt",
                                        "embedding_type": "text-embedding-3-small"
                                    }
                                    )
                                    )
        responses.append(response)
    pass
