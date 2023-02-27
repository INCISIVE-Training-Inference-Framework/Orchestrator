from rest_framework import serializers

from main.api.input_serializers import RunningExecutionSerializer
from main.domain.jobs_main import JobsDomain


class RunningExecutionDeserializer(serializers.Serializer):

    ai_engine = serializers.IntegerField()
    model = serializers.IntegerField()
    data = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        return JobsDomain.create_running_execution(**validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError('Not implemented')

    def to_representation(self, instance):
        return RunningExecutionSerializer().to_representation(instance)  # TODO refactor to not instantiated each time
