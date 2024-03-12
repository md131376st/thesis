from rest_framework import serializers

from indexing.types import IndexLevelTypes


class StoreEmbeddingSerializer(serializers.Serializer):
    # location in system path
    indexType = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in IndexLevelTypes],
        default=IndexLevelTypes.CODEBASE,
        allow_null=True
    )
    collectionName = serializers.CharField(required=True)
    codebaseName = serializers.CharField(required=True)
