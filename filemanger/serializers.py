from rest_framework import serializers

from filemanger.models import Document
import os

def validate_file_type(uploaded_file):
    # List of allowed mime types or file extensions
    allowed_types = ['text/plain',
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'text/html',
                     'application/pdf']
    content_type = uploaded_file.content_type

    if content_type not in allowed_types:
        raise serializers.ValidationError('File type not supported. Allowed types are: txt, docx, html, pdf')


class DocumentSerializer(serializers.ModelSerializer):
    content = serializers.FileField()

    def validate_content(self, value):
        validate_file_type(value)
        ext = os.path.splitext(value.name)[1]
        print(ext)

        return value

    def create(self, validated_data):
        print(validated_data['content'])
        return Document.objects.create(**validated_data)

    class Meta:
        model = Document
        fields = ["content"]
