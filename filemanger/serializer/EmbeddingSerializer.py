from rest_framework import serializers

from filemanger.Types import ChunkType
from simplePipline.embeder.embeder import EmbederType


class VectorStorageSerializer(serializers.Serializer):
    collection_name = serializers.CharField()
    collection_metadata = serializers.DictField(
        child=serializers.JSONField()
    )
    is_async = serializers.BooleanField()
    chunks = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(allow_blank=True)
        )
    )
    metadata = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField()
        )
    )
    chunks_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in ChunkType]
    )
    embedding_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in EmbederType],
        default=EmbederType.DEFULT.value
    )
