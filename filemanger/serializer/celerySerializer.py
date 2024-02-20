from rest_framework import serializers


class CelerySerializer(serializers.Serializer):
    id = serializers.UUIDField()
