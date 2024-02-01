from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError


class LimitedFileSizeParser(MultiPartParser):
    MAX_UPLOAD_SIZE = 2621440  # 2.5 MB

    def parse(self, stream, media_type=None, parser_context=None):
        # Parse the file from the request
        result = super().parse(stream, media_type=media_type, parser_context=parser_context)

        # Check the file size
        for key in result.data.keys():
            if hasattr(result.data[key], 'size') and result.data[key].size > self.MAX_UPLOAD_SIZE:
                raise ValidationError(f'File size must be under {self.MAX_UPLOAD_SIZE / 1024 / 1024} MB')

        return result
