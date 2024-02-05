import logging
from enum import Enum

from llama_index.node_parser import SentenceSplitter, JSONNodeParser, HierarchicalNodeParser
from llama_index.node_parser import get_leaf_nodes, get_root_nodes

from simplePipline.Loader.documentLoader import JsonLoader
from simplePipline.baseclass import Baseclass
from llama_index import Document


class Transformer(Baseclass):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__("Generate chunks of data", loglevel=loglevel)
        self.context = context
        self.chunks = []

    def transform(self, **kwargs):
        pass

    def get_chunk(self):
        return self.chunks


class RaptorTransformer(Transformer):
    def __init__(self, context, loglevel=logging.INFO):
        super().__init__(context, loglevel=loglevel)

    def transform(self, chunk_size=100, **kwargs):
        for node in self.context:
            self.generate_chunks(node.all_text)
            break
        pass

    def generate_chunks(self, text):
        CHUNKING_REGEX = "[^,.;。？！]+[,.;。？！]?"
        pass


class TransformType(Enum):
    SentenceSplitter = 0
    HierarchicalNodeParser = 1
    JSONNodeParser = 2
    # SemanticSplitterNodeParser = 3


class LlamaIndexTransformer(Transformer):
    def __init__(self, context, loglevel=logging.INFO, transformType=TransformType.SentenceSplitter):
        super().__init__(context, loglevel=loglevel)
        self.transformType = transformType

    def transform(self, chunk_size=None, chunk_overlap=None,
                  filename=None,
                  **kwargs):
        if self.transformType == TransformType.SentenceSplitter:
            parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            documents = [Document(text=node.all_text) for node in self.context]
            self.chunks += parser.get_nodes_from_documents(documents)

        if self.transformType == TransformType.JSONNodeParser:
            document = JsonLoader().load_data(filename)
            parser = JSONNodeParser()
            self.chunks += parser.get_nodes_from_documents(document)

        if self.transformType == TransformType.HierarchicalNodeParser:
            documents = [Document(text=node.all_text) for node in self.context]
            node_parser = HierarchicalNodeParser.from_defaults()
            self.chunks += node_parser.get_nodes_from_documents(documents)
            leaf_nodes = get_leaf_nodes(self.chunks)
            root_nodes = get_root_nodes(self.chunks)
            return leaf_nodes, root_nodes
