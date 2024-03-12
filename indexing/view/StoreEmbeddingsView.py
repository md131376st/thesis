from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from indexing.serializer.StoreEmbeddingSerializer import StoreEmbeddingSerializer
from indexing.storageManger.ClassStorageManger import ClassStorageManger
from indexing.types import IndexLevelTypes


class StoreEmbeddingsView(CreateAPIView):
    serializer_class = StoreEmbeddingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            if serializer.validated_data["indexType"] == IndexLevelTypes.CLASS.value:
                return self.class_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            elif serializer.validated_data["indexType"] == IndexLevelTypes.PACKAGE.value:
                return self.package_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            else:
                return self.codebase_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def codebase_storage(self, collection_name, codebase_name):
        taskid = "codebase"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def package_storage(self, collection_name, codebase_name):
        taskid = "package"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def class_storage(self, collection_name, codebase_name):
        task_id = "class"
        classStorageManger = ClassStorageManger(collection_name, codebase_name)
        method_object = classStorageManger.fetch_data_if_exists()
        if method_object:
            new_method_objects = classStorageManger.check_embedding_exists(method_object)
            if new_method_objects:

                return Response(
                    {"taskId": task_id},
                    status=status.HTTP_202_ACCEPTED)
            else:
                return Response(
                    {
                        "message": "All the requested data is successfully stored in the Chroma DB."
                    },
                    status=status.HTTP_200_OK)

        else:
            return Response(
                {
                    "error": "The combination of (collectionName, codebaseName) does not exist."
                },
                status=status.HTTP_404_NOT_FOUND)
