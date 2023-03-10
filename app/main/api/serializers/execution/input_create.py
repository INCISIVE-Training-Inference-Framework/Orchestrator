from typing import Dict

from django.conf import settings
from rest_framework import serializers

from main.api.serializers.execution.output import ExecutionOutputSerializer
from main.models import \
    Execution, \
    ExecutionState, \
    ExecutionInputPlatformData, \
    ExecutionInputExternalData, \
    ExecutionInputFederatedLearningConfiguration, \
    ExecutionInputAIEngine, \
    ExecutionInputAIModel, \
    ExecutionOutputAIModel
from main.exceptions import InternalError
from .maas_methods import retrieve_container_information
from main.domain import Domain


# TODO implement validate methods


def validate_data_partners_patients(value: Dict[str, list]) -> Dict[str, list]:
    found_error = False
    message_error = {}
    for data_partner, data_partner_patients in value.items():
        if data_partner not in settings.VALID_DATA_PARTNERS:
            found_error = True
            message_error[data_partner] = [f'\"{data_partner}\" is not a valid choice. Possible values: {list(settings.VALID_DATA_PARTNERS)}']
            continue
        if data_partner_patients is None:
            found_error = True
            message_error[data_partner] = [f'\"{data_partner_patients}\" is null.']
            continue
        if not isinstance(data_partner_patients, list):
            found_error = True
            message_error[data_partner] = [f'\"{data_partner_patients}\" is not a list.']
            continue
        if len(data_partner_patients) == 0:
            found_error = True
            message_error[data_partner] = [f'the list is empty.']
            continue
        if len(data_partner_patients) != len(set(data_partner_patients)):
            found_error = True
            message_error[data_partner] = [f'the list contains duplicates.']

        value[data_partner] = [str(item) for item in data_partner_patients]

    if found_error:
        raise serializers.ValidationError(message_error)
    else:
        return value


def validate_uploaded_file(context, file_key):
    files = context.get('files')
    files_keys = {file_key for file_key, file in files.items()}
    if file_key not in files_keys:
        raise serializers.ValidationError(f'the request should include a file with key {file_key}')
    serializers.FileField().to_internal_value(files[file_key])
    return files[file_key]


# Input classes

class ExecutionInputSerializerPlatformData(serializers.Serializer):
    data_partners_patients = serializers.DictField(required=False, allow_empty=False)

    def validate_data_partners_patients(self, value):
        # TODO validate only one if not federated, more than in the opposite case
        return validate_data_partners_patients(value)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        ExecutionInputPlatformData.objects.create(**{
            'data_partners_patients': validated_data['data_partners_patients'],
            'execution': execution_instance
        })


class ExecutionInputSerializerExternalData(serializers.Serializer):

    def _validate(self, context):
        contents = validate_uploaded_file(
            context,
            'external_data'
        )
        return {'contents': contents}

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        ExecutionInputExternalData.objects.create(**{
            'contents': validated_data['contents'],
            'execution': execution_instance
        })


class ExecutionInputSerializerFederatedLearningConfiguration(serializers.Serializer):
    number_iterations = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        ExecutionInputFederatedLearningConfiguration.objects.create(**{
            'number_iterations': validated_data['number_iterations'],
            'execution': execution_instance
        })


class ExecutionInputSerializerInputElements(serializers.Serializer):
    platform_data = ExecutionInputSerializerPlatformData(required=False)
    external_data = ExecutionInputSerializerExternalData(required=False)
    federated_learning_configuration = ExecutionInputSerializerFederatedLearningConfiguration(required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, validated_data):
        schema = self.context.get('schema')

        if schema.requires_input_elements_platform_data() and 'platform_data' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" requires platform data')
        if not schema.requires_input_elements_platform_data() and 'platform_data' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not require platform data')

        if schema.requires_input_elements_external_data():
            validated_data['external_data'] = ExecutionInputSerializerExternalData()._validate(self.context)
        if not schema.requires_input_elements_external_data():
            # TODO implement
            pass

        if schema.requires_input_elements_federated_learning_configuration() and 'federated_learning_configuration' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" requires a federated learning configuration')
        if not schema.requires_input_elements_federated_learning_configuration() and 'federated_learning_configuration' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not require a federated learning configuration')

        return validated_data

    def assign(self, execution_instance, validated_data):
        if 'platform_data' in validated_data:
            ExecutionInputSerializerPlatformData().assign(execution_instance, validated_data['platform_data'])
        if 'external_data' in validated_data:
            ExecutionInputSerializerExternalData().assign(execution_instance, validated_data['external_data'])
        if 'federated_learning_configuration' in validated_data:
            ExecutionInputSerializerFederatedLearningConfiguration().assign(execution_instance, validated_data['federated_learning_configuration'])


# AI logic classes

