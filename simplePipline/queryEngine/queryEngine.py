import logging

from llama_index import get_response_synthesizer
from llama_index.indices.vector_store import VectorIndexRetriever
from llama_index.postprocessor import SimilarityPostprocessor
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers.type import ResponseMode

from simplePipline.baseclass import Baseclass


class QueryEngine(Baseclass):
    def __init__(self, index, loglevel=logging.INFO):
        super().__init__("querying stage ", loglevel=loglevel)
        self.index = index

    def retrieve(self, question, **kwargs):
        pass


retrivalType = [
    "REFINE",
    "SIMPLE_SUMMARIZE"
]


class LamaIndexQueryEngine(QueryEngine):
    def __init__(self, index, top_k=5, mode=ResponseMode.COMPACT, similarity_cutoff=0.8, loglevel=logging.INFO):
        super().__init__(index, loglevel=loglevel)
        self.retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k,
        )
        response_synthesizer = get_response_synthesizer(response_mode=mode)
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)],
        )

    def retrieve(self, question, **kwargs):
        return self.query_engine.query(question)
