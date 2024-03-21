from rest_framework import serializers


class EmbeddingStoreInstanceSerializer(serializers.Serializer):
    collectionName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    codebaseName = serializers.CharField(required=True)
