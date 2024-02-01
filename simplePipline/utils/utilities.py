import os


def list_docx_files(directory):
    return [file for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file)) and file.endswith('.docx')]
