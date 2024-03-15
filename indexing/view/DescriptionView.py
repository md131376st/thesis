import json

from mongoengine import LookUpError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from indexing.models import MethodRecord, ClassRecord, PackageRecord
from indexing.serializer.IndexCreateSerializer import IndexCreateSerializer
from rest_framework import status, mixins, exceptions, viewsets
from rest_framework.response import Response
from indexing.collector.ClassCollector import ClassCollector
import indexing.collector.packageCollector as inpc
from indexing.collector.codeBaseCollector import CodeBaseCollector
from indexing.serializer.MongoSerializer import MethodRecordSerializer, PackageRecordSerializer, ClassRecordSerializer
from indexing.types import IndexLevelTypes, DescriptionType


class DescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = IndexCreateSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return IndexCreateSerializer
        if self.action in ['list', 'update']:
            type = self.kwargs['type']
            if type == DescriptionType.CODEBASE or type == DescriptionType.METHOD:
                return MethodRecordSerializer
            elif type == DescriptionType.PACKAGE:
                return PackageRecordSerializer
            else:
                return ClassRecordSerializer
        if self.action in ['destroy']:
            return IndexCreateSerializer
        return IndexCreateSerializer

    def get_queryset(self):
        type = self.kwargs['type']
        codebaseName = self.request.query_params.get('codebaseName', None)
        if not codebaseName and type is not DescriptionType.CODEBASE:
            raise exceptions.ValidationError(
                detail={"codebaseName": "This field is required."},
                code=status.HTTP_400_BAD_REQUEST)
        filter_fields = self.request.query_params.get('filter')
        try:
            filter_fields = json.loads(filter_fields)
        except json.JSONDecodeError:
            return exceptions.ValidationError(
                detail={'error': 'Invalid format for filter parameters'},
                code=status.HTTP_400_BAD_REQUEST)
        if isinstance(filter_fields, str):
            filter_fields = [filter_fields]
        records = []
        if type == DescriptionType.CODEBASE:
            for model in [MethodRecord, ClassRecord, PackageRecord]:
                if filter_fields:
                    filter_fields.append('id')
                    queryset = model.objects.only(*filter_fields)

                else:
                    queryset = model.objects.all()
                records.extend(queryset)
        elif type == DescriptionType.PACKAGE:
            if filter_fields:
                filter_fields.append('id')
                queryset = PackageRecord.objects(
                    codebase_name=codebaseName
                ).only(*filter_fields)
            else:
                queryset = PackageRecord.objects(
                    codebase_name=codebaseName
                )
            records.extend(queryset)
        elif type == DescriptionType.CLASS:
            if filter_fields:
                filter_fields.append('id')
                queryset = ClassRecord.objects(
                    codebase_name=codebaseName
                ).only(*filter_fields)
            else:
                queryset = ClassRecord.objects(
                    codebase_name=codebaseName
                )
            records.extend(queryset)
        else:
            if filter_fields:
                filter_fields.append('id')
                queryset = MethodRecord.objects(
                    codebase_name=codebaseName
                ).only(*filter_fields)
            else:
                queryset = MethodRecord.objects(
                    codebase_name=codebaseName
                )
            records.extend(queryset)
        return records

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookUpError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            if serializer.validated_data["indexType"] == IndexLevelTypes.CLASS.value:
                return self.class_index(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            elif serializer.validated_data["indexType"] == IndexLevelTypes.PACKAGE.value:
                return self.package_index(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
            else:
                return self.codebase_index(
                    serializer.validated_data["path"],
                    serializer.validated_data["collectionName"],
                    serializer.validated_data["codebaseName"])
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def codebase_index(self, path, collection_name, codebase_name):
        # taskid = "codebase"
        codebase_collector = CodeBaseCollector(path=path,
                                               codebase_name=codebase_name,
                                               packagePrefix=collection_name)
        taskid = codebase_collector.collect()
        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def package_index(self, path, collection_name, codebase_name):

        package_collector = inpc.PackageCollector(path, collection_name, codebase_name)
        taskid = package_collector.collect()

        return Response({"taskid": taskid}, status=status.HTTP_202_ACCEPTED)

    def class_index(self, path, collection_name, codebase_name):
        data_collector = ClassCollector(path, collection_name, codebase_name)
        task_id = data_collector.collect()

        return Response({"taskId": task_id}, status=status.HTTP_202_ACCEPTED)