class ExecutionInputSerializerInputAIEngine(serializers.Serializer):
    descriptor = serializers.CharField(max_length=100)
    version = serializers.IntegerField()
    ai_model = serializers.IntegerField(required=False)

    def validate_descriptor(self, value):
        schema = self.context.get('schema')
        required_descriptors = {ai_engine.descriptor for ai_engine in schema.get_ai_items_ai_engines()}
        if value not in required_descriptors:
            raise serializers.ValidationError(f'\"{value}\" does not appear in schema')
        return value

    def validate_version(self, value):
        # TODO check that it exists at MaaS
        # TODO check that complies with the specified role and functionalities
        return value

    def validate_ai_model(self, value):
        # TODO check that it exists at MaaS
        # TODO check that it belongs to provided ai_engine
        return value

    def validate(self, validated_data):
        schema = self.context.get('schema')

        is_ai_model_required = schema.get_ai_elements_specific_ai_engine(validated_data['descriptor'])[0].requires_ai_model()

        if is_ai_model_required and 'ai_model' not in validated_data:
            raise serializers.ValidationError(f'AI Engine \"{validated_data["descriptor"]}\" requires an AI Model')
        if not is_ai_model_required and 'ai_model' in validated_data:
            raise serializers.ValidationError(f'AI Engine \"{validated_data["descriptor"]}\" does not require an AI Model')

        validated_data['version_user_vars'] = validate_uploaded_file(
            self.context,
            f'{validated_data["descriptor"]}_version_user_vars'
        )

        # retrieve container name and version from MaaS
        container_name = 'dummy'
        container_version = 'dummy'
        if settings.VALIDATE_WITH_MAAS:
            container_name, container_version = retrieve_container_information(validated_data['version'])

        validated_data['container_name'] = container_name
        validated_data['container_version'] = container_version

        return validated_data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        ai_engine_schema = ExecutionInputAIEngine.objects.create(**{
            'descriptor': validated_data['descriptor'],
            'version': validated_data['version'],
            'version_user_vars': validated_data['version_user_vars'],
            'container_name': validated_data['container_name'],
            'container_version': validated_data['container_version'],
            'execution': execution_instance
        })
        if 'ai_model' in validated_data:
            ExecutionInputAIModel.objects.create(**{'ai_model': validated_data['ai_model'], 'input_ai_engine': ai_engine_schema})


class ExecutionInputSerializerAIElements(serializers.Serializer):
    ai_engines = ExecutionInputSerializerInputAIEngine(many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, validated_data):
        schema = self.context.get('schema')

        required_ai_engines = {ai_engine.descriptor for ai_engine in schema.get_ai_items_ai_engines()}
        provided_ai_engines = {ai_engine['descriptor'] for ai_engine in validated_data['ai_engines']}

        if len(validated_data['ai_engines']) > len(provided_ai_engines):
            raise serializers.ValidationError(f'there are repeated AI Engines')

        if len(provided_ai_engines) > len(required_ai_engines):
            raise serializers.ValidationError(f'the number of provided AI Engines does not comply the schema {schema.name}')

        for required_ai_engine in required_ai_engines:
            if required_ai_engine not in provided_ai_engines:
                raise serializers.ValidationError(f'\"{required_ai_engine}\" ai engine has not been provided')

        return validated_data

    def assign(self, execution_instance, validated_data):
        serializer = ExecutionInputSerializerInputAIEngine()
        for ai_engine in validated_data['ai_engines']:
            serializer.assign(execution_instance, ai_engine)


# Output classes

class ExecutionInputSerializerOutputAIModel(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    merge_type = serializers.CharField(max_length=50, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        ExecutionOutputAIModel.objects.create(**{
            'name': validated_data['name'],
            'description': validated_data['description'],
            'merge_type': validated_data['merge_type'],
            'execution': execution_instance
        })


class ExecutionInputSerializerOutputElements(serializers.Serializer):
    ai_model = ExecutionInputSerializerOutputAIModel(required=False)

    def validate(self, validated_data):
        schema = self.context.get('schema')

        if schema.produces_output_elements_ai_model() and 'ai_model' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" requires an output element AI Model')
        if not schema.produces_output_elements_ai_model() and 'ai_model' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not require an output element AI Model')

        return validated_data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, execution_instance, validated_data):
        if 'ai_model' in validated_data:
            ExecutionInputSerializerOutputAIModel().assign(execution_instance, validated_data['ai_model'])


# Main class

class ExecutionInputSerializer(serializers.ModelSerializer):
    input_elements = ExecutionInputSerializerInputElements()
    ai_elements = ExecutionInputSerializerAIElements()
    output_elements = ExecutionInputSerializerOutputElements()

    class Meta:
        model = Execution
        fields = '__all__'

    def create(self, validated_data):
        input_elements = validated_data.pop('input_elements')
        ai_elements = validated_data.pop('ai_elements')
        output_elements = validated_data.pop('output_elements')
        execution_instance = Execution.objects.create(**validated_data)
        try:
            ExecutionState.objects.create(**{'execution': execution_instance})
            ExecutionInputSerializerInputElements().assign(execution_instance, input_elements)
            ExecutionInputSerializerAIElements().assign(execution_instance, ai_elements)
            ExecutionInputSerializerOutputElements().assign(execution_instance, output_elements)
            Domain.start_schema_execution(execution_instance)
            return execution_instance
        except Exception as e:
            execution_instance.delete()
            raise InternalError(
                f'Internal error while creating execution: {e}',
                'Internal error while creating execution'
            )

    def to_representation(self, instance):
        instance = ExecutionOutputSerializer(context=self.context).to_representation(instance)
        return instance
