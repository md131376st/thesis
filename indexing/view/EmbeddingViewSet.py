from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response

from indexing.models import PackageRecord, MethodRecord, ClassRecord
from indexing.ragHandler import RagHandler
from indexing.serializer.IndexCreateSerializer import IndexCreateSerializer
from indexing.types import TreeLevel
from indexing.utility import log_debug


class EmbeddingViewSet(viewsets.ModelViewSet):
    serializer_class = IndexCreateSerializer

    def get_queryset(self):
        type = self.request.query_params.get('type', None)
        if type:
            if type == TreeLevel.METHOD.value:
                return MethodRecord.objects()
            elif type == TreeLevel.CLASS.value:
                return ClassRecord.objects()
            elif type == TreeLevel.PACKAGE.value:
                return PackageRecord.objects()
            else:
                raise exceptions.ValidationError(
                    detail={"error": "The type value can only be: 'method', 'class', 'package'"},
                    code=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.ValidationError(
                detail={"error": "The type value should be in the query parameter"},
                code=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        queryset = self.get_queryset()
        return queryset.get(id=self.kwargs['id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.chromadb_collection_name:
            rag_response = RagHandler.rag_delete(
                collection_name=instance.chromadb_collection_name,
                id=instance.id
            )
            log_debug(f"[RagSystem return] {rag_response} ")
            if rag_response:
                instance.chromadb_collection_name = None
                instance.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        pass

    def create(self, request, *args, **kwargs):
        pass
