import asyncio
import base64
import os
from io import BytesIO
import requests
import json
from llama_index import VectorStoreIndex, load_index_from_storage
from llama_index.node_parser import SentenceSplitter, HTMLNodeParser
from llama_index.schema import Document
import enviorment
from simplePipline.utils.utilities import list_docx_files
from simplePipline.test.lamaIndexTestPipline import TestLamaIndexPipeline
from simplePipline.Loader.documentLoader import DocumentLoader
import nest_asyncio
from docx2python import docx2python
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from bs4 import BeautifulSoup

nest_asyncio.apply()

from PIL import Image
import matplotlib.pyplot as plt

from llama_index import (
    SimpleDirectoryReader,
)


def get_image():
    docx_content = docx2python('data/image_testdata/AFU - ISY_Motore di ricerca - v1.0.1.docx')
    docx_content.save_images('./data/image/1')


def create_simple_index():
    parser = SentenceSplitter(chunk_size=200, chunk_overlap=0)
    documents = DocumentLoader.load_documents("./data")
    nodes = parser.get_nodes_from_documents(documents)
    return VectorStoreIndex(nodes)


def test_simple_pipeline(filepath='./data'):
    query_engine = create_simple_index().as_query_engine()
    pipeline = TestLamaIndexPipeline(query_engine, filepath)
    asyncio.run(pipeline.test_hallucination())
    asyncio.run(pipeline.test_correction())


def store_simpleContext(index):
    index.storage_context.from_defaults(persist_dir="simple")


def reload_index(path):
    return load_index_from_storage(path)


def create_pipline():
    pass


def simple_iamge_pipline():
    image_documents = SimpleDirectoryReader("./data/image/1").load_data()
    openai_mm_llm = OpenAIMultiModal(
        model="gpt-4-vision-preview", api_key=enviorment.os.getenv('OPENAI_API_KEY'), max_new_tokens=1500
    )
    response_1 = openai_mm_llm.complete(
        prompt="Describe the images as an alternative text",
        image_documents=image_documents[:1],
    )
    print(response_1)


def simple_html_pipline_with_out_images():
    DEFAULT_TAGS = ["p", "h2", "ul",
                    "strong", "b", "ol",
                    "li", "b", "i",
                    "u", "section",
                    "img", "table", "tr", "td", "th"]
    preprocessor = HTMLPreprocessor("data/image_testdata/AFU - ISY_Motore di ricerca - v1.0.1.docx",
                                    "output.html")
    html_content = preprocessor.process_docx_to_html()
    documents = []
    documents.append(Document(text=html_content))
    node_parser = HTMLNodeParser(tags=DEFAULT_TAGS)
    nodes = node_parser.get_nodes_from_documents(documents, True)
    index = VectorStoreIndex(nodes)
    query_engine = index.as_query_engine()
    pipeline = TestLamaIndexPipeline(query_engine)
    asyncio.run(pipeline.test_hallucination())
    asyncio.run(pipeline.test_correction())


def image_description_call(images, prompt):
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
                        "text": f"{prompt}"
                    },

                ]
            }
        ],
        "max_tokens": 1000,

    }
    for image in images:
        payload["messages"][0]["content"].append({

            "type": "image_url",
            "image_url": {
                "url": image
            }

        })

    # print(payload)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    #
    # print(response.json()["choices"][0]['message']['content'])
    # print(response.json()["choices"][0].message.function_call)
    return response.json()["choices"][0]['message']['content']
    # return payload


def show_image(image, context):
    image_data = base64.b64decode(image.split(',')[1])
    image = Image.open(BytesIO(image_data))
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(image)
    ax.axis('off')
    plt.show()


def prompt_generator(caption, title):
    return (
        f' You are asked to description the components in the provided image .\n '
        f' the description is used for Information retrival tasks\n '
        f' the caption of image is  {caption}. \n '
        f' the title of the image is {title} \n '
        f'first generate a list of all the component with there description  of the '
        f'image starting from the top to button \n'
        f'. after that give the goal of the image \n'
        f' take your time and only give information you are sure \n'
        f'do not include a list of all the elements in a component just \n '
        f'give one example of each component  \n  '
        f'In case it is a mobile application don\'t include the '
        f' app nave bar, status bar or '
        f' any information about the state of the mobile phone \n'
        f'answer in italian then translate it in english  '
        f'separate the italian answer and the english answer by two lines \n'
    )


