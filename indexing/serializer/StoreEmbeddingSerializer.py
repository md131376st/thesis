from rest_framework import serializers

from indexing.types import StoreLevelTypes


class StoreEmbeddingSerializer(serializers.Serializer):
    # location in system path
    indexType = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in StoreLevelTypes],
        default=StoreLevelTypes.CODEBASE,
    )
    collectionName = serializers.CharField(required=False)
    codebaseName = serializers.CharField(required=True)
    refresh = serializers.BooleanField(required=False, default=False)
