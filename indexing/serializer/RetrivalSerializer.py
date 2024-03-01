from rest_framework import serializers

from indexing.types import QueryTypes


class RetrivalSerializer(serializers.Serializer):
    question = serializers.CharField()
    collection_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    n_package_results = serializers.IntegerField( required=False)
    n_class_results = serializers.IntegerField( required=False)
    n_method_results = serializers.IntegerField(required=True)

    query_type = serializers.ChoiceField(
        choices=[(choice.value, choice.name) for choice in QueryTypes],
        default=QueryTypes.ALL.value,
        allow_null=True,
        allow_blank=True
    )

    def validate_n_package_results(self, value):
        if value < 1:
            raise serializers.ValidationError(
                " n_package_results should be a positive int")
        return value

    def validate_n_class_results(self, value):
        if value < 1:
            raise serializers.ValidationError(
                " n_class_results should be a positive int")
        return value

    def validate_n_method_results(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "n_method_results should be a positive int")
        return value

    def validate(self, data):
        if 'n_package_results' in data and (
                data['query_type'] == QueryTypes.CLASS.value or
                data['query_type'] == QueryTypes.PACKAGE):
            raise serializers.ValidationError(
                " n_package_results shouldn't be used with query_type:class, package")
        if 'n_class_results' in data and (
                data["query_type"] == QueryTypes.CLASS.value
        ):
            raise serializers.ValidationError(
                " n_class_results shouldn't be used with query_type:class")
        return data
