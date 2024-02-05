from llama_index import download_loader, SimpleDirectoryReader
from pathlib import Path
from simplePipline.Loader.loader import Loader


class DocumentLoader(Loader):
    def __init__(self):
        super().__init__()

    def load_data(self, directory):
        UnstructuredReader = download_loader('UnstructuredReader')
        dir_reader = SimpleDirectoryReader(directory, file_extractor={
            ".pdf": UnstructuredReader(),
            ".html": UnstructuredReader(),
            ".docx": UnstructuredReader(),
        })
        return dir_reader.load_data()


class JsonLoader(Loader):
    def __init__(self):
        super().__init__()

    def load_data(self, filename):
        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        return loader.load_data(Path(self.filename))
