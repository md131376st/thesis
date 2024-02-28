from rest_framework import serializers


class RetrivalSerializer(serializers.Serializer):
    question = serializers.CharField()
    className = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    n_results = serializers.IntegerField(default=1)
