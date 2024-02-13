import logging

import tiktoken
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from simplePipline.batchHandler.batchHandler import EmbeddingBatchHandler
from simplePipline.embeder.embeder import LamaIndexEmbeder, EmbederType
from simplePipline.utils.utilities import log_debug
from simplePipline.vectorStorage.vectorStorage import ChromadbLammaIndexVectorStorage
from .tasks import manage_embedding

from fileService import settings
from filemanger.piplinesteps import TaskHandler
from filemanger.serializers import VectorStorageSerializer, \
    ChunkType, CollectionSerializer


# Create your views here.


class CollectionInfo(ListAPIView):
    serializer_class = CollectionSerializer

    def get_queryset(self):
        vectorStore = ChromadbLammaIndexVectorStorage(settings.CHROMA_DB, loglevel=logging.INFO)
        collections = vectorStore.db.list_collections()
        return [{"collection_name": collection.name} for collection in collections]


class EmbeddingView(CreateAPIView):
    serializer_class = VectorStorageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            collection_name = serializer.validated_data['collection_name']
            if not collection_name and collection_name.strip():
                return Response(
                    {"message": f"please provide a collection name"},
                    status=status.HTTP_400_BAD_REQUEST)
            chunk_type = serializer.validated_data['chunks_type']
            chunks = serializer.validated_data['chunks']
            is_async = serializer.validated_data['is_async']
            metadata = serializer.validated_data['metadata']
            log_debug(f"metadataview={metadata}")
            log_debug(f"len metadataview={len(metadata)}")

            warning = self.check_meta_data(chunks, metadata)

            embedding_type = self.check_embeding_type(serializer.validated_data['embedding_type'])

            if chunk_type == ChunkType.TEXT.value:
                return self.text_chunks(chunks, collection_name, embedding_type,
                                        is_async, metadata, warning)

            elif chunk_type == ChunkType.CODE.value:
                return Response({"message": "new index added"}, status=status.HTTP_200_OK)

            elif chunk_type == ChunkType.LAMA_INDEX.value:
                return self.lams_index_chunks(chunks, collection_name, is_async)
            else:
                return Response(
                    {"message": f"invalid Chunk type allowed values are:"
                                f" {[member.value for member in ChunkType]}"},
                    status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def text_chunks(self, chunks, collection_name, embedding_type, is_async, metadata, warning):
        activeMetaData = False if warning else True
        chunks = TaskHandler.ensure_id(chunks)
        ids = [chunk['id'] for chunk in chunks]
        batch = EmbeddingBatchHandler()
        batch.createBatchHandler(
            info={
                "chunks": chunks,
                "metadata": metadata,
            },
            active_meta_data=activeMetaData
        )

        batch_list = batch.get_batch()
        log_debug(f"batch_text: {batch_list}")
        if is_async:
            taskId = manage_embedding.delay(collection_name, batch_list, embedding_type).id
            return Response({"message": "manage embedding added to task enqueued ",
                             "embedding_id_list": ids,
                             "taskId": taskId,
                             "warning": warning}, status=status.HTTP_202_ACCEPTED)
        else:
            for chunks in batch_list:
                TaskHandler.store_embedding(collection_name, chunks, metadata, embedding_type,ids)
            return Response({"message": "new index added",
                             "embedding_id_list": ids,
                             "warning": warning}, status=status.HTTP_200_OK)

    def lams_index_chunks(self, chunks, collection_name, is_async):
        vectorStore = ChromadbLammaIndexVectorStorage(settings.CHROMA_DB, loglevel=logging.INFO)
        embedding = LamaIndexEmbeder(chunks).get_service_context()
        vectorStore.store(nodes=chunks,
                          service_context=embedding,
                          collection_name=collection_name,
                          is_async=is_async)
        return Response({"message": "new index added"}, status=status.HTTP_200_OK)

    def check_embeding_type(self, embedding_type):
        if not embedding_type and embedding_type.strip():
            embedding_type = EmbederType.DEFULT.value
        return embedding_type

    def check_meta_data(self, chunks, metadata):
        warning = ""
        if len(metadata) != len(chunks):
            warning = f"Meta data was ignored chunk list and meta data should be of equal length"
        return warning
