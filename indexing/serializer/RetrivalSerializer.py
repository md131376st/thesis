from rest_framework import serializers

from indexing.types import QueryTypes


class RetrivalSerializer(serializers.Serializer):
    question = serializers.CharField()
    collection_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    n_results = serializers.IntegerField(default=1)
    query_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in QueryTypes],
        default=QueryTypes.CODEBASE,
        allow_null=True,
        allow_blank=True
    )
