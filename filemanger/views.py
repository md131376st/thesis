

from rest_framework import generics, status
from rest_framework.response import Response

from filemanger.models import Document
from filemanger.parser import LimitedFileSizeParser
from filemanger.serializers import DocumentSerializer


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

