import logging

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins, serializers, parsers, renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from main.api.input_serializers import JobInputSerializer
from main.api.input_serializers import \
    JobInputTrainingFromScratchSerializer, \
    JobInputTrainingFromPretrainedModelSerializer, \
    JobInputEvaluatingFromPretrainedModelSerializer, \
    JobInputInferencingFromPretrainedModelSerializer, \
    JobInputEndedExecutionSerializer
from main.api.parsers import MultipartJsonParser
from main.models import \
    Job

logger = logging.getLogger(__name__)
SUPPORTED_JOB_USE_CASES = {
    settings.TRAINING_FROM_SCRATCH,
    settings.TRAINING_FROM_PRETRAINED_MODEL,
    settings.EVALUATING_FROM_PRETRAINED_MODEL,
    settings.INFERENCING_FROM_PRETRAINED_MODEL
}


class PassthroughRenderer(renderers.BaseRenderer):
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ZipFileRenderer(renderers.BaseRenderer):
    media_type = 'model'
    format = 'zip'

    def render(self, data, media_type=None, renderer_context=None):
        return data


def perform_action(
        serializer_class: serializers.ModelSerializer.__class__,
        request
):
    serializer = serializer_class(data=request.data)
    if serializer.is_valid():
        _object = serializer.create(serializer.validated_data)
        return Response(serializer_class(_object, context={'request': request}).data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Job.objects.all()
    serializer_class = JobInputSerializer
    ordering_fields = [
        'ai_engine_id',
        'model_id',
        'model_name',
        'model_type',
        'status',
        'use_case',
        'created_at',
        'updated_at'
    ]
    ordering = '-created_at'
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = [
        'ai_engine_id',
        'model_id',
        'model_name',
        'model_type',
        'status',
        'use_case'
    ]

    @action(
        methods=['post'],
        detail=False,
        url_name='training_from_scratch',
        serializer_class=JobInputTrainingFromScratchSerializer,
        parser_classes=[MultipartJsonParser, parsers.JSONParser]
    )
    def training_from_scratch(self, request, *args, **kwargs):
        return perform_action(self.serializer_class, request)

    @action(
        methods=['post'],
        detail=False,
        url_name='training_from_pretrained_model',
        serializer_class=JobInputTrainingFromPretrainedModelSerializer,
        parser_classes=[MultipartJsonParser, parsers.JSONParser]
    )
    def training_from_pretrained_model(self, request, *args, **kwargs):
        return perform_action(self.serializer_class, request)

    @action(
        methods=['post'],
        detail=False,
        url_name='evaluating_from_pretrained_model',
        serializer_class=JobInputEvaluatingFromPretrainedModelSerializer,
        parser_classes=[MultipartJsonParser, parsers.JSONParser]
    )
    def evaluating_from_pretrained_model(self, request, *args, **kwargs):
        return perform_action(self.serializer_class, request)

    @action(
        methods=['post'],
        detail=False,
        url_name='inferencing_from_pretrained_model',
        serializer_class=JobInputInferencingFromPretrainedModelSerializer,
        parser_classes=[MultipartJsonParser, parsers.JSONParser]
    )
    def inferencing_from_pretrained_model(self, request, *args, **kwargs):
        return perform_action(self.serializer_class, request)

    @action(
        methods=['get'],
        detail=True,
        renderer_classes=(PassthroughRenderer, ZipFileRenderer),
        serializer_class=Job,
        url_name='download_ai_engine_config'
    )
    def download_ai_engine_config(self, request, *args, **kwargs):
        ai_engine_config = self.get_object().ai_engine_config

        response = FileResponse(open(ai_engine_config.path, 'rb'))
        response['Content-Length'] = ai_engine_config.file.size
        response['Content-Disposition'] = 'attachment; filename=ai_engine_config.json'
        return response

    @action(
        methods=['get'],
        detail=True,
        renderer_classes=(PassthroughRenderer, ZipFileRenderer),
        serializer_class=JobInputInferencingFromPretrainedModelSerializer,
        url_name='download_input_data_files'
    )
    def download_input_data_files(self, request, *args, **kwargs):
        _object = self.get_object()
        if _object.use_case != settings.INFERENCING_FROM_PRETRAINED_MODEL:
            raise serializers.ValidationError(f'The input_data_files are only available in the {settings.INFERENCING_FROM_PRETRAINED_MODEL} use case')
        input_data_files = _object.input_data_files

        response = FileResponse(open(input_data_files.path, 'rb'))
        response['Content-Length'] = input_data_files.file.size
        response['Content-Disposition'] = 'attachment; filename=input_data_files.zip'
        return response

    @action(
        methods=['patch'],
        detail=True,
        url_name='ended_job_execution',
        serializer_class=JobInputEndedExecutionSerializer
    )
    def ended_job_execution(self, request, pk=None):
        job = get_object_or_404(Job.objects.all(), pk=pk)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            _object = serializer.update(job, serializer.validated_data)
            return Response(
                self.serializer_class(_object, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
