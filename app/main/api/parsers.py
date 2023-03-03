import json

from rest_framework import parsers, serializers


class DictWithEncoding(dict):

    def __init__(self, *args):
        super().__init__(*args)
        self.encoding = 'utf-8'


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            result = super().parse(
                stream,
                media_type=media_type,
                parser_context=parser_context
            )
            data = {}
            if 'data' in result.data:
                data = json.loads(result.data['data'])
                data = DictWithEncoding(data)
            files = {key: value[0] for key, value in dict(result.files).items()}
        except Exception as e:
            raise serializers.ValidationError(f'Error while parsing the input json file. {e}')
        return parsers.DataAndFiles(data, files)
