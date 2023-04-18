import logging

from django.http import FileResponse
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from main.api.serializers.execution.input_create import ExecutionInputSerializer
from main.api.serializers.execution.input_update_failed import ExecutionInputSerializerForFailedUpdate
from main.api.serializers.execution.input_update_succeeded import ExecutionInputSerializerForSucceededUpdate
from main.api.serializers.schema.input import SchemaInputSerializer
from main.domain import Domain
from main.models import \
    Schema, \
    Execution, \
    ExecutionStatus
from .parsers import MultipartJsonParser as OwnMultipartJsonParser

logger = logging.getLogger(__name__)


def file_response(contents):
    response = FileResponse(open(contents.path, 'rb'))
    response['Content-Length'] = contents.file.size
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename={contents.name}'
    return response


class SchemaViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Schema.objects.all()
    serializer_class = SchemaInputSerializer
    parser_classes = [OwnMultipartJsonParser]
    ordering_fields = ['name', 'type', 'implementation', 'created_at']
    ordering = '-created_at'
    filterset_fields = ['name', 'type', 'implementation']

    @action(
        methods=['get'],
        detail=True,
        url_name='auxiliary_file'
    )
    def download_auxiliary_file(self, *args, **kwargs):
        return file_response(self.get_object().auxiliary_file)


class ExecutionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionInputSerializer
    parser_classes = [OwnMultipartJsonParser]
    ordering_fields = ['schema', 'created_at', 'updated_at']
    ordering = '-created_at'
    filterset_fields = ['schema']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if 'schema' not in serializer.initial_data:
            raise serializers.ValidationError('\"schema\" not provided')
        schema_name = serializer.initial_data['schema']
        schema = Schema.objects.filter(name=schema_name)
        if len(schema) < 1:
            raise serializers.ValidationError(f'\"{schema_name}\" does not exist')
        serializer.context['schema'] = schema[0]
        serializer.context['files'] = request.FILES
        serializer.is_valid(raise_exception=True)
        serializer.context['files'] = request.FILES
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Domain.end_schema_execution(instance)
        return super().destroy(request, *args, **kwargs)

    @action(
        methods=['get'],
        detail=True,
        url_name='external_data'
    )
    def download_external_data(self, *args, **kwargs):
        instance = self.get_object()
        if not instance.schema.requires_input_elements_external_data():
            raise serializers.ValidationError(f'\"{instance.schema.name}\" does not require external data')
        return file_response(instance.get_input_elements_external_data().contents)

    @action(
        methods=['get'],
        detail=True,
        url_name='version_user_vars'
    )
    def download_user_vars(self, *args, **kwargs):
        ai_engine_descriptor = self.request.query_params.get('descriptor')
        if ai_engine_descriptor is None:
            raise serializers.ValidationError('descriptor query parameter is missing')

        instance = self.get_object()
        specific_ai_engine = instance.get_ai_elements_specific_ai_engine(ai_engine_descriptor)
        if len(specific_ai_engine) < 1:
            raise serializers.ValidationError('does not exist an AI Engine in the schema with that descriptor')
        specific_ai_engine = specific_ai_engine[0]

        return file_response(specific_ai_engine.version_user_vars)

    @action(
        methods=['patch'],
        detail=True,
        url_name='update_to_running'
    )
    def update_to_running(self, *args, **kwargs):
        instance = self.get_object()
        state = instance.get_auxiliary_elements_state()
        serializer = self.get_serializer(data=instance)
        if state.status == ExecutionStatus.RUNNING:
            return Response(serializer.to_representation(instance), status=status.HTTP_200_OK)
        elif state.status != ExecutionStatus.PENDING:
            raise serializers.ValidationError(f'no update possible, the current status is \"{state.status}\"')
        else:
            # TODO add error handling
            instance = instance.update_status(ExecutionStatus.RUNNING)
            return Response(serializer.to_representation(instance), status=status.HTTP_200_OK)

    @action(
        methods=['patch'],
        detail=True,
        url_name='update_to_failed',
        serializer_class=ExecutionInputSerializerForFailedUpdate
    )
    def update_to_failed(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        error_message = serializer.data['message']

        instance = self.get_object()
        state = instance.get_auxiliary_elements_state()
        instance_serializer = ExecutionInputSerializer

        if state.status == ExecutionStatus.FAILED:
            return Response(instance_serializer(context={'request': request}).to_representation(instance), status=status.HTTP_200_OK)
        elif state.status == ExecutionStatus.SUCCEEDED:
            raise serializers.ValidationError(f'no update possible, the current status is \"{state.status}\"')
        else:
            # TODO add error handling
            instance = instance.update_status(ExecutionStatus.FAILED, error_message)
            return Response(instance_serializer(context={'request': request}).to_representation(instance), status=status.HTTP_200_OK)

    @action(
        methods=['patch'],
        detail=True,
        url_name='update_to_succeeded',
        serializer_class=ExecutionInputSerializerForSucceededUpdate
    )
    def update_to_succeeded(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.context['schema'] = instance.schema
        serializer.is_valid(raise_exception=True)

        state = instance.get_auxiliary_elements_state()
        instance_serializer = ExecutionInputSerializer

        if state.status == ExecutionStatus.SUCCEEDED:
            return Response(instance_serializer(context={'request': request}).to_representation(instance), status=status.HTTP_200_OK)
        elif state.status == ExecutionStatus.FAILED:
            raise serializers.ValidationError(f'no update possible, the current status is \"{state.status}\"')
        else:
            # TODO add error handling, rollback if error (atomic operation)
            if 'ai_model' in serializer.data:
                instance.update_output_elements_ai_model(serializer.data['ai_model']['ai_model'])
            if 'evaluation_metrics' in serializer.data:
                evaluation_metrics = [evaluation_metric['evaluation_metric'] for evaluation_metric in serializer.data['evaluation_metrics']]
                instance.update_output_elements_evaluation_metrics(evaluation_metrics)
            if 'generic_file' in serializer.data:
                instance.update_output_elements_generic_file(serializer.data['generic_file']['generic_file'])
            instance = instance.update_status(ExecutionStatus.SUCCEEDED)
            return Response(instance_serializer(context={'request': request}).to_representation(instance), status=status.HTTP_200_OK)
