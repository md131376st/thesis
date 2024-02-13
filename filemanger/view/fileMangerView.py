import logging
import os
import tempfile

from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from fileService import settings
from filemanger.models import Document
from filemanger.parser import LimitedFileSizeParser
from filemanger.piplinesteps import TaskHandler
from filemanger.serializers import DocumentSerializer, PiplineSerializer, ProcessSerializer, FeatureExtractionSerializer
from filemanger.tasks import process_document, feature_extract_document
from simplePipline.preproccess.dataTransfer import DOCXtoHTMLDataTransfer, TransferType
from simplePipline.preproccess.dataprocess.htmlDataPreprocess import HTMLDataPreprocess
from simplePipline.preproccess.featureExtraction.htmlFeatureExtraction import HTMLFeatureExtraction
from simplePipline.preproccess.imgTextConvertor import ImgTextConvertor
from simplePipline.utils.utilities import save_NodeMetadata_to_json, Get_json_filename, Get_html_filename


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
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            filename = serializer.validated_data['file_name']
            try:
                document = Document.objects.get(file_name=filename)
            except Document.DoesNotExist:
                return Response({"error": "Filename does not exist."}
                                , status=status.HTTP_404_NOT_FOUND)
            if document.state > Document.State.FileUpload:
                return Response({"message": "File all ready processed."}
                                , status=status.HTTP_200_OK)
            if request.data.get("is_async"):
                taskId = process_document.delay(filename).id
                return Response(
                    {
                        "message": "File preprocessing task enqueued.",
                        "taskId": taskId
                    }
                    , status=status.HTTP_202_ACCEPTED)
            else:
                process_html = TaskHandler.proccess_data(document.content, is_async=False)
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
                    temp_file.write(process_html)

                document.state = Document.State.FilePreporcess
                document.save()
                response = Response({"message": "File processed successfully."}, status=status.HTTP_200_OK)
                response['Content-Disposition'] = f'attachment; filename="{filename.split('.')[0]}.html"'
                response['Content-Type'] = 'text/html'
                response['X-Sendfile'] = temp_file.name
                return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeatureExtract(CreateAPIView):
    serializer_class = FeatureExtractionSerializer

    def check_document_state(self, document, html_file_name):
        if document.state == Document.State.FilePreporcess:
            return True
        elif document.state == Document.State.FeatureExtraction:
            return True
        elif (document.state > Document.State.FeatureExtraction
              and os.path.exists(
                    f"{settings.FEATURE_EXTRACT}/{html_file_name}")):
            return True
        else:
            return False

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            filename = serializer.validated_data['filename']
            store = serializer.validated_data['store']
            include_images = serializer.validated_data['include_images']
            try:
                document = Document.objects.get(file_name=filename)
            except Document.DoesNotExist:
                return Response(
                    {"error": "Filename does not exist."},
                    status=status.HTTP_404_NOT_FOUND)
            json_file_name = Get_json_filename(str(document.content))

            if self.check_document_state(document, json_file_name):
                if serializer.validated_data["is_async"]:
                    feature_extract_document.delay(filename, store, include_images)
                else:
                    html_file_name = Get_html_filename(str(document.content))
                    TaskHandler.feature_extraction(html_file_name, json_file_name, store, include_images)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            elif document.state < Document.State.FilePreporcess:
                return Response(
                    {"error": "File needs to be preprocessed before extracting features"},
                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(
                    {"error": "File should be preprocessed or file extracting doesn't exist"},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
