import logging

from rest_framework.generics import ListAPIView

from fileService import settings
from filemanger.serializer.ChromaDbSerializer import CollectionSerializer
from simplePipline.vectorStorage.vectorStorage import ChromadbLammaIndexVectorStorage


class CollectionInfo(ListAPIView):
    serializer_class = CollectionSerializer

    def get_queryset(self):
        vectorStore = ChromadbLammaIndexVectorStorage(settings.CHROMA_DB, loglevel=logging.INFO)
        collections = vectorStore.db.list_collections()
        return [{"collection_name": collection.name} for collection in collections]
