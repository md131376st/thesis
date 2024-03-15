from rest_framework import serializers

from indexing.models import MethodRecord


class MethodRecordSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    method_name = serializers.CharField(required=False)
    qualified_class_name = serializers.CharField(required=False)
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        for field in ['method_name',
                      'qualified_class_name',
                      'package_name',
                      'codebase_name',
                      'chromadb_collection_name',
                      'description',
                      'metadata',
                      'technical_questions',
                      'functional_questions']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance

    class Meta:
        fields = '__all__'


class ClassRecordSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    qualified_class_name = serializers.CharField()
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        for field in [
            'qualified_class_name',
            'package_name',
            'codebase_name',
            'chromadb_collection_name',
            'description',
            'metadata',
            'technical_questions',
            'functional_questions'
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance

    class Meta:
        fields = '__all__'


class PackageRecordSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        # Update fields if they are in validated data
        for field in [
            'package_name',
            'codebase_name',
            'chromadb_collection_name',
            'description',
            'metadata',
            'technical_questions',
            'functional_questions'
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance

    class Meta:
        fields = '__all__'
