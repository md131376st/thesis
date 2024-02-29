from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from indexing.serializer.RetrivalSerializer import RetrivalSerializer
from indexing.taskHandler import TaskHandler


class IndexRetrivalView(CreateAPIView):
    serializer_class = RetrivalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data["question"]
            collection_name = serializer.validated_data.get("collection_name")
            n_results = serializer.validated_data["n_results"]
            query_type = serializer.validated_data.get("query_type")
            result = TaskHandler.query_handler(question, collection_name, n_results, query_type)
            if "error" in result:
                return Response(
                    data={"error": result},
                    status=status.HTTP_404_NOT_FOUND

                )
            else:
                return Response(data={
                    "answer": result
                }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
