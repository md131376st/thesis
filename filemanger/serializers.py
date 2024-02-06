import hashlib

from rest_framework import serializers

from filemanger.models import Document
import os

from simplePipline.utils.utilities import log_debug


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
    state_display = serializers.SerializerMethodField()

    def get_state_display(self, obj):
        return obj.get_state_display()

    def validate_content(self, value):
        validate_file_type(value)
        ext = os.path.splitext(value.name)[1]
        log_debug(str(ext))
        return value

    def create(self, validated_data):
        file = validated_data['content']
        file_name = file.name
        content_hash = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)
        document, created = Document.objects.update_or_create(
            file_name=file_name,
            defaults={
                'content': file,
                'content_hash': content_hash,
                'state': Document.State.FileUpload  # Reset state to default
            }
        )
        return document

    class Meta:
        model = Document
        fields = ["content", "state_display"]
