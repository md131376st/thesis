from rest_framework import serializers


class CollectionSerializer(serializers.Serializer):
    collection_name = serializers.CharField()
