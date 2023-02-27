import json

from django.http import QueryDict
from rest_framework import parsers, serializers


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            result = super().parse(
                stream,
                media_type=media_type,
                parser_context=parser_context
            )
            qdict = QueryDict('', mutable=True)
            if 'data' in result.data:
                data = json.loads(result.data['data'])
                qdict.update(data)
        except Exception:
            raise serializers.ValidationError(f'Error while parsing the input json file')
        output = parsers.DataAndFiles(qdict, result.files)
        return output
