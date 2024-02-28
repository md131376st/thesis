from rest_framework import serializers

from filemanger.Types import IndexLevelTypes


class IndexCreateSerializer(serializers.Serializer):
    # location in system path
    path = serializers.CharField()
    indexType = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in IndexLevelTypes],
        default=IndexLevelTypes.CODEBASE,
        allow_null=True
    )
    # this is used for in case of code base the root package in other case it is the package path or class path
    collectionName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
