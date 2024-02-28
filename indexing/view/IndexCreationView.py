from rest_framework.generics import CreateAPIView

from filemanger.Types import IndexLevelTypes
from indexing.serializer.IndexCreateSerializer import IndexCreateSerializer
from rest_framework import status
from rest_framework.response import Response
from indexing.ClassCollector import ClassCollector
import indexing.packageCollector as inpc
from indexing.codeBaseCollector import CodeBaseCollector


class IndexCreationView(CreateAPIView):
    serializer_class = IndexCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["indexType"] == IndexLevelTypes.CODEBASE.value:
                return self.codebase_index(serializer.validated_data["path"],
                                           serializer.validated_data["collectionName"])
            elif serializer.validated_data["indexType"] == IndexLevelTypes.PACKAGE.value:
                return self.package_index(serializer.validated_data["path"],
                                          serializer.validated_data["collectionName"])
            elif serializer.validated_data["indexType"] == IndexLevelTypes.CLASS.value:
                return self.class_index(serializer.validated_data["path"],
                                        serializer.validated_data["collectionName"])
            else:
                return self.codebase_index(serializer.validated_data["path"],
                                           serializer.validated_data["collectionName"])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def codebase_index(self, path, collection_name):
        # taskid = "codebase"
        codebaseCollector = CodeBaseCollector(path, collection_name)
        taskid = codebaseCollector.collect()
        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def package_index(self, path, collection_name):

        PackageCollector = inpc.PackageCollector(path, collection_name)
        taskid = PackageCollector.collect()

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def class_index(self, path, collection_name):
        data_collector = ClassCollector(path, collection_name)
        task_id = data_collector.collect()

        return Response({"taskId": task_id}, status=status.HTTP_202_ACCEPTED)
