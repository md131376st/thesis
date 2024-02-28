from rest_framework import serializers

from simplePipline.embeder.embeder import EmbederType


class RetrivalSerializer(serializers.Serializer):
    question = serializers.CharField()
    className = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    embedding_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in EmbederType],
        default=EmbederType.DEFULT.value
    )
    n_results = serializers.IntegerField(default=1)
