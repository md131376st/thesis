from rest_framework import status
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.response import Response

from indexing.serializer.StoreEmbeddingSerializer import StoreEmbeddingSerializer
from indexing.storageManger.ClassStorageManger import ClassStorageManger
from indexing.types import IndexLevelTypes, StoreLevelTypes


class StoreEmbeddingsView(ListCreateAPIView):
    serializer_class = StoreEmbeddingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["indexType"] == StoreLevelTypes.OBJECT.value:
                return self.class_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"],
                    serializer.validated_data["refresh"]
                )

            elif serializer.validated_data["indexType"] == StoreLevelTypes.CLASS.value:
                return self.class_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"],
                    serializer.validated_data["refresh"]
                )
            elif serializer.validated_data["indexType"] == StoreLevelTypes.PACKAGE.value:
                return self.package_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"],
                    serializer.validated_data["refresh"],
                )
            else:
                return self.codebase_storage(
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"],
                    serializer.validated_data["refresh"]
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def codebase_storage(self, collection_name, codebase_name, refresh):
        taskid = "codebase"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def package_storage(self, collection_name, codebase_name, refresh):
        taskid = "package"

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def class_storage(self, collection_name, codebase_name, refresh):
        classStorageManger = ClassStorageManger(collection_name, codebase_name)
        data = classStorageManger.store(refresh=refresh)
        if "taskId" in data:
            return Response(
                data,
                status=status.HTTP_202_ACCEPTED)
        elif "message" in data:
            return Response(
                data,
                status=status.HTTP_200_OK)

        else:
            return Response(
                data,
                status=status.HTTP_404_NOT_FOUND)
