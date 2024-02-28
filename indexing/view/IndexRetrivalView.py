from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from filemanger.piplinesteps import TaskHandler
from indexing.serializer.RetrivalSerializer import RetrivalSerializer


class IndexRetrivalView(CreateAPIView):
    serializer_class = RetrivalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data["question"]
            classname = serializer.validated_data.get("className")
            embedding_type = serializer.validated_data["embedding_type"]
            n_results = serializer.validated_data["n_results"]
            result = TaskHandler.query_handler(question, classname, embedding_type, n_results)
            return Response(data={
                "answer": result
            }, status=status.HTTP_200_OK)



        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
