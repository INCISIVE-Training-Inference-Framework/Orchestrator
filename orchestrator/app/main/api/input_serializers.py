from typing import Dict

from django.conf import settings
from rest_framework import serializers

from main.api.output_serializers import JobOutputSerializer
from main.domain.jobs_main import JobsDomain
from main.models import \
    Job, \
    JobStatus, \
    JobTrainingFromScratch, \
    JobTrainingFromPretrainedModel, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel


# TODO check config files are json files

class JobInputSerializer(serializers.ModelSerializer):
    # data_partners_patients = serializers.DictField(
    #    required=True,
    #    child=serializers.ListField(
    #        required=True,
    #        child=serializers.CharField()
    #    )
    # )
    data_partners_patients = serializers.DictField(required=True)  # TODO solve this super strange bug!!!

    class Meta:
        model = Job
        fields = '__all__'

    def validate_data_partners_patients(self, value: Dict[str, list]) -> Dict[str, list]:
        value = self.initial_data['data_partners_patients']  # TODO solve this super strange bug!!!

        if len(value) == 0:
            raise serializers.ValidationError(
                f'The data partners patients dictionary must not be empty'
            )

        for data_partner, data_partner_patients in value.items():
            if data_partner not in settings.VALID_DATA_PARTNERS:
                raise serializers.ValidationError(
                    f'All data partners must be valid. Possible values: {list(settings.VALID_DATA_PARTNERS)}'
                )
            if not data_partner_patients:
                raise serializers.ValidationError(f'The patient ids of data partner {data_partner} is empty')
            if len(data_partner_patients) != len(set(data_partner_patients)):
                raise serializers.ValidationError(f'The patient ids of data partner {data_partner} must be different')
        return value

    def to_representation(self, instance):
        instance = JobOutputSerializer(context=self.context).to_representation(instance)
        return instance


class JobInputTraining(JobInputSerializer):
    model_name = serializers.CharField(required=True, max_length=200)  # to make it required (typed models in db)
    model_type = serializers.CharField(required=True, max_length=50)  # idem
    model_description = serializers.CharField(required=True, max_length=500)  # idem

    class Meta:
        model = Job
        fields = [
            'ai_engine_config',
            'data_partners_patients',
            'data_path',
            'number_iterations',
            'model_name',
            'model_type',
            'model_description'
        ]

    def validate(self, data):
        data = super().validate(data)
        if len(data['data_partners_patients']) > 1 and 'number_iterations' not in data:
            raise serializers.ValidationError(
                'In the parallel training case the number of iterations must be specified'
            )
        return data


class JobInputTrainingFromScratchSerializer(JobInputTraining):

    class Meta:
        model = Job
        fields = ['ai_engine_id'] + JobInputTraining.Meta.fields

    def create(self, validated_data):
        validated_data['use_case'] = settings.TRAINING_FROM_SCRATCH
        job = JobTrainingFromScratch(**validated_data)
        return JobsDomain.start_job_execution(job)

    def update(self, instance, validated_data):
        raise NotImplementedError('Serializer not supports UPDATE')


class JobInputTrainingFromPretrainedModelSerializer(JobInputTraining):
    model_id = serializers.IntegerField(required=True)  # to make it required (typed models in db)

    class Meta:
        model = Job
        fields = ['model_id'] + JobInputTraining.Meta.fields

    def create(self, validated_data):
        validated_data['use_case'] = settings.TRAINING_FROM_PRETRAINED_MODEL
        job = JobTrainingFromPretrainedModel(**validated_data)
        return JobsDomain.start_job_execution(job)

    def update(self, instance, validated_data):
        raise NotImplementedError('Serializer not supports UPDATE')


class JobInputEvaluatingFromPretrainedModelSerializer(JobInputSerializer):
    model_id = serializers.IntegerField(required=True)  # to make it required (typed models in db)

    class Meta:
        model = Job
        fields = [
            'ai_engine_config',
            'data_partners_patients',
            'data_path',
            'model_id'
        ]

    def create(self, validated_data):
        validated_data['use_case'] = settings.EVALUATING_FROM_PRETRAINED_MODEL
        job = JobEvaluatingFromPretrainedModel(**validated_data)
        return JobsDomain.start_job_execution(job)

    def update(self, instance, validated_data):
        raise NotImplementedError('Serializer not supports UPDATE')


class JobInputInferencingFromPretrainedModelSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField(required=True)  # to make it required (typed models in db)

    class Meta:
        model = Job
        fields = [
            'ai_engine_config',
            'model_id',
            'input_data_files'
        ]

    def to_representation(self, instance):
        instance = JobOutputSerializer(context=self.context).to_representation(instance)
        return instance

    def create(self, validated_data):
        validated_data['use_case'] = settings.INFERENCING_FROM_PRETRAINED_MODEL
        job = JobInferencingFromPretrainedModel(**validated_data)
        return JobsDomain.start_job_execution(job)

    def update(self, instance, validated_data):
        raise NotImplementedError('Serializer not supports UPDATE')


class JobInputEndedExecutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['status', 'result']

    def validate_status(self, value: str) -> str:
        if value != JobStatus.SUCCEEDED and value != JobStatus.FAILED:
            raise serializers.ValidationError(f'The status should be {JobStatus.SUCCEEDED} or {JobStatus.FAILED}')
        return value

    def validate(self, data):
        data = super().validate(data)
        if data['status'] == JobStatus.SUCCEEDED and 'result' not in data:
            raise serializers.ValidationError(f'The result is missing')
        return data

    def to_representation(self, instance):
        instance = JobOutputSerializer(context=self.context).to_representation(instance)
        return instance

    def create(self, validated_data):
        raise NotImplementedError('Serializer not supports CREATE')

    def update(self, instance, validated_data):
        return JobsDomain.ended_job_execution(instance, validated_data['status'], validated_data['result'] if 'result' in validated_data else None)
