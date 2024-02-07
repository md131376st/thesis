import logging
import tempfile

from rest_framework import generics, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from simplePipline.embeder.embeder import LamaIndexEmbeder, EmbederType
from simplePipline.vectorStorage.vectorStorage import ChromadbLammaIndexVectorStorage
from .tasks import process_document, manage_embedding

from fileService import settings
from filemanger.models import Document
from filemanger.parser import LimitedFileSizeParser
from filemanger.piplinesteps import TaskHandler
from filemanger.serializers import DocumentSerializer, ProcessSerializer, PiplineSerializer, VectorStorageSerializer, \
    ChunkType, CollectionSerializer
from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.preproccess.featureExtraction.htmlFeatureExtraction import HTMLFeatureExtraction
from simplePipline.preproccess.imgTextConvertor import ImgTextConvertor
from simplePipline.utils.utilities import save_NodeMetadata_to_json


# Create your views here.

class Fileupload(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [LimitedFileSizeParser]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Pipline(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = PiplineSerializer
    parser_classes = [LimitedFileSizeParser]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['content']
            transfer = DOCXtoHTMLDataTransfer(loglevel=logging.DEBUG, transfer_type=TransferType.BYTEIO)
            html_content = transfer.transfer(content=file)
            preprocess = HTMLDataPreprocess(loglevel=logging.DEBUG, html_content=html_content)
            preprocess.preprocess()
            process_html = preprocess.get_content()
            feature_extractor = HTMLFeatureExtraction(process_html, loglevel=logging.DEBUG)
            feature_extractor.extract_node_data()
            data = feature_extractor.get_instance()
            for node in data:
                if len(node.image) != 0:
                    img_txt_con = ImgTextConvertor(node.all_text, node.image, loglevel=logging.DEBUG)
                    description = img_txt_con.convert()
                    node.img_placeholder_to_description(description)
                    break
            save_NodeMetadata_to_json(f'{file.name}', data)

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreProcess(CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = ProcessSerializer

    def create(self, request, *args, **kwargs):
        filename = request.data.get('file_name')

        if not filename:
            return Response({"error": "Filename is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(file_name=filename)
        except Document.DoesNotExist:
            return Response({"error": "Filename does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if document.state > Document.State.FileUpload:
            return Response({"message": "File all ready processed."}, status=status.HTTP_200_OK)
        if request.data.get("is_async"):
            process_document.delay(
                filename
            )
            return Response({"message": "File preprocessing task enqueued."}, status=status.HTTP_202_ACCEPTED)
        else:
            process_html = TaskHandler.proccess_data(document.content, is_async=False)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
                temp_file.write(process_html)

            document.state = Document.State.FilePreporcess
            document.save()

            # Return the temporary file as a downloadable response
            response = Response({"message": "File processed successfully."}, status=status.HTTP_200_OK)
            response['Content-Disposition'] = f'attachment; filename="{filename.split('.')[0]}.html"'
            response['Content-Type'] = 'text/html'
            response['X-Sendfile'] = temp_file.name
            return response


class FeatureExtract(CreateAPIView):
    pass


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
            embedding_type = serializer.validated_data['embedding_type']
            metadata = serializer.validated_data['metadata']
            warning = self.check_meta_data(chunk_type, metadata)
            embedding_type = self.check_embeding_type(embedding_type)

            if chunk_type == ChunkType.TEXT.value:
                return self.text_chunks(chunks, collection_name, embedding_type, is_async, metadata, warning)

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
        if is_async:
            ids = TaskHandler.ensure_id(chunks)
            manage_embedding.delay(collection_name, chunks, metadata, embedding_type, ids)
            return Response({"message": "manage embedding added to task enqueued ",
                             "ids": ids,
                             "warning": warning}, status=status.HTTP_202_ACCEPTED)
        else:
            ids = TaskHandler.store_embedding(collection_name, chunks, metadata, embedding_type)
            return Response({"message": "new index added",
                             "ids": ids,
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

    def check_meta_data(self, chunk_type, metadata):
        warning = ""
        if len(metadata) != len(chunk_type):
            warning = f"Meta data was ignored chunk list and meta data should be of equal length"
        return warning