def prompt_generator_all_paragraph(alldata):
    return """You are asked generate the description of the components in the provided images.

I'll provide the surrounding text of the images.
The images context is:
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
""".replace("<ALL_DATA>", alldata)


def test_iamge_with_promt(image, context):
    prompt = prompt_generator_all_paragraph(context)
    description = image_description_call(image, prompt)
    show_image(image, description)


def generate_image_descriptions():
    listfiles = list_docx_files('./data/')
    for file in listfiles:
        filename = str(file).split('.docx')[0]
        preprocessor = HTMLPreprocessor("./data/" + file,
                                        f"./datapre/{filename}.html")
        html_content = preprocessor.process_docx_to_html()
        soup = BeautifulSoup(html_content, 'html.parser')
        preNodes = create_node_metadata_instances_associated(soup)
        instances_with_images = [instance for instance in preNodes if instance.image]
        result = []
        with open('utils/report_templates/texttemplate.html', 'r', encoding='utf-8') as htmlfile:
            html_content = htmlfile.read()
        for instance in instances_with_images:
            context = instance.all_text
            images = instance.image
            prompt = prompt_generator_all_paragraph(context)
            try:
                description = image_description_call(images, prompt)
                description = description.strip('```json').replace('```json', '').replace('```', '').strip()
                descriptionlist = json.loads(description)
            except json.JSONDecodeError as e:
                print(f"JSON loading error: {e}")
                continue  # Skip to the next iteration if JSON loading fails

            result.append(description)

            for index, image in enumerate(images):
                try:
                    html_content += f'''
                              <div class="image-container">
                                  <img src="{image}" alt="Image {index}">
                                  <div class="description">
                                      <pre>{{
                                          'index': '{descriptionlist[index]["index"]}',
                                          'description': '{descriptionlist[index]["description"]}'
                                      }}</pre>
                                  </div>
                              </div>
                              '''
                except IndexError:
                    print(f"Index {index} is out of range for the descriptions.")
                    html_content += f'''
                              <div class="image-container">
                                  <img src="{image}" alt="Image {index}">
                                  <div class="description">
                                      <pre>{{'index': 'N/A', 'description': 'No description available'}}</pre>
                                  </div>
                              </div>
                              '''

        with open("./imgdescription/"+filename + ".json", 'w') as file1:
            json.dump(result, file1)
        html_content += """
            </body>
            </html>
            """
        with open("./img/"+filename + ".html", "w") as file2:
            file2.write(html_content)


if __name__ == '__main__':
    # generate_image_descriptions()
    listfiles = list_docx_files('./data/')
    for file in listfiles:
        filename = str(file).split('.docx')[0]
        preprocessor = HTMLPreprocessor("./data/" + file,
                                        "output.html")
        html_content = preprocessor.process_docx_to_html()
        soup = BeautifulSoup(html_content, 'html.parser')
        # preNodes = create_node_metadata_instances_associated(soup)
        with open("./img/"+filename + '.html', 'r', encoding='utf-8') as htmlfile:
            htmldata = htmlfile.read()
            soup1 = BeautifulSoup(htmldata, 'html.parser')
        text, html, soup = margeDescriptionWithText(soup, soup1)
        title_sepration = ""
        titles = soup.find_all("h2")
        for title in titles:
            if title.text != "":
                text = text.replace(title.text, "\n" + title.text)

        with open("./data1/" + filename + ".txt", 'w', encoding='utf-8') as file:
            file.write(text)
        with open("./data2/" + filename + ".html", 'w', encoding='utf-8') as file:
            file.write(html)
    # test_simple_pipeline('./data')
    parser = SentenceSplitter(chunk_size=150, chunk_overlap=50)
    documents = DocumentLoader.load_documents("./data1")
    nodes = parser.get_nodes_from_documents(documents)
    query_engine = VectorStoreIndex(nodes).as_query_engine()
    pipeline = TestLamaIndexPipeline(query_engine, "./data1")
    asyncio.run(pipeline.test_hallucination())
    # asyncio.run(pipeline.test_correction())

    pass
