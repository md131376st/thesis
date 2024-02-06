import logging

from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from fileService import settings
from filemanger.models import Document
from filemanger.parser import LimitedFileSizeParser
from filemanger.serializers import DocumentSerializer, ProcessSerializer, PiplineSerializer
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
        if request.data.get("useQuery"):
            pass
        else:
            transfer = DOCXtoHTMLDataTransfer(loglevel=logging.DEBUG, transfer_type=TransferType.FIle)
            html_content = transfer.transfer(f"../{settings.MEDIA_ROOT}/files/{filename}")
            preprocess = HTMLDataPreprocess(loglevel=logging.DEBUG, html_content=html_content)
            preprocess.preprocess()
            # preprocess.write_content("out.html")
            process_html = preprocess.get_content()

        # If the file exists, you might want to perform additional checks or actions here

        return Response({"message": "File exists."}, status=status.HTTP_200_OK)
