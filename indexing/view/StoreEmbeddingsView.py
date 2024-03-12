from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from indexing.serializer.IndexCreateSerializer import IndexCreateSerializer
from indexing.storageManger.ClassStorageManger import ClassStorageManger
from indexing.types import IndexLevelTypes


class StoreEmbeddingsView(CreateAPIView):
    serializer_class = IndexCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            if serializer.validated_data["indexType"] == IndexLevelTypes.CLASS.value:
                return self.class_storage(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            elif serializer.validated_data["indexType"] == IndexLevelTypes.PACKAGE.value:
                return self.package_storage(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            else:
                return self.codebase_storage(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def codebase_storage(self, path, collection_name, codebase_name):
        taskid = "codebase"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def package_storage(self, path, collection_name, codebase_name):
        taskid = "package"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def class_storage(self, path, collection_name, codebase_name):
        task_id = "class"
        classStorageManger = ClassStorageManger()

        return Response({"taskId": task_id}, status=status.HTTP_202_ACCEPTED)

    pass
