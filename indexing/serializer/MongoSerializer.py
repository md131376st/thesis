from rest_framework import serializers


class MethodRecordSerializer(serializers.Serializer):
    method_name = serializers.CharField(required=False)
    qualified_class_name = serializers.CharField(required=False)
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = '__all__'


class ClassRecordSerializer(serializers.Serializer):
    qualified_class_name = serializers.CharField()
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = '__all__'


class PackageRecordSerializer(serializers.Serializer):
    package_name = serializers.CharField()
    codebase_name = serializers.CharField()
    chromadb_collection_name = serializers.CharField(required=False)
    description = serializers.CharField()
    metadata = serializers.DictField()
    technical_questions = serializers.ListField(child=serializers.CharField())
    functional_questions = serializers.ListField(child=serializers.CharField())

    class Meta:
        fields = '__all__'
