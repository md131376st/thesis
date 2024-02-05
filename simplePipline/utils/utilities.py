import json
import os


def list_docx_files(directory):
    return [file for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file)) and file.endswith('.docx')]


def img_to_html_template(content):
    return '''<!DOCTYPE html>
    <html>
        <head>
             <meta charset="UTF-8">
            <title>Base64 Images and JSON Data</title>
           <style>
                .image-container {
                    display: flex;
                    align-items: flex-start;
                    margin-bottom: 20px;
                }
                .image-container img {
                    max-width: 300px; /* Adjust image size as needed */
                    margin-right: 20px;
                }
                .description {
                    background-color: #f7f7f7;
                    border: 1px solid #ccc;
                    padding: 10px;
                    max-width: 60%; /* Adjust width as needed */
                }
                pre {
                    white-space: pre-wrap;
                    overflow-x: auto;
                    margin: 0;
                }
            </style>
        </head>
        <body>
            <h1>Base64 Images and JSON Data Display</h1>
            <content>
        </body>
    </html>
            '''.replace("<content>", content)


def write_html_file(filename, content):
    with open(filename + ".html", "w") as file:
        file.write(content)


def save_NodeMetadata_to_json(filename, nodes):
    nodes_dict = [node.dict() for node in nodes]
    with open(f'{filename}.json', 'w') as f:
        json.dump(nodes_dict, f, indent=4)
